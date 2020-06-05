import cv2
import numpy as np
from datetime import datetime

# f = open("pos1.txt", "a")
# f = open("pos2.txt", "a")
# f = open("pos3.txt", "a")
# f = open("pos4.txt", "a")
# f = open("pos5.txt", "a")
f = open("gen_pos_new_4.txt", "a")


def changePos(x):
  if x >300 and x <= 380:
    return 'POS_2'
  elif x >400 and x <= 490:
    return 'POS_1'
  elif x >= 130 and x <= 200:
    return 'POS_4'
  elif x >= 210 and x < 300:
    return 'POS_3'

  elif x >= 40 and x < 100:
    return 'POS_5'
  else:
    return None, x

def changeColor(color):
  if color == (0, 255, 0):
    return 'VERDE'
  elif color == (0, 0, 255):
    return 'RED'
  elif color == (255, 0, 0):
    return 'BLUE'
  elif color == (25, 221, 185):
    return 'VERDE_BLUE'
  else:
    return None

def dibujar(mask,color):

  contornos,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  for c in contornos:
    area = cv2.contourArea(c)
    if area > 1000 and area < 30000:
      M = cv2.moments(c)
      if (M["m00"]==0): M["m00"]=1
      x = int(M["m10"]/M["m00"])
      y = int(M['m01']/M['m00'])

      # pos1 330 +-30
      # pos2 420 +-30
      # pos3 260 +-20
      # pos4 160 +-20
      # pos5 50 +-20

      nuevoContorno = cv2.convexHull(c)


      if y < 300:
        now = datetime.now()
        # print('X: {} and Y: {} and Color: {} and Time: {}'.format(x, y, changeColor(color), now.time()))
        f.write('POS: {}  and Color: {} and Time: {}'.format(changePos(x), changeColor(color), now.time()) + '\n')
        cv2.circle(frame,(x,y),7,(0,0,0),-1)
        cv2.putText(frame,'{},{}'.format(x,y),(x+10,y), font, 0.75,(255,255,255),1,cv2.LINE_AA)
        cv2.drawContours(frame, [nuevoContorno], 0, color, 3)

        tempImg= nuevoContorno

        colors, count = np.unique(tempImg.reshape(-1, tempImg.shape[-1]), axis=0, return_counts=True)
        # print(colors, count)
        # print(colors[np.argsort(-count)][:1])

cap = cv2.VideoCapture(0)
blanco = np.array([0, 0, 100], np.uint8)

verdeAzulBajo= np.array([81, 38, 84], np.uint8)
verdeAzulAlto= np.array([158, 199, 205], np.uint8)
verdeBajo = np.array([36, 100, 20], np.uint8)
verdeAlto = np.array([70, 255, 255], np.uint8)
azulBajo = np.array([93,143,134],np.uint8)
azulAlto = np.array([198,255,255],np.uint8)
# amarilloBajo = np.array([15,100,20],np.uint8)
# amarilloAlto = np.array([45,255,255],np.uint8)
redBajo1 = np.array([0,100,20],np.uint8)
redAlto1 = np.array([5,255,255],np.uint8)
redBajo2 = np.array([175,100,20],np.uint8)
redAlto2 = np.array([179,255,255],np.uint8)
font = cv2.FONT_HERSHEY_SIMPLEX
while True:
  ret,frame = cap.read()
  if ret == True:
    frameHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    maskBlanco = cv2.inRange(frameHSV, blanco, blanco)
    maskVerdeAzul = cv2.inRange(frameHSV, verdeAzulBajo, verdeAzulAlto)
    maskVerde = cv2.inRange(frameHSV, verdeBajo, verdeAlto)
    maskAzul = cv2.inRange(frameHSV,azulBajo,azulAlto)
    # maskAmarillo = cv2.inRange(frameHSV,amarilloBajo,amarilloAlto)
    maskRed1 = cv2.inRange(frameHSV,redBajo1,redAlto1)
    maskRed2 = cv2.inRange(frameHSV,redBajo2,redAlto2)
    maskRed = cv2.add(maskRed1,maskRed2)
    # dibujar(maskBlanco, (255, 255, 255))
    dibujar(maskVerde, (0, 255, 0))
    dibujar(maskAzul,(255,0,0))
    dibujar(maskVerdeAzul, (25, 221, 185))
    # dibujar(maskAmarillo,(0,255,255))
    dibujar(maskRed,(0,0,255))
    # cv2.imshow('maskVerde', maskVerde)
    # cv2.imshow('maskAzul', maskAzul)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('s'):
      break
cap.release()
cv2.destroyAllWindows()
f.close()