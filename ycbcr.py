import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
from dithering import ditherTruncate


class CompressorYCC:
    def compress(self, image):
        # convert RGB image to YCrCb color space
        image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        # truncate 4 lower bits
        image = ditherTruncate(image)
        # extract each component
        y = image[:, :, 0].flatten()
        cr = image[:, :, 1].flatten()
        cb = image[:, :, 2].flatten()
        # subsample Cr and Cb by 4
        cr = cr[::4]
        cb = cb[::4]
        # concatenate into result
        result = np.concatenate([y, cr, cb])
        # return result
        return result


class DecompressorYCC:
    def __init__(self, shape):
        self.shape = shape

    def decompress(self, image_array):
        # get length of one component in YCrCb image representation
        component_len = self.shape[0] * self.shape[1]
        # extract Y component
        y = image_array[0:component_len]
        # extract Cr and Cb
        cr = image_array[component_len:component_len + component_len // 4]
        cb = image_array[component_len + component_len // 4:, ]
        # up-sample Cr and Cb components
        cr = np.repeat(cr, 4)
        cb = np.repeat(cb, 4)
        # reshape each component
        y = np.reshape(y, (self.shape[0], self.shape[1]))
        cr = np.reshape(cr, (self.shape[0], self.shape[1]))
        cb = np.reshape(cb, (self.shape[0], self.shape[1]))
        # stack components into an image
        image = np.dstack((y, cr, cb))
        # convert YCrCb image to RGB color space
        image = cv2.cvtColor(image, cv2.COLOR_YCrCb2BGR)
        # return image
        return image


if __name__ == '__main__':
    # read image
    image = cv2.imread('image.jpg')
    # get image shape
    shape = image.shape
    # compressor
    compressor = CompressorYCC()
    # compress image
    print('compress')
    start = time.time()
    array = compressor.compress(image)
    end = time.time()
    print('Took {}'.format(end - start))

    # decompressor
    decompressor = DecompressorYCC(shape)
    # decompress image
    print('decompress')
    start = time.time()
    im = decompressor.decompress(array)
    end = time.time()
    print('Took {}'.format(end - start))