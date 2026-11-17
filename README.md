# Measure It — camera calibration and paper measurement (partial)

This repository is an honest, partial submission for the Measure It assessment. Read `docs/Definition_of_Done.md` for what is finished and what is not.

## Status

| Part | Status |
|---|---|
| Camera calibration | Done. RMS reprojection error 0.092 px on 20 images |
| Dataset | 10 photos captured; target 70 not met; no masks yet |
| Model | Not started |
| Image-to-mm command | Partial: `inference/measure.py` runs; mm values not valid yet |
| Accuracy table | Not started |

## Hardware and software

- CPU: Intel Core i7-8650U @ 1.90 GHz
- RAM: 16 GB
- GPU: Intel UHD Graphics 620 (no CUDA)
- OS: Windows 11 Pro, 64-bit
- Camera: phone, model to be recorded. Calibration photos are 960 × 1280 (WhatsApp copies; originals not yet used).
- Python 3 and OpenCV (`opencv-python`). Exact versions to be pinned in `requirements.txt`.

## Setup (Windows PowerShell)

Run from the repository root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install opencv-python numpy
```

## Run calibration

Photos must be in a folder, for example `calibration\images`. The board is 8 × 10 squares, so the inner corners are 7 × 9.

```powershell
python calibration\calibrate.py --images calibration\images --cols 7 --rows 9 --square-mm 20.0
```

Outputs: `calibration\camera_params.npz` and `calibration\calibration_report.json`. The `--square-mm` value should be the calliper-measured size once it is available. It affects only translation vectors, not the camera matrix or distortion.

## Run image to mm (partial)

```powershell
python inference\measure.py --image path\to\photo.jpg --ref-w-mm 85.6 --ref-h-mm 54.0
```

Replace the reference size with the calliper-measured size of the cardboard piece. The values above are a placeholder. The script prints paper width and height, the scale, and two rectangularity scores. It writes an overlay image and a confidence value. The confidence is a shape score (the smaller of the paper and reference rectangularity scores), not a probability. It prints `RESULT: object not found` or `RESULT: reference not found` when it cannot find the paper or the reference.

## Dataset summary

- Object: one white paper sheet, about 290 × 205 mm (ruler measurement, not yet calliper).
- Reference object: a flat piece of cardboard, size to be measured with a calliper.
- Images: 10 captured so far (target 70).
- Split: `dataset\split_v1.csv` lists 100 planned IDs (70 / 20 / 10). It is not applied to the captured photos yet.
- Labelling tool: none used yet (CVAT or Label Studio planned).
- Background: 3 photos on black cloth, 7 photos on a brown carpet. The brown-carpet photos have lower contrast and are a known weakness.

## Model weights

No weights exist yet. When trained, the file's SHA-256 hash will be written here.

## Pull request

Not created. The `main` branch does not exist yet in this repository, so the pull request must be opened after `main` is created from `dev-test01`.
