"""Image to millimetres for a flat paper sheet, using a flat cardboard reference.

Steps: undistort with the saved calibration, find the paper (bright region),
find the reference (brown rectangle), convert pixels to mm with the reference
size, and print width, height and a rectangularity score.

Segmentation here is classical thresholding, not a trained model.

Usage (PowerShell, from the repository root):
    python inference\\measure.py --image path\\to\\photo.jpg --ref-w-mm 90 --ref-h-mm 85
"""

import argparse
import os

import cv2
import numpy as np

MIN_PAPER_FRACTION = 0.05   # paper must cover at least 5% of the image
MIN_REF_FRACTION = 0.002    # reference must cover at least 0.2% of the image
MIN_PAPER_RECTANGULARITY = 0.90  # paper must look like a rectangle
MIN_REF_RECTANGULARITY = 0.90  # reference must look like a rectangle (0.99 on good photos, 0.50 on brown carpet)


def undistort(image, calib_path):
    """Undistort with the saved calibration.

    The camera matrix is only valid for the calibration image size and
    orientation. If the photo has a different size, scale fx, cx by the
    width ratio and fy, cy by the height ratio. If the photo is rotated
    (landscape vs portrait), the calibration does not apply and we refuse.
    """
    data = np.load(calib_path)
    K = data["camera_matrix"].astype(np.float64).copy()
    cal_w, cal_h = int(data["image_width"]), int(data["image_height"])
    h, w = image.shape[:2]
    if (w > h) != (cal_w > cal_h):
        raise ValueError(f"calibration is {cal_w}x{cal_h} (portrait) but photo is {w}x{h} (landscape)")
    K[0, :] *= w / cal_w
    K[1, :] *= h / cal_h
    return cv2.undistort(image, K, data["dist_coeffs"])


def largest_rect(mask):
    found = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = found[-2]  # contours are second-to-last in OpenCV 4 and 5
    if not contours:
        return None, 0.0
    best = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(best)
    hull_area = cv2.contourArea(cv2.convexHull(best))
    rectangularity = area / hull_area if hull_area > 0 else 0.0
    return best, rectangularity


def rect_sides_px(contour):
    (_, _), (w, h), _ = cv2.minAreaRect(contour)
    return max(w, h), min(w, h)


def find_paper(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contour, rectangularity = largest_rect(mask)
    if contour is None or cv2.contourArea(contour) < MIN_PAPER_FRACTION * image.shape[0] * image.shape[1]:
        return None, 0.0, mask
    return contour, rectangularity, mask


def find_reference(image, paper_contour):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    brown = cv2.inRange(hsv, (5, 60, 60), (25, 255, 255))
    if paper_contour is not None:
        paper_fill = np.zeros(brown.shape, np.uint8)
        cv2.drawContours(paper_fill, [paper_contour], -1, 255, -1)
        brown = cv2.bitwise_and(brown, cv2.bitwise_not(paper_fill))
    kernel = np.ones((5, 5), np.uint8)
    brown = cv2.morphologyEx(brown, cv2.MORPH_OPEN, kernel)
    brown = cv2.morphologyEx(brown, cv2.MORPH_CLOSE, kernel)
    contour, rectangularity = largest_rect(brown)
    if contour is None or cv2.contourArea(contour) < MIN_REF_FRACTION * image.shape[0] * image.shape[1] or rectangularity < MIN_REF_RECTANGULARITY:
        return None, 0.0
    return contour, rectangularity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--calib", default="calibration/camera_params.npz")
    parser.add_argument("--ref-w-mm", type=float, required=True)
    parser.add_argument("--ref-h-mm", type=float, required=True)
    parser.add_argument("--overlay", default="inference/overlay.jpg")
    args = parser.parse_args()

    raw = cv2.imread(args.image)
    if raw is None:
        raise SystemExit("Cannot read image.")
    try:
        image = undistort(raw, args.calib)
    except ValueError as err:
        print(f"RESULT: calibration mismatch: {err}")
        return

    paper, paper_rect, _ = find_paper(image)
    if paper is None:
        print("RESULT: object not found")
        return
    ref, ref_rect = find_reference(image, paper)
    if ref is None:
        print("RESULT: reference not found")
        return
    if paper_rect < MIN_PAPER_RECTANGULARITY:
        print(f"RESULT: object not found (paper shape score {paper_rect:.3f} is below {MIN_PAPER_RECTANGULARITY})")
        return

    ref_long_px, ref_short_px = rect_sides_px(ref)
    ref_long_mm, ref_short_mm = max(args.ref_w_mm, args.ref_h_mm), min(args.ref_w_mm, args.ref_h_mm)
    mm_per_px = (ref_long_mm / ref_long_px + ref_short_mm / ref_short_px) / 2

    paper_long_px, paper_short_px = rect_sides_px(paper)
    long_mm = paper_long_px * mm_per_px
    short_mm = paper_short_px * mm_per_px

    overlay = image.copy()
    cv2.drawContours(overlay, [paper], -1, (0, 255, 0), 3)
    cv2.drawContours(overlay, [ref], -1, (255, 0, 0), 3)
    os.makedirs(os.path.dirname(args.overlay) or ".", exist_ok=True)
    cv2.imwrite(args.overlay, overlay)

    confidence = min(paper_rect, ref_rect)  # shape score, not a probability
    print(f"RESULT: ok")
    print(f"Paper sides: {long_mm:.1f} mm x {short_mm:.1f} mm (long x short)")
    print(f"Confidence (shape score, min of paper and reference rectangularity): {confidence:.3f}")
    print(f"Scale: {mm_per_px:.4f} mm per pixel")
    print(f"Rectangularity paper: {paper_rect:.3f}, reference: {ref_rect:.3f}")
    print(f"Overlay: {args.overlay}")


if __name__ == "__main__":
    main()
