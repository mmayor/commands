# Algoritmo de deteccion de colores
# Por Glar3
# www.robologs.net
# Detecta objetos verdes y amarillos

import cv2
import numpy as np

# Iniciar la camara
captura = cv2.VideoCapture(2)

while (1):

    # Capturamos una imagen y la convertimos de RGB -> HSV
    _, imagen = captura.read()
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Rango de colores detectados:
    # Verdes:
    verde_bajos = np.array([49, 50, 50], dtype=np.uint8)
    # verde_altos = np.array([255, 253, 254], dtype=np.uint8)
    verde_altos = np.array([100, 255, 210], dtype=np.uint8)
    # Amarillos:
    amarillo_bajos = np.array([16, 76, 72], dtype=np.uint8)
    amarillo_altos = np.array([30, 255, 210], dtype=np.uint8)

    # Detectar los pixeles de la imagen que esten dentro del rango de verdes
    mascara_verde = cv2.inRange(hsv, verde_bajos, verde_altos)

    # Detectar los pixeles de la imagen que esten dentro del rango de amarillos
    mascara_amarillo = cv2.inRange(hsv, amarillo_bajos, amarillo_altos)

    # Filtrar el ruido aplicando un OPEN seguido de un CLOSE
    kernel = np.ones((6, 6), np.uint8)
    mascara_verde = cv2.morphologyEx(mascara_verde, cv2.MORPH_CLOSE, kernel)
    mascara_verde = cv2.morphologyEx(mascara_verde, cv2.MORPH_OPEN, kernel)
    # mascara_amarillo = cv2.morphologyEx(mascara_amarillo, cv2.MORPH_CLOSE, kernel)
    # mascara_amarillo = cv2.morphologyEx(mascara_amarillo, cv2.MORPH_OPEN, kernel)

    # Unir las dos mascaras con el comando cv2.add()
    mask = cv2.add(mascara_amarillo, mascara_verde)
    print('Mascar Verde: ', mascara_verde)
    print(print('Mascara Amarillo: '), mascara_amarillo)

    # Mostrar la imagen de la webcam y la mascara
    cv2.imshow('mask', mask)
    cv2.imshow('Camara', imagen)
    tecla = cv2.waitKey(5) & 0xFF
    if tecla == 27:
        break

cv2.destroyAllWindows()