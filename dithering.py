import cv2
import numpy as np
import time


def ditherSingle(image, levels=8):
    '''
    for each y from top to bottom
        for each x from left to right
            oldpixel  := pixel[x][y]
            newpixel  := find_closest_palette_color(oldpixel)
            pixel[x][y]  := newpixel
            quant_error  := oldpixel - newpixel
            pixel[x+1][y  ] := pixel[x+1][y  ] + quant_error * 7/16
            pixel[x-1][y+1] := pixel[x-1][y+1] + quant_error * 3/16
            pixel[x  ][y+1] := pixel[x  ][y+1] + quant_error * 5/16
            pixel[x+1][y+1] := pixel[x+1][y+1] + quant_error * 1/16
    '''
    w, h = image.shape
    for x in range(w):
        for y in range(h):
            oldpixel = image[x][y]
            newpixel = find_closest_palette_color(oldpixel, levels)
            image[x][y] = newpixel
            quant_error = oldpixel - newpixel
            if x < w - 1:
                image[x + 1][y] += quant_error * 7 / 16
                if y < h - 1:
                    image[x + 1][y + 1] += quant_error * 1 / 16
            if y < h - 1:
                image[x][y + 1] += quant_error * 5 / 16
                if x > 0:
                    image[x - 1][y + 1] += quant_error * 3 / 16
    return image


def find_closest_palette_color(pixel, levels):
    section_width = 256 / levels
    section_number = int(pixel / section_width)
    return section_number * int(255 / (levels - 1))


def ditherColor(image, levels=8):
    b = ditherSingle(image[:, :, 0], levels)
    g = ditherSingle(image[:, :, 1], levels)
    r = ditherSingle(image[:, :, 2], levels)
    return np.dstack((b, g, r))


def ditherTruncate(image, bits=4):
    return np.left_shift(np.right_shift(image, bits), bits)


def ditherTruncateAndPack(image, bits=4):
    im = image.flatten()
    result = np.zeros((int(np.round(im.shape[0] / 2)), ))
    result += ditherTruncate(im[0::2], bits)
    result += np.right_shift(im[1::2], bits)
    return result


if __name__ == '__main__':
    im = cv2.imread('lena_rgb.tif')
    cv2.imshow("Window2", im)

    if cv2.waitKey() & 0xFF == ord('q'):
        cv2.destroyAllWindows()
    t1 = time.time()
    res = ditherTruncate(im)
    t2 = time.time()
    print(t2 - t1)
    cv2.imshow("Window", res)
    if cv2.waitKey() & 0xFF == ord('q'):
        cv2.destroyAllWindows()
