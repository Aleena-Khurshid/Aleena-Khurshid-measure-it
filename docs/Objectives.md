# Objectives — Measure It

Status is written as it stands at 2026-11-18 00:10 (Asia/Karachi). Nothing here is claimed without evidence.

## MO-1: Measurement accuracy (required)

| Field | Entry |
|---|---|
| What is measured | Mean absolute error (mm) of width and height of a white paper sheet, system vs calliper, on 10 instances |
| How | `measurement/` script compares the system output with hand calliper values, per instance |
| Target | MAE ≤ 2.0 mm on width and height, over 10 instances. Chosen because a packaging-scale check needs about 1% accuracy on a 200 mm sheet |
| Conditions | Phone camera (model: TBD), locked focus, zoom and resolution, black background, camera top-down, reference object in the same plane |
| Not included | Tilted images, glare, curled paper |
| Status | **Not measured.** The pixel-to-mm command is not built yet, so there is no error number. |

## MO-2: Mask quality (my choice)

| Field | Entry |
|---|---|
| What is measured | Mask IoU on the held-out test split |
| How | Compare predicted masks with hand-labelled masks, test split only |
| Target | Mean IoU ≥ 0.90 on the test split |
| Conditions | Same camera settings as MO-1; test split fixed before training |
| Status | **Not measured.** No model is trained and no test split is labelled. |

## Calibration target (supporting)

| Field | Entry |
|---|---|
| What is measured | RMS reprojection error of the camera calibration |
| Target | ≤ 0.5 px |
| Result | **0.092 px RMS, 0.079 px mean per image, 20 images.** Evidence: `calibration/calibration_report.json`, commit `af5f0ae`. |
| Caveat | The 20 photos are of a single board on a laptop screen, and are WhatsApp copies (960 × 1280). The board covers only the centre of the frame, so the distortion at the image edges is not constrained. Undistorted test images show curved edges at the corners, with all five coefficients free (k2 ≈ −1.98, k3 ≈ 4.13) and also with k3 fixed to 0 (k2 ≈ −0.64, RMS 0.165 px). **The undistortion is not reliable, and mm results on undistorted images must not be trusted yet.** |

## Dataset (supporting)

| Field | Entry |
|---|---|
| Target | 70 or more original photos of the paper, split 70/20/10 |
| Result | **10 unique photos captured** (paper and cardboard reference together), from about 40 minutes of shooting. The 70 target is **not met**. |
| Caveat | The 10 photos are not yet labelled, and no masks exist. Duplicate photos were removed by file hash before counting. |
