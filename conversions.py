def rgb_to_hsl(rgb_pixels):
    hsl_pixels = [0] * len(rgb_pixels)

    for i in range(0, len(rgb_pixels), 3):
        r, g, b = rgb_pixels[i] / 255, rgb_pixels[i + 1] / 255, rgb_pixels[i + 2] / 255

        max_val = max(r, g, b)
        min_val = min(r, g, b)

        l = (max_val + min_val) / 2

        if max_val == min_val:
            h = 0
            s = 0
        else:
            if l == 0:
                s = 0
            elif l <= 0.5:
                s = (max_val - min_val) / (max_val + min_val)
            else:
                s = (max_val - min_val) / (2 - (max_val + min_val))

            if max_val == g:
                h = 60 * (b - r) / (max_val - min_val) + 120
            elif max_val == b:
                h = 60 * (r - g) / (max_val - min_val) + 240
            elif g >= b:
                h = 60 * (g - b) / (max_val - min_val)
            else:
                h = 60 * (g - b) / (max_val - min_val) + 360

        hsl_pixels[i], hsl_pixels[i + 1], hsl_pixels[i + 2] = h, s, l

    return hsl_pixels


def hsl_to_rgb(hsl_pixels):
    rgb_pixels = bytearray(len(hsl_pixels))

    for i in range(0, len(hsl_pixels), 3):
        h, s, l = hsl_pixels[i], hsl_pixels[i + 1], hsl_pixels[i + 2]

        if l < 0.5:
            q = l * (1 + s)
        else:
            q = l + s - (l * s)
        p = 2 * l - q
        h_k = h / 360
        t = [h_k + 1 / 3, h_k, h_k - 1 / 3]

        for c in range(3):
            if t[c] < 0:
                t[c] += 1
            elif t[c] > 1:
                t[c] -= 1

        rgb = [0] * 3
        for c in range(3):
            if t[c] < 1 / 6:
                temp = p + ((q - p) * 6 * t[c])
            elif t[c] < 1 / 2:
                temp = q
            elif t[c] < 2 / 3:
                temp = p + ((q - p) * 6 * (2 / 3 - t[c]))
            else:
                temp = p
            rgb[c] = int(temp * 255 + 0.5)

        rgb_pixels[i], rgb_pixels[i + 1], rgb_pixels[i + 2] = rgb[0], rgb[1], rgb[2]

    return rgb_pixels


def rgb_to_hsv(rgb_pixels):
    hsv_pixels = [0] * len(rgb_pixels)

    for i in range(0, len(rgb_pixels), 3):
        r, g, b = rgb_pixels[i] / 255, rgb_pixels[i + 1] / 255, rgb_pixels[i + 2] / 255

        max_val = max(r, g, b)
        min_val = min(r, g, b)

        v = max_val
        if max_val == min_val:
            h = 0
            s = 0
        else:
            s = 1 - min_val / max_val
            if max_val == g:
                h = 60 * (b - r) / (max_val - min_val) + 120
            elif max_val == b:
                h = 60 * (r - g) / (max_val - min_val) + 240
            elif g >= b:
                h = 60 * (g - b) / (max_val - min_val)
            else:
                h = 60 * (g - b) / (max_val - min_val) + 360
        hsv_pixels[i], hsv_pixels[i + 1], hsv_pixels[i + 2] = h, s, v

    return hsv_pixels


def hsv_to_rgb(hsv_pixels):
    rgb_pixels = bytearray(len(hsv_pixels))

    for i in range(0, len(hsv_pixels), 3):
        h, s, v = hsv_pixels[i], hsv_pixels[i + 1], hsv_pixels[i + 2]
        h_i = int(h) // 60
        v_min = (1 - s) * v
        a = (v - v_min) * (h % 60) / 60
        v_inc = v_min + a
        v_dec = v - a
        if h_i == 0:
            r, g, b = v, v_inc, v_min
        elif h_i == 1:
            r, g, b = v_dec, v, v_min
        elif h_i == 2:
            r, g, b = v_min, v, v_inc
        elif h_i == 3:
            r, g, b = v_min, v_dec, v
        elif h_i == 4:
            r, g, b = v_inc, v_min, v
        elif h_i == 5:
            r, g, b = v, v_min, v_dec
        rgb_pixels[i], rgb_pixels[i + 1], rgb_pixels[i + 2] = int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5)

    return rgb_pixels


def rgb_to_ypp(rgb_pixels, k_r, k_b):
    ypp_pixels = bytearray(len(rgb_pixels))
    for i in range(0, len(rgb_pixels), 3):
        r, g, b = rgb_pixels[i] / 255, rgb_pixels[i + 1] / 255, rgb_pixels[i + 2] / 255
        ypp_pixels[i] = int(max(min(k_r * r + (1 - k_r - k_b) * g + k_b * b, 1), 0) * 255)
        ypp_pixels[i + 1] = int((max(min((b - ypp_pixels[i] / 255) / (2 * (1 - k_b)), 0.5), -0.5) + 0.5) * 255)
        ypp_pixels[i + 2] = int((max(min((r - ypp_pixels[i] / 255) / (2 * (1 - k_r)), 0.5), -0.5) + 0.5) * 255)
    return ypp_pixels


def ypp_to_rgb(ypp_pixels, k_r, k_b):
    rgb_pixels = bytearray(len(ypp_pixels))
    for i in range(0, len(rgb_pixels), 3):
        y, p1, p2 = ypp_pixels[i] / 255, ypp_pixels[i + 1] / 255 - 0.5, ypp_pixels[i + 2] / 255 - 0.5
        rgb_pixels[i] = int(max(min(y + (2 * (1 - k_r)) * p2, 1), 0) * 255)
        rgb_pixels[i + 2] = int(max(min(y + (2 * (1 - k_b)) * p1, 1), 0) * 255)
        rgb_pixels[i + 1] = int(max(min((y - k_r * (rgb_pixels[i] / 255) - k_b * (rgb_pixels[i + 2] / 255)) / (1 - k_r - k_b), 1), 0) * 255)
    return rgb_pixels


def rgb_to_ycbcr601(rgb_pixels):
    return rgb_to_ypp(rgb_pixels, 0.299, 0.114)


def ycbcr601_to_rgb(ycc_pixels):
    return ypp_to_rgb(ycc_pixels, 0.299, 0.114)


def rgb_to_ycbcr709(rgb_pixels):
    return rgb_to_ypp(rgb_pixels, 0.2126, 0.0722)


def ycbcr709_to_rgb(ycc_pixels):
    return ypp_to_rgb(ycc_pixels, 0.2126, 0.0722)


def rgb_to_ycocg(rgb_pixels):
    ycocg_pixels = [0] * len(rgb_pixels)

    for i in range(0, len(rgb_pixels), 3):
        r, g, b = rgb_pixels[i] / 255, rgb_pixels[i + 1] / 255, rgb_pixels[i + 2] / 255
        ycocg_pixels[i] = r / 4 + g / 2 + b / 4
        ycocg_pixels[i + 1] = r / 2 - b / 2
        ycocg_pixels[i + 2] = -r / 4 + g / 2 - b / 4

    return ycocg_pixels


def ycocg_to_rgb(ycocg_pixels):
    rgb_pixels = bytearray(len(ycocg_pixels))

    for i in range(0, len(ycocg_pixels), 3):
        y, co, cg = ycocg_pixels[i], ycocg_pixels[i + 1], ycocg_pixels[i + 2]
        rgb = [int((y + co - cg) * 255),
               int((y + cg) * 255),
               int((y - co - cg) * 255)]
        for j in range(3):
            if rgb[j] < 0:
                rgb[j] = 0
            elif rgb[j] > 255:
                rgb[j] = 255
        rgb_pixels[i] = rgb[0]
        rgb_pixels[i + 1] = rgb[1]
        rgb_pixels[i + 2] = rgb[2]

    return rgb_pixels


def rgb_to_cmy(rgb_pixels):
    cmy_pixels = bytearray(len(rgb_pixels))
    for i in range(0, len(rgb_pixels), 3):
        cmy_pixels[i] = 255 - rgb_pixels[i]
        cmy_pixels[i + 1] = 255 - rgb_pixels[i + 1]
        cmy_pixels[i + 2] = 255 - rgb_pixels[i + 2]
    return cmy_pixels


def cmy_to_rgb(cmy_pixels):
    rgb_pixels = bytearray(len(cmy_pixels))
    for i in range(0, len(cmy_pixels), 3):
        rgb_pixels[i] = 255 - cmy_pixels[i]
        rgb_pixels[i + 1] = 255 - cmy_pixels[i + 1]
        rgb_pixels[i + 2] = 255 - cmy_pixels[i + 2]
    return rgb_pixels