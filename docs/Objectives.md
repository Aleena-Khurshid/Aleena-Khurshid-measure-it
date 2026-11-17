# Objectives — Measure It

Status written 2026-11-18 01:58 (Asia/Karachi). A number is listed only when it came from a real run on this machine.

## MO-1: Measurement accuracy (required)

| Field | Entry |
|---|---|
| What is measured | Mean absolute error (mm) of width and height of one white paper sheet, system vs calliper, over 10 or more instances |
| How | Calliper readings typed into `measurement/calliper.csv`; `measurement/` script compares them with `inference/measure.py` output, per instance |
| Target | MAE ≤ 5.0 mm on each side, over 10 instances. Reason: a packaging-scale check is useful at about 2% on a 250 mm sheet. This target is set before measuring. |
| Conditions | Phone camera (model to be recorded), locked focus, zoom and resolution, black background, camera top-down, reference in the same plane |
| Not included | Tilted images, glare, curled paper |
| Status | **Not measured.** No calliper table exists yet. The undistortion check is also not done, so no accuracy number is valid. |

## MO-2: Mask quality on the held-out test split (my choice)

| Field | Entry |
|---|---|
| What is measured | Mask IoU, pixel precision and pixel recall on the 7-image test split |
| How | `models/train_unet.py` evaluation on `dataset/split_v3.csv` test IDs, scored once |
| Target | Mean IoU ≥ 0.90 against hand-labelled masks |
| Conditions | Test split fixed before training (split committed in `dataset/split_v3.csv`) |
| Result so far | Mask IoU 0.991, precision 0.997, recall 0.995 on 7 test images. **This is measured against automatically generated masks, not hand-labelled masks.** It is therefore NOT the target condition, and MO-2 is not met as written. |
| Not computed | mAP@0.5 and mAP@0.5:0.95 (these need instance detections, not covered yet) |

## Supporting: camera calibration

| Field | Entry |
|---|---|
| What is measured | RMS reprojection error of the calibration |
| Target | ≤ 0.5 px |
| Result | **0.092 px RMS, 0.078 px mean per image, 21 images** (board 9 × 7 inner corners, square 15 mm). Evidence: `calibration/calibration_report.json`, commit `76a818b`. One image (`c07.jpg`, 1.20 px) was excluded as an outlier. |
| Caveat | The board is shown on a laptop screen, not printed. All 21 photos are portrait (960 × 1280). The board covers mainly the centre of the frame, so distortion at the edges is weakly constrained. **Undistortion is not yet verified on straight edges.** |

## Supporting: dataset

| Field | Entry |
|---|---|
| Target | 70 or more original photos, 70 / 20 / 10 split |
| Result | 74 unique photos with auto-generated paper masks, split `dataset/split_v3.csv` (52 / 15 / 7) |
| Caveat | Masks are auto-generated and not hand-checked. Photos are not undistorted. The undistortion requirement from the assessment is therefore not met for the dataset. |
