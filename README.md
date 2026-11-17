# Measure It — camera calibration, dataset, segmentation and paper measurement

This is a partial submission. Items 1 to 4 of the assessment are NOT all complete. See `docs/Definition_of_Done.md` for the verified status of each item, and `docs/Objectives.md` for the measurable targets and their results.

## Status

| Item | Status |
|---|---|
| 1. Calibrated camera | Calibration done (21 images, RMS 0.092 px). Undistortion NOT verified. |
| 2. Dataset of 70+, masks, fixed split | 74 photos, auto-generated masks, split committed. Not undistorted. Not hand-labelled. |
| 3. Segmentation model | Small U-Net trained on CPU. Metrics on 7 test images against auto masks. mAP NOT computed. |
| 4. One command, image to mm | `inference/measure.py` runs with classical segmentation. Undistortion NOT verified. U-Net not yet used. |
| 5. Calliper accuracy | Not done. |
| 6. Undistortion proof | Not done. |

## Hardware and software

- CPU: Intel Core i7-8650U @ 1.90 GHz
- RAM: 16 GB
- GPU: Intel UHD Graphics 620 (no CUDA). Training runs on CPU.
- OS: Windows 11 Pro, 64-bit
- Camera: phone, model to be recorded. Calibration photos are 960 × 1280 (WhatsApp copies, not original files).
- Library versions: see `requirements.txt`

## Setup (Windows PowerShell)

Run from the repository root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

PyTorch is needed for training only. Install the CPU build from https://pytorch.org if the default install fails.

## Run calibration

Board: 9 × 7 inner corners (10 × 8 squares). Square size measured with a ruler as 1.5 cm.

```powershell
python calibration\calibrate.py --images calibration\images --cols 9 --rows 7 --square-mm 15
```

Outputs: `calibration\camera_params.npz` and `calibration\calibration_report.json`. The square size affects only translation vectors, not the camera matrix or distortion coefficients.

## Run image to mm (partial)

```powershell
python inference\measure.py --image path\to\photo.jpg --ref-w-mm 129 --ref-h-mm 144
```

The reference values are the cardboard piece measured with a ruler, not a calliper. The script prints `RESULT: ok`, paper width and height in mm, the scale, a shape-score confidence (not a probability), and writes an overlay image. It prints `RESULT: object not found` or `RESULT: reference not found` when it cannot find the object or the reference. It also refuses photos whose orientation does not match the calibration (`RESULT: calibration mismatch`).

## Train the segmentation model

```powershell
python models\train_unet.py
```

Reads `dataset/split_v3.csv`, trains for 40 epochs with seed 42, and writes `models/unet_small.pt` and `models/training_report.json`.

## Dataset summary

- Object: one white paper sheet, about 290 × 205 mm (ruler estimate, not calliper).
- Reference object: flat cardboard piece, 129 × 144 mm (ruler measurement).
- Images: 74 unique photos (dataset/images), masks in dataset/masks (auto-generated, not hand-checked).
- Split: `dataset/split_v3.csv`, 52 train / 15 validation / 7 test, seed 42. Committed before the final retrain.
- Labelling tool: none (masks come from an automatic contour method). CVAT or Label Studio is not used yet.
- Known weakness: brown-carpet backgrounds give lower contrast, and the reference is not found in some photos.

## Model weights

- File: `models/unet_small.pt`
- SHA-256: `bc2a5494cae43f73298b12ab2817777ebc0a50231bd8ea39a84922d41b2bf989`

## Limitations

- Undistortion is not verified, so mm values are not validated.
- Masks are not hand-labelled. The U-Net learned to match the automatic masks.
- mAP is not computed. Only mask IoU, pixel precision and pixel recall are reported.
- The calibration board is shown on a laptop screen, and its square size is a ruler measurement.

## Pull request

Not created. `main` does not exist yet. A pull request will be opened only after the author approves.
