"""Check undistortion on the calibration board photos.

For each portrait calibration photo, find the 9 x 7 inner corners, fit a
straight line to each row of 9 corners, and record the largest distance of
any corner from its row line. Run on the raw photo and on the undistorted photo.
"""
import glob

import cv2
import numpy as np

PATTERN = (9, 7)
CALIB = "calibration/camera_params.npz"
IMAGES = "calibration/images/*.jpg"


def row_deviation(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, PATTERN, None)
    if not found:
        return None
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)
    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    corners = corners.reshape(PATTERN[1], PATTERN[0], 2)
    worst = 0.0
    for row in corners:
        A = np.c_[row[:, 0], np.ones(len(row))]
        m = np.linalg.lstsq(A, row[:, 1], rcond=None)[0]
        worst = max(worst, float(np.abs(row[:, 1] - A @ m).max()))
    return worst


def main():
    data = np.load(CALIB)
    K, D = data["camera_matrix"], data["dist_coeffs"]
    raw, und, names = [], [], []
    for path in sorted(glob.glob(IMAGES)):
        img = cv2.imread(path)
        if img.shape[0] < img.shape[1]:
            continue  # portrait only, same size as the calibration
        a = row_deviation(img)
        b = row_deviation(cv2.undistort(img, K, D))
        if a is None or b is None:
            continue
        raw.append(a)
        und.append(b)
        names.append(path)
    print(f"images used: {len(raw)}")
    print(f"raw         max row deviation (px): mean {np.mean(raw):.2f}, worst {np.max(raw):.2f}")
    print(f"undistorted max row deviation (px): mean {np.mean(und):.2f}, worst {np.max(und):.2f}")


if __name__ == "__main__":
    main()
