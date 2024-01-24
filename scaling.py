import math

from imageclasses import RGBImage
def nearest_neighbor(rgb_image, width, height):
    pixels = list(rgb_image.pixels)
    width, height = int(width), int(height)
    new_pixels = bytearray(width * height * 3)
    w = rgb_image.width
    h = rgb_image.height
    if width == w and height == h:
        return rgb_image
    w_coef = w / width
    h_coef = h / height
    for i in range(height):
        for j in range(width):
            x = int(j * w_coef + 0.49)
            y = int(i * h_coef + 0.49)
            new_pixels[3 * (i * width + j)] = pixels[3 * (y * w + x)]
            new_pixels[3 * (i * width + j) + 1] = pixels[3 * (y * w + x) + 1]
            new_pixels[3 * (i * width + j) + 2] = pixels[3 * (y * w + x) + 2]

    return RGBImage(width, height, new_pixels)


def bilinear_scaling(rgb_image, width, height):
    pixels = rgb_image.pixels
    width, height = int(width), int(height)
    new_pixels = bytearray(int(width * height * 3))
    w = rgb_image.width
    h = rgb_image.height
    if width == w and height == h:
        return rgb_image
    w_coef = (w - 1) / width
    h_coef = (h - 1) / height
    for i in range(height):
        for j in range(width):
            x = int(j * w_coef)
            y = int(i * h_coef)
            delta_x = j * w_coef - x
            delta_y = i * h_coef - y
            square = [
                pixels[3 * (y * w + x): 3 * (y * w + x) + 3],
                pixels[3 * (y * w + x + 1): 3 * (y * w + x + 1) + 3],
                pixels[3 * ((y + 1) * w + x): 3 * ((y + 1) * w + x) + 3],
                pixels[3 * ((y + 1) * w + x + 1): 3 * ((y + 1) * w + x + 1) + 3]
            ]

            new_pixels[3 * (i * width + j)] = int(
                square[0][0] * (1 - delta_x) * (1 - delta_y) + square[1][0] * delta_x * (
                        1 - delta_y) + square[2][0] * (1 - delta_x) * delta_y + square[3][0] * delta_x * delta_y)
            new_pixels[3 * (i * width + j) + 1] = int(
                square[0][1] * (1 - delta_x) * (1 - delta_y) + square[1][1] * delta_x * (
                        1 - delta_y) + square[2][1] * (1 - delta_x) * delta_y + square[3][1] * delta_x * delta_y)
            new_pixels[3 * (i * width + j) + 2] = int(
                square[0][2] * (1 - delta_x) * (1 - delta_y) + square[1][2] * delta_x * (
                        1 - delta_y) + square[2][2] * (1 - delta_x) * delta_y + square[3][2] * delta_x * delta_y)

    return RGBImage(width, height, new_pixels)


def pixel_formula(b, c, square, d):
    return (((-1 / 6 * b - c) * square[0] + (-3 / 2 * b - c + 2) * square[1] + (
            3 / 2 * b + c - 2) * square[2] + (1 / 6 * b + c) * square[3]) * d * d * d + (
                    (1 / 2 * b + 2 * c) * square[0] + (2 * b + c - 3) * square[1] + (
                    -5 / 2 * b - 2 * c + 3) * square[2] - c * square[3]) * d * d + (
                    ((-1 / 2 * b - c) * square[0] + (1 / 2 * b + c) * square[1]) * d + (
                    1 / 6 * b * square[2]) + (-1 / 3 * b + 1) * square[1] + (1 / 6 * b * square[2])))


def bc_splines(rgb_image, width, height, b=0, c=0.5):
    pixels = rgb_image.pixels
    width, height = int(width), int(height)
    w = rgb_image.width
    h = rgb_image.height
    if width == w and height == h:
        return rgb_image
    w_coef = (w - 1) / width
    h_coef = (h - 1) / height
    new_pixels = bytearray(width * height * 3)
    for i in range(height):
        for j in range(width):
            x = int(j * w_coef)
            y = int(i * h_coef)
            red_square = [
                pixels[3 * (y * w + x)],
                pixels[3 * (y * w + x + 1)],
                pixels[3 * ((y + 1) * w + x)],
                pixels[3 * ((y + 1) * w + x + 1)],
            ]
            green_square = [
                pixels[3 * (y * w + x) + 1],
                pixels[3 * (y * w + x + 1) + 1],
                pixels[3 * ((y + 1) * w + x) + 1],
                pixels[3 * ((y + 1) * w + x + 1) + 1],
            ]
            blue_square = [
                pixels[3 * (y * w + x) + 2],
                pixels[3 * (y * w + x + 1) + 2],
                pixels[3 * ((y + 1) * w + x) + 2],
                pixels[3 * ((y + 1) * w + x + 1) + 2],
            ]
            distance = 1
            new_pixels[3 * (i * width + j)] = int(pixel_formula(b, c, red_square, distance))
            new_pixels[3 * (i * width + j) + 1] = int(pixel_formula(b, c, green_square, distance))
            new_pixels[3 * (i * width + j) + 2] = int(pixel_formula(b, c, blue_square, distance))
    return RGBImage(width, height, new_pixels)


def is_zero(x):
    return -0.01 < x < 0.01


def lanczos_kernel(x):
    if is_zero(x):
        return 1
    if -3 <= x < 3:
        x = x * math.pi
        return 3 * math.sin(x) * math.sin(x / 3) / (x * x)
    return 0


def lanczos3(rgb_image, width, height):
    pixels = rgb_image.pixels
    width, height = int(width), int(height)
    w = rgb_image.width
    h = rgb_image.height
    if width == w and height == h:
        return rgb_image
    w_coef = (w - 1) / width
    h_coef = (h - 1) / height
    new_pixels = bytearray(width * height * 3)
    for i in range(height):
        for j in range(width):
            x = int(j * w_coef)
            y = int(i * h_coef)
            rgb = [0, 0, 0]
            for k in range(max(0, x - 3), min(w, x + 4)):
                l_x = lanczos_kernel((x - k))
                if is_zero(l_x):
                    continue
                for l in range(max(0, y - 3), min(h, y + 4)):
                    l_coef = l_x * lanczos_kernel((y - l))
                    rgb[0] += pixels[3 * (l * w + k)] * l_coef
                    rgb[1] += pixels[3 * (l * w + k) + 1] * l_coef
                    rgb[2] += pixels[3 * (l * w + k) + 2] * l_coef
            for index in range(3):
                if rgb[index] < 0:
                    rgb[index] = 0
                if rgb[index] > 255:
                    rgb[index] = 255
            new_pixels[3 * (i * width + j)] = int(rgb[0])
            new_pixels[3 * (i * width + j) + 1] = int(rgb[1])
            new_pixels[3 * (i * width + j) + 2] = int(rgb[2])
    return RGBImage(width, height, new_pixels)

# image = RGBImage.read_from_file('images/sample_1920×1280_p6.pnm')
# nearest_neighbor(image, 1920 * 2, 1280 * 2).write_to_file('images/sample_1920×1280_p6_nearest_neighbor.pnm')

# image = RGBImage.read_from_file('images/sample_1920×1280_p6.pnm')
# bilinear_scaling(image, 3840, 2160).write_to_file('images/sample_1920×1280_p6_bilinear.pnm')


# image = RGBImage.read_from_file('images/sample_1920×1280_p6.pnm')
# bc_splines(image, 3840, 2160).write_to_file('images/sample_1920×1280_p6_bc_splines.pnm')
#
# images = RGBImage.read_from_file('images/sample_1920×1280_p6.pnm')
# lanczos3(images, 1920 * 2, 1280 * 2).write_to_file('images/sample_1920×1280_p6_lanczos.pnm')
