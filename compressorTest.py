import time
import numpy as np
import cv2
import compressor
import dithering

comp = compressor.CompressorYCC()
decomp = compressor.DecompressorYCC()


def drawColormap(colormap):
    # print(sum(colormap))
    pass


def printRatio(A, B):
    print("Compression ratio: ", A.size / B.size)


def processor(frame):
    compressed1 = comp.compress(frame)
    compressed2 = dithering.ditherTruncateAndPack(compressed1)
    # drawColormap(colormap)
    decompressed2 = dithering.unpackTruncated(compressed2)
    decompressed1 = decomp.decompress(decompressed2)
    printRatio(decompressed1, compressed2)
    return decompressed1


def startCamera(frameProcessor, frameWriter):
    cap = cv2.VideoCapture(0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    decomp.shape = (height, width, 3)

    _, frame = cap.read()
    # prev = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    while (True):
        # Capture frame-by-frame

        t1 = time.time()

        _, frame = cap.read()

        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # difference = frame - prev
        # diff = frameProcessor(difference)
        # frame = prev + diff
        frame = frameProcessor(frame)

        t2 = time.time()

        print("FPS: ", 1 / (t2 - t1))
        # frameWriter(processedFrame)
        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    startCamera(processor, None)