"""Camera calibration with OpenCV chessboard corners.

Usage (PowerShell, from the repository root):
    python calibration/calibrate.py --images calibration/images --cols 7 --rows 9 --square-mm 20.0

--cols and --rows are INNER corners (7 x 9 for the hand-drawn 8 x 10 square board).
--square-mm is the measured square size. It only scales the translation vectors;
the camera matrix and distortion coefficients do not depend on it.
"""

import argparse
import glob
import json
import os

import cv2
import numpy as np


def find_corners(gray, pattern):
    found, corners = cv2.findChessboardCorners(gray, pattern, None)
    if not found:
        return None
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    return cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", required=True, help="folder with calibration photos")
    parser.add_argument("--cols", type=int, default=7, help="inner corners per row")
    parser.add_argument("--rows", type=int, default=9, help="inner corners per column")
    parser.add_argument("--square-mm", type=float, required=True, help="measured square size in mm")
    parser.add_argument("--out", default="calibration", help="output folder")
    args = parser.parse_args()

    pattern = (args.cols, args.rows)
    objp = np.zeros((args.rows * args.cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:args.cols, 0:args.rows].T.reshape(-1, 2) * args.square_mm

    files = sorted(
        f for ext in ("*.jpg", "*.jpeg", "*.png") for f in glob.glob(os.path.join(args.images, ext))
    )
    obj_points, img_points, used, skipped = [], [], [], []
    image_size = None

    for path in files:
        gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if gray is None:
            skipped.append((os.path.basename(path), "unreadable"))
            continue
        image_size = gray.shape[::-1]
        corners = find_corners(gray, pattern)
        if corners is None:
            skipped.append((os.path.basename(path), "board not found"))
            continue
        obj_points.append(objp)
        img_points.append(corners)
        used.append(os.path.basename(path))

    if len(used) < 10:
        raise SystemExit(f"Only {len(used)} usable photos. Need at least 20.")

    rms, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, image_size, None, None
    )

    per_image = []
    for i, (op, ip) in enumerate(zip(obj_points, img_points)):
        projected, _ = cv2.projectPoints(op, rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
        diff = ip.reshape(-1, 2) - projected.reshape(-1, 2)
        err = float(np.sqrt((diff ** 2).sum(axis=1)).mean())
        per_image.append((used[i], float(err)))

    os.makedirs(args.out, exist_ok=True)
    np.savez(
        os.path.join(args.out, "camera_params.npz"),
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        image_width=image_size[0],
        image_height=image_size[1],
    )
    with open(os.path.join(args.out, "calibration_report.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "usable_images": len(used),
                "skipped": skipped,
                "pattern_inner_corners": list(pattern),
                "square_mm": args.square_mm,
                "image_size": list(image_size),
                "rms_reprojection_error_px": float(rms),
                "mean_reprojection_error_px": float(np.mean([e for _, e in per_image])),
                "max_per_image_error_px": float(max(e for _, e in per_image)),
                "camera_matrix": camera_matrix.tolist(),
                "dist_coeffs": dist_coeffs.ravel().tolist(),
                "per_image_error_px": per_image,
            },
            f,
            indent=2,
        )

    print(f"Usable images: {len(used)} / {len(files)}")
    for name, reason in skipped:
        print(f"  skipped {name}: {reason}")
    print(f"Image size: {image_size[0]} x {image_size[1]}")
    print(f"RMS reprojection error: {rms:.4f} px")
    print(f"Mean per-image error: {np.mean([e for _, e in per_image]):.4f} px")
    print("Camera matrix:\n", camera_matrix)
    print("Distortion coefficients:", dist_coeffs.ravel())


if __name__ == "__main__":
    main()
