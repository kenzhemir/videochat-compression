import time
import numpy as np
import cv2
import compressor
import dithering

comp = compressor.CompressorLZW()
decomp = compressor.DecompressorLZW()


def drawColormap(colormap):
    # print(sum(colormap))
    pass


def printRatio(A, B):
    print("Compression ratio: ", A.size / B.size)


def processor(frame):
    
    compressed = comp.compress(frame)
    # drawColormap(colormap)
    printRatio(frame, compressed)
    return frame


def startCamera(frameProcessor, frameWriter):
    cap = cv2.VideoCapture(0)

    _, frame = cap.read()
    prev = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    while (True):
        # Capture frame-by-frame

        t1 = time.time()

        _, frame = cap.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        difference = frame - prev
        diff = frameProcessor(difference)
        frame = prev + diff

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