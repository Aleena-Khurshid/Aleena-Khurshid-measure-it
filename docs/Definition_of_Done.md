# Definition of Done — Measure It

Checked at 2026-11-18 00:10 (Asia/Karachi). A box is ticked only when the evidence exists in this repository or in a stated commit.

## Assessment deliverables

- [~] **1. Calibrated camera.** 20 chessboard photos calibrated with OpenCV. Parameters saved to `calibration/camera_params.npz`. Reprojection error reported: 0.092 px RMS. Evidence: `calibration/calibration_report.json`, commit `af5f0ae`. **Partly done:** the undistortion is not verified. Undistorted images still show curved edges at the corners, because the calibration board does not cover the image edges. Not ticked.
- [~] **4. Image-to-mm command (partial).** `inference/measure.py` undistorts, finds the paper and the cardboard reference, and prints sizes. It runs on the 3 black-background photos (reference found, rectangularity 0.99). On the 7 brown-carpet photos, the reference is not found, which is the correct output for that case. Cardboard reference measured with a ruler (not a calliper): 129 mm x 144 mm. On the 3 black-background photos this gives paper sides of 296-300 mm x 216-221 mm (ruler estimate of the paper: about 290 x 205 mm). The scale differs from photo to photo (0.36 to 0.48 mm/px). Pixel check: the cardboard is 404, 348 and 301 px long in the three photos, and the paper is 831, 730 and 620 px long, so the camera distance changed between photos. The paper-to-cardboard ratio stays at 2.06 to 2.10, which is why the paper mm agree. This is a self-consistency check only, not proof of accuracy. The undistortion is not reliable, so these mm values are not verified. Evidence: commit to follow.
- [ ] **2. Labelled dataset.** Target 70 original photos, masks, 70/20/10 split. Done so far: 10 photos captured. Not done: labelling, masks, undistortion of the paper photos, and a split that matches the captured images. Evidence of split plan: `dataset/split_v1.csv`, commit `0d4e956` (lists 100 planned IDs; not applied to the captured photos).
- [ ] **3. Segmentation model.** Not started. No training, no test evaluation.
- [ ] **5. Accuracy against calliper.** Not started. No 10-instance table.
- [ ] **6. Undistortion proof.** Not started.

## Process checks

- [x] Plan committed before any code. Evidence: commit `0d4e956` (Plan, split file, git author set to GitHub noreply address).
- [x] Work on branch `dev-test01`, incremental commits. Evidence: `0d4e956`, `af5f0ae`.
- [x] Git history shows calibration as its own commit, not one large commit.
- [ ] Pull request from `dev-test01` into `main`. Not created (see README).
- [ ] Weights hash in README. No weights exist.
- [ ] Loom recording (5 minutes or less) answering K1 to K4. Not recorded.

## Not finished (listed explicitly)

- Deliverables 2 (70 photos and masks), 3, 4, 5 and 6 are not done.
- Deliverables 7 to 10 are out of scope by the candidate's choice.
- The reference object (cardboard piece) size is not yet measured with a calliper. The paper size (about 290 × 205 mm) was measured with a ruler only.
- The board's square size was measured with a ruler, not a calliper. The board is shown on a laptop screen, not printed.

## Dataset status (checked 2026-11-18 00:45)

- 38 photos of paper plus cardboard: 10 earlier photos (1200 × 1600, portrait), 12 photos (1280 × 960, landscape, confirmed as taken by the author), and 16 photos (1280 × 960, landscape, received 00:40; author confirmation pending). Target is 70. Not met.
- The 12 new photos are landscape. The calibration was made on portrait photos (960 × 1280), so `measure.py` now refuses them with `RESULT: calibration mismatch`. They need a calibration in landscape orientation before they can be measured.
- Photos are not flipped, and flipped copies are not counted.
- Of the 16 newest photos, 15 detect both paper and cardboard (paper score 0.98 to 0.99). One photo (16th) detects the paper (0.93) but not the cardboard.
- No landscape calibration exists yet. The only landscape item received was a screen image (1920 × 1080), not a photo of a board, so it cannot be used for calibration.
- No masks exist yet. No split is applied to these photos. No model is trained.

