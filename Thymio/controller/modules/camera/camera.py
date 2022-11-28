import cv2 as cv
import numpy as np
from picamera import PiCamera

width = 640
height = 480
COLORS = [
    ((0, 15, 190),
    (20, 255, 255),
    "Orangered"),
    ((90, 15, 200),
    (115, 255, 255),
    "Blue"),
    ((45, 15, 200),
    (90, 255, 255),
    "Green"),
    ((135, 15, 200),
    (170, 255, 255),
    "Purple"),
]
PREV_CIRCLE = None
PREV_FRAME = None

# statistical significance - explains that if we done something enough then it isnt a coincidence , if chance
# is below 5% then we have this significance most likely

class Scope:
    # TODO: might be useful https://mattmaulion.medium.com/color-image-segmentation-image-processing-4a04eca25c0
    def get_quadrant(self, pos):
        if (pos > width/3):
            return "l"
        elif (pos > width/2*3):
            return "m"
        else:
            return "r"
    
    def hsv(self, f, lower, upper):
        hsv = cv.cvtColor(f, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        thresholded_img = cv.bitwise_and(f, f, mask=mask)

        # erosion
        kernel = np.ones((3, 3), np.uint8)
        binary_img = cv.erode(thresholded_img, kernel, iterations=1)

        return binary_img

    def edge_detection(self, img):
        # Convert to graycsale
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # Blur the image for better edge detection
        img_blur = cv.GaussianBlur(img_gray, (3,3), 0) 

        # Canny Edge Detection
        edges = cv.Canny(image=img_blur, threshold1=100, threshold2=200)
        return edges
    
    def movement_detection(self, frame):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (21, 21), 0)
        ret,gray = cv.threshold(gray,200,255,0)
        
        # if the first frame is None, initialize it
        global PREV_FRAME
        posX = None
        if PREV_FRAME is not None:
            frameDelta = cv.absdiff(PREV_FRAME, gray)
            thresh = cv.threshold(frameDelta, 15, 255, cv.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh = cv.dilate(thresh, None, iterations=2)
            cnts, _ = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
                cv.CHAIN_APPROX_SIMPLE)
            contours_sizes = [(cv.contourArea(cnt), cnt) for cnt in cnts]
            if contours_sizes:
                c = max(contours_sizes, key=lambda x: x[0])[1]
           
                # if the contour is too small, ignore it
                if cv.contourArea(c) > 500:
                    
                    # compute the bounding box for the contour, draw it on the frame,
                    # and update the text
                    (x, y, w, h) = cv.boundingRect(c)
                    #print(x+w/2, y+h/2)
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    posX = (x+w/2)
        
        PREV_FRAME = gray
        return (self.get_quadrant(posX), None)

    def find_color(self, frame):
        biggest = None
        b_area = 0
        col = None
        for c in COLORS:
            res = s.hsv(frame, c[0], c[1])
            res = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
            contours,_ = cv.findContours(res, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
            if len(contours)>0:
                cont = max(contours, key = cv.contourArea)
                ar = cv.contourArea(cont)
                if ar < 100:
                    continue

                if ar > b_area:
                    biggest = cont
                    b_area = ar
                    col = c[2]
                    
        if b_area > 0:
            x,y,w,h = cv.boundingRect(biggest)
            cv.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            print(col)
            posX = (x+w/2)
            return (self.get_quadrant(posX), col)

        return None

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
    video_capture = cv.VideoCapture(0)
    camera = PiCamera()

    prev_circle = None
    dist = lambda x1, y1, x2, y2: (x1-x2)**2 + (y1-y2)**2

    s = Scope()
    print("Starting capture")
    while True:

        camera.resolution = (width,height)
        camera.framerate = 24
        image = np.empty((height,width,3), dtype=np.uint8)
        camera.capture(image,'bgr')
        frame = cv.rotate(image, cv.ROTATE_180)
        #ret, frame = video_capture.read()
        #if not ret:
        #    break
        
        #pos = s.movement_detection(frame)
        s.find_color(frame)
        #cv.imshow("frame", frame)
        
        #if pos:
        #    print(pos)
        
        #gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        #blur_frame = cv.GaussianBlur(gray_frame, (17, 17), 0) # larger numbers in tuple (has to be odd) - more blur
        #cv.imshow('blur_frame', blur_frame)
        
        #s.find_circles(res, frame)

        #gray_frame = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
        #blur_frame = cv.GaussianBlur(gray_frame, (17, 17), 0)  # larger numbers in tuple (has to be odd) - more blur
        #s.find_circles(blur_frame, blur_frame)

        #cv.imshow("res", res)

        if cv.waitKey(1) & 0xFF == ord("q"):
            break
    #video_capture.release()
    cv.destroyAllWindows()
