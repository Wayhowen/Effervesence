import cv2
import cv2 as cv
import numpy as np

LOWER_YELLOW = (20, 50, 100)
UPPER_YELLOW = (80, 255, 255)
PREV_CIRCLE = None

class Scope:
    # TODO: might be useful https://mattmaulion.medium.com/color-image-segmentation-image-processing-4a04eca25c0
    def hsv(self, f):
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_YELLOW, UPPER_YELLOW)
        thresholded_img = cv2.bitwise_and(f, f, mask=mask)

        # erosion
        kernel = np.ones((3, 3), np.uint8)
        binary_img = cv2.erode(thresholded_img, kernel, iterations=1)

        return binary_img

    def find_circles(self, bf, f):
        global PREV_CIRCLE
        circles = cv.HoughCircles(bf, cv.HOUGH_GRADIENT, 1.2, 100, param1=100, param2=30, minRadius=75,
                                  maxRadius=200)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            print(circles)
            chosen = None
            for i in circles[0, :]:
                if chosen is None:
                    chosen = i
                if PREV_CIRCLE is not None:
                    if dist(chosen[0], chosen[1], PREV_CIRCLE[0], PREV_CIRCLE[1]) <= dist(i[0], i[1], PREV_CIRCLE[0],
                                                                                          PREV_CIRCLE[1]):
                        chosen = i
            cv.circle(f, (chosen[0], chosen[1]), 1, (0, 100, 100), 3)
            cv.circle(f, (chosen[0], chosen[1]), chosen[2], (255, 0, 255), 3)
            PREV_CIRCLE = chosen

        cv.imshow("circles", f)


if __name__ == "__main__":
    video_capture = cv.VideoCapture(0)

    prev_circle = None
    dist = lambda x1, y1, x2, y2: (x1-x2)**2 + (y1-y2)**2

    s = Scope()
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        # cv.imshow("frame", frame)

        # gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # blur_frame = cv.GaussianBlur(gray_frame, (17, 17), 0) # larger numbers in tuple (has to be odd) - more blur
        # cv.imshow('blur_frame', blur_frame)

        res = s.hsv(frame)
        # s.find_circles(res, frame)

        gray_frame = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
        s.find_circles(gray_frame, gray_frame)

        # cv2.imshow("res", gray_frame)

        if cv.waitKey(1) & 0xFF == ord("q"):
            break
    video_capture.release()
    cv2.destroyAllWindows()
