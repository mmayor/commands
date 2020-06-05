import cv2
import numpy as np
import pytesseract
import argparse
import time
from scipy import ndimage
from matplotlib.pyplot import gray
from pytesseract import Output
from imutils.video import VideoStream
import os
import re

from scipy.ndimage.filters import convolve

BINARY_THREHOLD = 180
kernel_size=5
sigma=1
lowthreshold=0.05
highthreshold=0.15
weak_pixel=75
strong_pixel=255

def camIdMotor():

    font = cv2.FONT_HERSHEY_SIMPLEX

    def image_smoothening(img):
        ret1, th1 = cv2.threshold(img, BINARY_THREHOLD, 255, cv2.THRESH_BINARY)
        ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        blur = cv2.GaussianBlur(th2, (1, 1), 0)
        ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return th3

    def remove_noise_and_smooth(img):
        print('Removing noise and smoothening image')
        # img = cv2.imread(file_name, 0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered = cv2.adaptiveThreshold(gray.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41, 3)
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        img = image_smoothening(gray)
        or_image = cv2.bitwise_or(gray, closing)
        return or_image

    def gaussian_kernel(size, sigma=1):
        size = int(size) // 2
        x, y = np.mgrid[-size:size + 1, -size:size + 1]
        normal = 1 / (2.0 * np.pi * sigma ** 2)
        g = np.exp(-((x ** 2 + y ** 2) / (2.0 * sigma ** 2))) * normal
        return g

    def sobel_filters(img):
        Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
        Ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], np.float32)

        Ix = ndimage.filters.convolve(img, Kx)
        Iy = ndimage.filters.convolve(img, Ky)

        G = np.hypot(Ix, Iy)
        G = G / G.max() * 255
        theta = np.arctan2(Iy, Ix)
        return (G, theta)

    def non_max_suppression(img, D):
        M, N = img.shape
        Z = np.zeros((M, N), dtype=np.int32)
        angle = D * 180. / np.pi
        angle[angle < 0] += 180

        for i in range(1, M - 1):
            for j in range(1, N - 1):
                try:
                    q = 255
                    r = 255

                    # angle 0
                    if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                        q = img[i, j + 1]
                        r = img[i, j - 1]
                    # angle 45
                    elif (22.5 <= angle[i, j] < 67.5):
                        q = img[i + 1, j - 1]
                        r = img[i - 1, j + 1]
                    # angle 90
                    elif (67.5 <= angle[i, j] < 112.5):
                        q = img[i + 1, j]
                        r = img[i - 1, j]
                    # angle 135
                    elif (112.5 <= angle[i, j] < 157.5):
                        q = img[i - 1, j - 1]
                        r = img[i + 1, j + 1]

                    if (img[i, j] >= q) and (img[i, j] >= r):
                        Z[i, j] = img[i, j]
                    else:
                        Z[i, j] = 0


                except IndexError as e:
                    pass

        return Z

    def threshold(img):

        highThreshold = img.max() * highthreshold
        lowThreshold = highThreshold * lowthreshold

        M, N = img.shape
        res = np.zeros((M, N), dtype=np.int32)

        weak = np.int32(weak_pixel)
        strong = np.int32(strong_pixel)

        strong_i, strong_j = np.where(img >= highThreshold)
        zeros_i, zeros_j = np.where(img < lowThreshold)

        weak_i, weak_j = np.where((img <= highThreshold) & (img >= lowThreshold))

        res[strong_i, strong_j] = strong
        res[weak_i, weak_j] = weak

        return (res)

    def hysteresis(self, img):

        M, N = img.shape
        weak = self.weak_pixel
        strong = self.strong_pixel

        for i in range(1, M - 1):
            for j in range(1, N - 1):
                if (img[i, j] == weak):
                    try:
                        if ((img[i + 1, j - 1] == strong) or (img[i + 1, j] == strong) or (img[i + 1, j + 1] == strong)
                                or (img[i, j - 1] == strong) or (img[i, j + 1] == strong)
                                or (img[i - 1, j - 1] == strong) or (img[i - 1, j] == strong) or (
                                        img[i - 1, j + 1] == strong)):
                            img[i, j] = strong
                        else:
                            img[i, j] = 0
                    except IndexError as e:
                        pass

        return img

    def hysteresis(img):

        M, N = img.shape
        weak = weak_pixel
        strong = strong_pixel

        for i in range(1, M - 1):
            for j in range(1, N - 1):
                if (img[i, j] == weak):
                    try:
                        if ((img[i + 1, j - 1] == strong) or (img[i + 1, j] == strong) or (img[i + 1, j + 1] == strong)
                                or (img[i, j - 1] == strong) or (img[i, j + 1] == strong)
                                or (img[i - 1, j - 1] == strong) or (img[i - 1, j] == strong) or (
                                        img[i - 1, j + 1] == strong)):
                            img[i, j] = strong
                        else:
                            img[i, j] = 0
                    except IndexError as e:
                        pass

        return img


    def detectarPlaca(img):


        ##TESTING
        # blurred_image = gaussian_blur(image, kernel_size=9, verbose=False)



        # img_smoothed = convolve(img, gaussian_kernel(kernel_size, sigma))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # gradientMat, thetaMat = sobel_filters(img_smoothed)
        # nonMaxImg = non_max_suppression(gradientMat, thetaMat)
        # thresholdImg = threshold(nonMaxImg)
        # img_final = hysteresis(thresholdImg)

        # imgNoise = remove_noise_and_smooth(img)
        # grayNew= unsharp_mask(img)
        # im_resized(img, dpi=(300, 300))  # best for OCR
        # img = cv2.resize(img, (300, 300))
        # img = cv2.medianBlur(img, 5)


        # gray = cv2.blur(gray, (5, 5))
        # gray= cv2.medianBlur(gray, 5)
        # gray= img.gaussian_kernel(5)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # ret, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # ret, thresh2 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        # ret, thresh3 = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)
        # ret, thresh4 = cv2.threshold(gray, 127, 255, cv2.THRESH_TOZERO)
        # ret, thresh5 = cv2.threshold(gray, 127, 255, cv2.THRESH_TOZERO_INV)

        ## OTHER
        # th2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        # th3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # ret3, th3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)



        canny = cv2.Canny(gray, 50, 150)
        # kernel = np.ones((5, 5), np.uint8)

        canny = cv2.dilate(canny, None, iterations=2)
        # canny = cv2.erode(canny, None, iterations=1)
        kernel = np.ones((5, 5), np.uint8)

        # canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, None)
        # canny = cv2.morphologyEx(canny, cv2.MORPH_GRADIENT,None)
        # canny = cv2.dilate(canny, None, iterations=2)
        # canny= cv2.bitwise_not(canny)
        # canny = cv2.erode(canny, kernel, iterations=1)

        return canny

    def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        """Return a sharpened version of the image, using an unsharp mask."""
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened

    def binarizacion(img):
        # img = cv2.imread('gradient.png', 0)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        ret, thresh2 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        ret, thresh3 = cv2.threshold(img, 127, 255, cv2.THRESH_TRUNC)
        ret, thresh4 = cv2.threshold(img, 127, 255, cv2.THRESH_TOZERO)
        ret, thresh5 = cv2.threshold(img, 127, 255, cv2.THRESH_TOZERO_INV)
        # titles = ['Original Image', 'BINARY', 'BINARY_INV', 'TRUNC', 'TOZERO', 'TOZERO_INV']
        # images = [img, thresh1, thresh2, thresh3, thresh4, thresh5]
        return thresh5




    def conTornos(src):

        # gris = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        # Aplicar suavizado Gaussiano
        # gauss = cv2.GaussianBlur(gris, (5, 5), 0)
        # canny = cv2.Canny(gauss, 50, 150)

       # imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        # im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        # gray = cv2.GaussianBlur(gray, (7, 7), 3)

        # t, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE)

        # gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        # _, th = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        # canny = cv2.Canny(th, 50, 150)
        # img1, contornos1, hierarchy1 = cv2.findContours(th, cv2.RETR_EXTERNAL,
        #                                                cv2.CHAIN_APPROX_NONE)
        # img2, contornos2, hierarchy2 = cv2.findContours(th, cv2.RETR_EXTERNAL,
        #                                                cv2.CHAIN_APPROX_SIMPLE)
        # contornos1, hierarchy1 = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        # gray = cv2.blur(gray, (3, 3))
        gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Blur to reduce noise
        th3 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                    cv2.THRESH_BINARY, 11, 2)
        canny = cv2.Canny(gray, 150, 200)
        # canny = cv2.dilate(canny, None, iterations=1)
        canny = cv2.morphologyEx(canny, cv2.MORPH_OPEN, None)

        return canny

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

        return th2

    def rescalingNew(imgNew):
        img = cv2.resize(imgNew, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # kernel = np.ones((1, 1), np.uint8)
        # img = cv2.dilate(img, kernel, iterations=1)
        # img = cv2.erode(img, kernel, iterations=1)
        # cv2.threshold(cv2.bilateralFilter(img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # cv2.adaptiveThreshold(cv2.bilateralFilter(img, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                       cv2.THRESH_BINARY, 31, 2)
        cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

        return img

    def maskNew(img):
        frame = cv2.resize(img,(400, 300), interpolation=cv2.INTER_CUBIC)
        hsv=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lowerBlue = np.array([100,50,50])
        upperBlue = np.array([130, 255, 255])# cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

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
        return  cv2.addWeighted(img, 1.5, np.zeros(img.shape, img.dtype), 0, 0)

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
           img= cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
           ret, thresh2 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
           # Aplicar suavizado Gaussiano
           gauss = cv2.GaussianBlur(thresh2, (5, 5), 0)
           # canny = cv2.Canny(gauss, 100, 200)
           # canny= auto_canny(img)
           return gauss

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

    def auto_canny(image, sigma=0.33):
        # compute the median of the single channel pixel intensities
        v = np.median(image)
        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(image, lower, upper)
        # return the edged image
        return edged

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
        vs = VideoStream(src=0).start()
        # vs = cv2.VideoCapture(0)
        time.sleep(2.0)

    # otherwise, load the video
    else:
        vs = cv2.VideoCapture(args["video"])

    # keep looping over the frames
    while True:

        # check to see if we have reached the end of the
        # video
        # time.sleep(2.0)
        frame = vs.read()
        frame = frame[1] if args.get("video", False) else frame

        if frame is None:
            break

        # length = int(vs.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        # width = int(vs.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        # height = int(vs.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
        # fps = vs.get(cv2.cv.CV_CAP_PROP_FPS)
        # grab the current frame and then handle if the frame is returned
        # from either the 'VideoCapture' or 'VideoStream' object,
        # respectively

        # frame = thresholding(frame)
        # frame =  opening(frame)
        # frame = canny(frame)

        # frame = canny(frameOriginal)
        # frameModificado = get_grayscale(frame)
        # frameModificado = binarizacion(frame)
        frameModificado= detectarPlaca(frame)
        # frame= image_smoothening(frame)
        # frame= auto_canny(frame)

        # frame = sobel(frame)
        # frame = laplacian(frame)
        # frame = umbralChangeBack(frame)
        # frame = detectaCode(frame)

        # frame = get_grayscale(frame)
        # frame = thresHolding(frame)
        # frame = maskNew1(frame)

        # frame = contrast(frame)
        # frame = conTornos(frame)
        # frame = maskNew1(frame)
        # frame= rescalingNew(frame)

        # contornos1,hierarchy1 = cv2.findContours(frameOriginal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        cnts, _ = cv2.findContours(frameModificado, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # OpenCV 4

        # print('Número de contornos encontrados: ', len(cnts))

        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1500 and area < 6000:
                # print(area)
                # nuevoContorno = cv2.convexHull(c)

                perimeter = cv2.arcLength(c, True)
                epsilon = 0.1 * cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, epsilon, True)
                hull = cv2.convexHull(c)

                M = cv2.moments(c)
                if (M["m00"] == 0): M["m00"] = 1
                x = int(M["m10"] / M["m00"])
                y = int(M['m01'] / M['m00'])


                cv2.drawContours(frame, [approx], 0, (255,0,0), 3)
                # cv2.drawContours(frame, c, -1, (0, 0, 255), 3)
                # Dibujar el centro
                cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
                # cv2.drawContours(frame, cnts, -1, (0, 255, 0), 2)
                # epsilon = 0.01 * cv2.arcLength(c, True)
                # approx = cv2.approxPolyDP(c, epsilon, True)
                # print(len(approx))
                # x, y, w, h = cv2.boundingRect(approx)
                # print('AREA', x, y, w, h)
                # placa = frameModificado[y:y + h, x:x + w]
                # textNew = pytesseract.image_to_string(placa, config='--psm 11')
                # print('PLACA: ', textNew)
                # textCycle = pytesseract.image_to_string([nuevoContorno], config='--psm 11')
                # print(textCycle)

        custom_oem_psm_config = r'--oem 3 --psm 6'
        # config = '--psm 11'
        d = pytesseract.image_to_data(frameModificado, output_type=Output.DICT, config=custom_oem_psm_config)
        #print(d.keys())
        print(d['text'])

        ## EXAMPLE
        text = pytesseract.image_to_string(frameModificado, config=custom_oem_psm_config)
        # print("Detected Number is:", text)

        x= 0
        y= 0
        n_boxes = len(d['text'])
        for i in range(n_boxes):
             if int(d['conf'][i]) > 60:
                 (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])

                 frameModificado = cv2.rectangle(frameModificado, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frameModificado, '{}'.format(d['text']), (x-60, y + 160), font, 1.00, (0, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow('Frame', frame)
        cv2.imshow('Frame_Modificado', frameModificado)
        # cv2.imshow("Frame_Original", frameOriginal)


        # Salir con 'ESC'


        patronNew = re.compile('^FKI[0-9][0-9][0-9][0-9][0-9]')

        tempLength = d['text']


        print(len(d['text']))


        for t in d['text']:
            findText = re.search(patronNew, t, flags=0)
            # print("Iteracion: " + t)
            if findText:
                print("Detected Number is:", findText.group(0))
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

camIdMotor()