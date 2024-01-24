import random

import numpy as np

from imageclasses import RGBImage

bayer_matrix = [
    [0, 32, 8, 40, 2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21]
]



def ordered_dithering(rgb_image, bitness=8):
    pixels = list(rgb_image.pixels[:])
    w = rgb_image.width
    h = rgb_image.height
    dithered_pixels = bytearray(len(pixels))
    amount_of_colors = 2 ** bitness
    coef = 255 / (amount_of_colors - 1)

    for i in range(h):
        for j in range(w):
            r = pixels[3 * (i * w + j)]
            g = pixels[3 * (i * w + j) + 1]
            b = pixels[3 * (i * w + j) + 2]
            r = r + coef * (bayer_matrix[i % 8][j % 8] / 64 - 0.5)
            g = g + coef * (bayer_matrix[i % 8][j % 8] / 64 - 0.5)
            b = b + coef * (bayer_matrix[i % 8][j % 8] / 64 - 0.5)
            dithered_pixels[3 * (i * w + j)] = int(nearest_color(r, amount_of_colors))
            dithered_pixels[3 * (i * w + j) + 1] = int(nearest_color(g, amount_of_colors))
            dithered_pixels[3 * (i * w + j) + 2] = int(nearest_color(b, amount_of_colors))
    return RGBImage(w, h, dithered_pixels)


def random_dithering(rgb_image, bitness=8):
    pixels = list(rgb_image.pixels[:])
    w = rgb_image.width
    h = rgb_image.height
    dithered_pixels = bytearray(len(pixels))
    amount_of_colors = 2 ** bitness
    coef = 255 / (amount_of_colors - 1)

    for i in range(h):
        for j in range(w):
            rnd = random.randint(0, 63)
            r = pixels[3 * (i * w + j)]
            g = pixels[3 * (i * w + j) + 1]
            b = pixels[3 * (i * w + j) + 2]
            r = r + coef * (rnd / 64 - 0.5)
            g = g + coef * (rnd / 64 - 0.5)
            b = b + coef * (rnd / 64 - 0.5)
            dithered_pixels[3 * (i * w + j)] = int(nearest_color(r, amount_of_colors))
            dithered_pixels[3 * (i * w + j) + 1] = int(nearest_color(g, amount_of_colors))
            dithered_pixels[3 * (i * w + j) + 2] = int(nearest_color(b, amount_of_colors))
    return RGBImage(w, h, dithered_pixels)



def floyd_steinberg_dithering(rgb_image, bitness=8):
    pixels = list(rgb_image.pixels[:])
    w = rgb_image.width
    h = rgb_image.height
    dithered_pixels = np.array(pixels, dtype=float)
    amount_of_colors = 2 ** bitness
    coef = 255 / (amount_of_colors - 1)

    for i in range(h):
        for j in range(w):
            r = dithered_pixels[3 * (i * w + j)]
            g = dithered_pixels[3 * (i * w + j) + 1]
            b = dithered_pixels[3 * (i * w + j) + 2]

            new_r = nearest_color(r, amount_of_colors)
            new_g = nearest_color(g, amount_of_colors)
            new_b = nearest_color(b, amount_of_colors)

            dithered_pixels[3 * (i * w + j)] = new_r
            dithered_pixels[3 * (i * w + j) + 1] = new_g
            dithered_pixels[3 * (i * w + j) + 2] = new_b

            r_err = r - new_r
            g_err = g - new_g
            b_err = b - new_b

            if j + 1 < w:
                dithered_pixels[3 * (i * w + j + 1)] += r_err * 7 / 16
                dithered_pixels[3 * (i * w + j + 1) + 1] += g_err * 7 / 16
                dithered_pixels[3 * (i * w + j + 1) + 2] += b_err * 7 / 16
            if i + 1 < h:
                if j - 1 >= 0:
                    dithered_pixels[3 * ((i + 1) * w + j - 1)] += r_err * 3 / 16
                    dithered_pixels[3 * ((i + 1) * w + j - 1) + 1] += g_err * 3 / 16
                    dithered_pixels[3 * ((i + 1) * w + j - 1) + 2] += b_err * 3 / 16
                dithered_pixels[3 * ((i + 1) * w + j)] += r_err * 5 / 16
                dithered_pixels[3 * ((i + 1) * w + j) + 1] += g_err * 5 / 16
                dithered_pixels[3 * ((i + 1) * w + j) + 2] += b_err * 5 / 16
                if j + 1 < w:
                    dithered_pixels[3 * ((i + 1) * w + j + 1)] += r_err / 16
                    dithered_pixels[3 * ((i + 1) * w + j + 1) + 1] += g_err / 16
                    dithered_pixels[3 * ((i + 1) * w + j + 1) + 2] += b_err / 16
    return RGBImage(w, h, dithered_pixels.astype(np.uint8))



def atkinson_dithering(rgb_image, bitness=8):
    pixels = list(rgb_image.pixels[:])
    w = rgb_image.width
    h = rgb_image.height
    dithered_pixels = np.array(pixels, dtype=float)
    amount_of_colors = 2 ** bitness
    coef = 255 / (amount_of_colors - 1)

    for i in range(h):
        for j in range(w):
            r = dithered_pixels[3 * (i * w + j)]
            g = dithered_pixels[3 * (i * w + j) + 1]
            b = dithered_pixels[3 * (i * w + j) + 2]

            new_r = nearest_color(r, amount_of_colors)
            new_g = nearest_color(g, amount_of_colors)
            new_b = nearest_color(b, amount_of_colors)

            dithered_pixels[3 * (i * w + j)] = new_r
            dithered_pixels[3 * (i * w + j) + 1] = new_g
            dithered_pixels[3 * (i * w + j) + 2] = new_b

            r_err = r - new_r
            g_err = g - new_g
            b_err = b - new_b

            if j + 1 < w:
                dithered_pixels[3 * (i * w + j + 1)] += r_err * 1 / 8
                dithered_pixels[3 * (i * w + j + 1) + 1] += g_err * 1 / 8
                dithered_pixels[3 * (i * w + j + 1) + 2] += b_err * 1 / 8
            if j + 2 < w:
                dithered_pixels[3 * (i * w + j + 2)] += r_err * 1 / 8
                dithered_pixels[3 * (i * w + j + 2) + 1] += g_err * 1 / 8
                dithered_pixels[3 * (i * w + j + 2) + 2] += b_err * 1 / 8
            if i + 1 < h:
                if j - 1 >= 0:
                    dithered_pixels[3 * ((i + 1) * w + j - 1)] += r_err * 1 / 8
                    dithered_pixels[3 * ((i + 1) * w + j - 1) + 1] += g_err * 1 / 8
                    dithered_pixels[3 * ((i + 1) * w + j - 1) + 2] += b_err * 1 / 8
                dithered_pixels[3 * ((i + 1) * w + j)] += r_err * 1 / 8
                dithered_pixels[3 * ((i + 1) * w + j) + 1] += g_err * 1 / 8
                dithered_pixels[3 * ((i + 1) * w + j) + 2] += b_err * 1 / 8
                if j + 1 < w:
                    dithered_pixels[3 * ((i + 1) * w + j + 1)] += r_err * 1 / 8
                    dithered_pixels[3 * ((i + 1) * w + j + 1) + 1] += g_err * 1 / 8
                    dithered_pixels[3 * ((i + 1) * w + j + 1) + 2] += b_err * 1 / 8
            if i + 2 < h:
                if j + 1 < w:
                    dithered_pixels[3 * ((i + 2) * w + j + 1)] += r_err * 1 / 8
                    dithered_pixels[3 * ((i + 2) * w + j + 1) + 1] += g_err * 1 / 8
                    dithered_pixels[3 * ((i + 2) * w + j + 1) + 2] += b_err * 1 / 8
                if j + 2 < w:
                    dithered_pixels[3 * ((i + 2) * w + j + 2)] += r_err * 1 / 8
                    dithered_pixels[3 * ((i + 2) * w + j + 2) + 1] += g_err * 1 / 8
                    dithered_pixels[3 * ((i + 2) * w + j + 2) + 2] += b_err * 1 / 8
    return RGBImage(w, h, dithered_pixels.astype(np.uint8))


def nearest_color(pixel, amount_of_colors):
    if pixel < 0:
        return 0
    if pixel > 255:
        return 255
    coef = 255 / (amount_of_colors - 1)
    lowest = pixel // coef * coef
    highest = lowest + coef
    if abs(pixel - lowest) < abs(pixel - highest):
        return lowest
    else:
        return highest


#
# image = RGBImage.read_from_file('images/gradient_rgb')
# image = ordered_dithering(image, 2)
# image.write_to_file('images/sample_1920×1280_p6_ordered_dithering')
