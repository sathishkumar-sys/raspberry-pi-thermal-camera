
import cv2 as cv
import numpy as np

from config import TEMP_MIN, TEMP_MAX, IMAGE_SCALE


def process_thermal_image(temp_img):

    # Convert to float
    temp_img = np.asarray(temp_img, dtype=np.float32)

    # Restrict temperature range
    clipped = np.clip(temp_img, TEMP_MIN, TEMP_MAX)

    # Normalize temperature
    normalized = (
        (clipped - TEMP_MIN) /
        (TEMP_MAX - TEMP_MIN) * 255
    ).astype(np.uint8)

    # Apply thermal colour map
    thermal = cv.applyColorMap(
        normalized,
        cv.COLORMAP_JET
    )

    # Enlarge image
    thermal = cv.resize(
        thermal,
        None,
        fx=IMAGE_SCALE,
        fy=IMAGE_SCALE,
        interpolation=cv.INTER_CUBIC
    )

    return thermal

