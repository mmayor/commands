import cv2
import numpy as np
import pytesseract
import argparse
import time
from pytesseract import Output
from imutils.video import VideoStream
import os
import re





class ScanComplete():

    def __init__(self):

        super().__init__()
        # self.__text = str(text)
        self.__index = 0
        self.__data= ''
        self.__found= ''
        self.__foundFlag= False

        # self.textEdit.setText(self.__text
        # self.updateUi()

    def getFound(self):
        return self.__found

    def getData(self):
        return self.__data

    def getFoundFlag(self):
        return self.__foundFlag


    def camIdMotor(self):


        def conTornos(img):
            imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(imgray, 127, 255, 0)
            im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            return im2

        def maskNew2(img):

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # grayscale
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)  # threshold
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
            dilated = cv2.dilate(thresh, kernel, iterations=13)  # dilate

            return dilated

        def maskNew1(img):
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #canny = cv2.Canny(gray_img, 100, 200)
            # gray_img = canny
            ret1, th1 = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)

            # th3 = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            # global thresholding
            ret1, th1 = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)

            # Otsu's thresholding
            ret2, th2 = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Otsu's thresholding after Gaussian filtering
            blur = cv2.GaussianBlur(gray_img, (5, 5), 0)
            ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            ##other
            ret, thresh1 = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)
            ret, thresh2 = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY_INV)
            ret, thresh3 = cv2.threshold(gray_img, 127, 255, cv2.THRESH_TRUNC)
            ret, thresh4 = cv2.threshold(gray_img, 127, 255, cv2.THRESH_TOZERO)
            ret, thresh5 = cv2.threshold(gray_img, 127, 255, cv2.THRESH_TOZERO_INV)


            return th3

        def maskNew(img):
            frame = cv2.resize(img,(400, 300), interpolation=cv2.INTER_CUBIC)
            hsv=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lowerBlue = np.array([100,50,50])
            upperBlue = np.array([130, 255, 255])

            mask = cv2.inRange(hsv, lowerBlue, upperBlue)
            return mask

        def detectaCode(img):
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray_img = cv2.bitwise_not(gray_img)
            return gray_img


        def umbralChangeBack(img):
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            img_contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
            img_contours = sorted(img_contours, key=cv2.contourArea)

            for i in img_contours:

                if cv2.contourArea(i) > 100:
                    break

            mask = np.zeros(img.shape[:2], np.uint8)
            cv2.drawContours(mask, [i], -1, 255, -1)
            new_img = cv2.bitwise_and(img, img, mask=mask)
            return new_img

        def contrast(img):
            return  cv2.addWeighted(img, 3.5, np.zeros(img.shape, img.dtype), 0, 0)

        def focusing(val):
            value = (val << 4) & 0x3ff0
            data1 = (value >> 8) & 0x3f
            data2 = value & 0xf0
            os.system("i2cset -y 0 0x0c %d %d" % (data1, data2))


        def sobel(img):
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_sobel = cv2.Sobel(img_gray, cv2.CV_16U, 1, 1)
            return cv2.mean(img_sobel)[0]


        def laplacian(img):
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_sobel = cv2.Laplacian(img_gray, cv2.CV_16U)
            return cv2.mean(img_sobel)[0]


        # get grayscale image
        def get_grayscale(image):
               return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


        def get_grayscaleNEW(image):
            return cv2.bilateralFilter(image, 11, 17, 17)


        # noise removal
        def remove_noise(image):
              return cv2.medianBlur(image, 5)


        # thresholding
        def thresholding(image):
              return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        def thresHolding(img):
            return cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)


        # dilation
        def dilate(image):
              kernel = np.ones((5, 5), np.uint8)
              return cv2.dilate(image, kernel, iterations=1)


        # erosion
        def erode(image):
             kernel = np.ones((5, 5), np.uint8)
             return cv2.erode(image, kernel, iterations=1)


        # opening - erosion followed by dilation
        def opening(image):
              kernel = np.ones((5, 5), np.uint8)
              return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


        # canny edge detection
        def canny(image):
              return cv2.Canny(image, 100, 200)




        # skew correction
        def deskew(image):
            coords = np.column_stack(np.where(image > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)

            else:
                angle = -angle
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated


        # template matching
        def match_template(image, template):
            return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)


        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video",
            help="path to the (optional) video file")
        args = vars(ap.parse_args())

        # if the video path was not supplied, grab the reference to the
        # camera
        if not args.get("video", False):
            vs = VideoStream(src=2).start()
            time.sleep(2.0)

        # otherwise, load the video
        else:
            vs = cv2.VideoCapture(args["video"])



        # keep looping over the frames
        while True:



            # check to see if we have reached the end of the
            # video

            frame = vs.read()
            frame = frame[1] if args.get("video", False) else frame





            if frame is None:
                break

            # grab the current frame and then handle if the frame is returned
            # from either the 'VideoCapture' or 'VideoStream' object,
            # respectively


            # frame = get_grayscale(frame)
            # frame = thresholding(frame)
            # frame =  opening(frame)
            # frame = canny(frame)
            # frame = get_grayscale(frame)
            # frame = sobel(frame)
            # frame = laplacian(frame)
            # frame = umbralChangeBack(frame)
            # frame = detectaCode(frame)
            # frame = contrast(frame)
            # frame = thresHolding(frame)
            # frame = maskNew1(frame)
            # frame = conTornos(frame)
            frame = maskNew1(frame)

            d = pytesseract.image_to_data(frame, output_type=Output.DICT)
            #print(d.keys())
            # print(d['text'])
            self.__data = d['text']
            print(self.__data)

            ## EXAMPLE
            text = pytesseract.image_to_string(frame, config='--psm 11')
            # print("Detected Number is:", text)


            n_boxes = len(d['text'])
            for i in range(n_boxes):
                 if int(d['conf'][i]) > 60:
                     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                     frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # cv2.imshow('Frame', frame)
            # Salir con 'ESC'




            patronNew = re.compile('^FKI[0-9][0-9][0-9][0-9][0-9]')

            tempLength = d['text']


            # print(len(d['text']))


            for t in d['text']:
                findText = re.search(patronNew, t, flags=0)
                # print("Iteracion: " + t)
                if findText:
                    print("Detected Number is:", findText.group(0))
                    self.__foundFlag= True
                    self.__found = findText.group(0)
                    break


            # findText = re.search(patronNew, text, flags=0)
            # print(findText.group(0))
            if findText:
                ## print("Detected Number is:", findText.group(0))
                break




            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break

        # if we are not using a video file, stop the video file stream
        if not args.get("video", False):
            vs.stop()

        # otherwise, release the camera pointer
        else:
            vs.release()



        # close all windows
        cv2.destroyAllWindows()
        # waitTime = findText.group(0)
        # print('waitTime: ' + waitTime)

        return findText.group(0)

    # camIdMotor()