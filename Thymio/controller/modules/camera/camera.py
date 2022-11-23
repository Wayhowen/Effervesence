import cv2
import cv2 as cv
import numpy as np
from picamera import PiCamera

#Red
#LOWER_YELLOW = (0, 40, 230)
#UPPER_YELLOW = (30, 255, 255)
#Blue
LOWER_YELLOW = (120, 40, 230)
UPPER_YELLOW = (150, 255, 255)

PREV_CIRCLE = None
PREV_FRAME = None

# statistical significance - explains that if we done something enough then it isnt a coincidence , if chance
# is below 5% then we have this significance most likely

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

    def edge_detection(self, img):
        # Convert to graycsale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur the image for better edge detection
        img_blur = cv2.GaussianBlur(img_gray, (3,3), 0) 

        # Canny Edge Detection
        edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)
        return edges
    
    def movement_detection(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        ret,gray = cv2.threshold(gray,200,255,0)
        
        # if the first frame is None, initialize it
        global PREV_FRAME
        posX = None
        if PREV_FRAME is not None:
            frameDelta = cv2.absdiff(PREV_FRAME, gray)
            thresh = cv2.threshold(frameDelta, 15, 255, cv2.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            contours_sizes = [(cv2.contourArea(cnt), cnt) for cnt in cnts]
            if contours_sizes:
                c = max(contours_sizes, key=lambda x: x[0])[1]
           
                # if the contour is too small, ignore it
                if cv2.contourArea(c) > 500:
                    
                    # compute the bounding box for the contour, draw it on the frame,
                    # and update the text
                    (x, y, w, h) = cv2.boundingRect(c)
                    #print(x+w/2, y+h/2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    posX = (x+w/2)
        
        PREV_FRAME = gray
        return posX


    def find_circles(self, bf, f):
        global PREV_CIRCLE
        circles = cv.HoughCircles(bf, cv.HOUGH_GRADIENT, 1.2, 45, param1=75, param2=40, minRadius=0,
                                  maxRadius=300)
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

        #cv.imshow("circles", f)


if __name__ == "__main__":
    #video_capture = cv.VideoCapture(0)
    camera = PiCamera()

    prev_circle = None
    dist = lambda x1, y1, x2, y2: (x1-x2)**2 + (y1-y2)**2

    s = Scope()
    print("Starting capture")
    while True:
        width = 640
        height = 480

        camera.resolution = (width,height)
        camera.framerate = 24
        image = np.empty((height,width,3), dtype=np.uint8)
        camera.capture(image,'bgr')
        frame = cv2.rotate(image, cv2.ROTATE_180)
        #ret, frame = video_capture.read()
        #if not ret:
        #    break
        
        pos = s.movement_detection(frame)

        #cv.imshow("frame", frame)

        if pos:
            print(pos)
        
        #gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        #blur_frame = cv.GaussianBlur(gray_frame, (17, 17), 0) # larger numbers in tuple (has to be odd) - more blur
        #cv.imshow('blur_frame', blur_frame)
        

        #res = s.hsv(frame)
        #s.find_circles(res, frame)

        #gray_frame = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
        #blur_frame = cv.GaussianBlur(gray_frame, (17, 17), 0)  # larger numbers in tuple (has to be odd) - more blur
        #s.find_circles(blur_frame, blur_frame)

        #cv2.imshow("res", gray_frame)

        if cv.waitKey(1) & 0xFF == ord("q"):
            break
    #video_capture.release()
    cv2.destroyAllWindows()
