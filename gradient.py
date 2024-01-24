from imageclasses import RGBImage


def gradient(x, y):
    pixels = bytearray(x * y * 3)
    diff = 255 / x
    for i in range(x):
        for j in range(y):
            pixels[3 * (i + j * x)] = int(i * diff)
            pixels[3 * (i + j * x) + 1] = int(i * diff)
            pixels[3 * (i + j * x) + 2] = int(i * diff)

    return RGBImage(x, y, pixels)


# image = gradient(1920, 1080)
# image.write_to_file('images/gradient_rgb')
