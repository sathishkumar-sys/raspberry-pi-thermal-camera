
import numpy as np


def get_temperature_stats(temp_img):

    temp_img = np.asarray(temp_img, dtype=np.float32)

    min_temp = float(np.min(temp_img))
    max_temp = float(np.max(temp_img))
    avg_temp = float(np.mean(temp_img))

    center_temp = float(
        temp_img[
            temp_img.shape[0] // 2,
            temp_img.shape[1] // 2
        ]
    )

    return min_temp, max_temp, avg_temp, center_temp
