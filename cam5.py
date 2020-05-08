# Algoritmo de deteccion de colores
# Por Glar3
#
#
# Detecta objetos verdes, elimina el ruido y busca su centro

import cv2
import numpy as np

# Iniciamos la camara
captura = cv2.VideoCapture(2)

while (1):

    # Capturamos una imagen y la convertimos de RGB -> HSV
    _, imagen = captura.read()
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Establecemos el rango de colores que vamos a detectar
    # En este caso de verde oscuro a verde-azulado claro
    verde_bajos = np.array([49, 50, 50], dtype=np.uint8)
    verde_altos = np.array([80, 255, 255], dtype=np.uint8)

    rojos_bajos= np.array([132, 101, 50], dtype=np.uint8)
    rojos_altos= np.array([255, 255, 255], dtype=np.uint8)

    azules_bajos= np.array([38, 101, 131], dtype=np.uint8)
    azules_altos= np.array([160, 255, 255], dtype=np.uint8)

    # Crear una mascara con solo los pixeles dentro del rango de verdes
    maskVerdes = cv2.inRange(hsv, verde_bajos, verde_altos)
    maskRojos = cv2.inRange(hsv, rojos_bajos, rojos_altos)
    maskAzules = cv2.inRange(hsv, azules_bajos, azules_altos)

    # Encontrar el area de los objetos que detecta la camara Verde
    momentsVerdes = cv2.moments(maskVerdes)
    areaVerde = momentsVerdes['m00']

    # Encontrar el area de los objetos que detecta la camara RED
    momentsRojos = cv2.moments(maskRojos)
    areaRojos = momentsRojos['m00']

    # Encontrar el area de los objetos que detecta la camara RED
    momentsAzules = cv2.moments(maskAzules)
    areaAzules = momentsAzules['m00']

    # Descomentar para ver el area por pantalla
    print('Area Azules: ', areaAzules)
    if (areaAzules > 2000000):
        # Buscamos el centro x, y del objeto
        print('Encontrado Data Azul: ', areaAzules)
        xAzules = int(momentsAzules['m10'] / momentsAzules['m00'])
        yAzules = int(momentsRojos['m01'] / momentsAzules['m00'])

        # Mostramos sus coordenadas por pantalla
        print("x = ", xAzules)
        print("y = ", yAzules)

        # Dibujamos una marca en el centro del objeto
        cv2.rectangle(imagen, (xAzules, yAzules), (xAzules + 2, yAzules + 2), (26, 68, 210), 2)

    # Descomentar para ver el area por pantalla
    # print('Area: ', area)

    else:
        print('No Encontrada Area Azules')

    # Descomentar para ver el area por pantalla
    print('Area Rojas: ', areaRojos)
    if (areaRojos > 2000000):
        # Buscamos el centro x, y del objeto
        print('Encontrado Data Rojo: ', areaRojos)
        xRojos = int(momentsRojos['m10'] / momentsRojos['m00'])
        yRojos = int(momentsRojos['m01'] / momentsRojos['m00'])

        # Mostramos sus coordenadas por pantalla
        print("x = ", xRojos)
        print("y = ", yRojos)

        # Dibujamos una marca en el centro del objeto
        cv2.rectangle(imagen, (xRojos, yRojos), (xRojos + 2, yRojos + 2), (26, 68, 210), 2)

    # Descomentar para ver el area por pantalla
    # print('Area: ', area)

    else:
        print('No Encontrada Area Rojo')

    print('Area Verdes: ', areaVerde)
    if (areaVerde > 2000000):
        # Buscamos el centro x, y del objeto
        print('Encontrado Data Verde: ', areaVerde )
        xVerdes = int(momentsVerdes['m10'] / momentsVerdes['m00'])
        yVerdes = int(momentsVerdes['m01'] / momentsVerdes['m00'])

        # Mostramos sus coordenadas por pantalla
        print("x = ", xVerdes)
        print("y = ", yVerdes)


        # Dibujamos una marca en el centro del objeto
        cv2.rectangle(imagen, (xVerdes, yVerdes), (xVerdes + 2, yVerdes + 2), (0, 0, 255), 2)

    else:
        print('No Encontrada Area Verde')
    # Mostramos la imagen original con la marca del centro y
    # la mascara
    cv2.imshow('mask', maskRojos)
    cv2.imshow('Camara', imagen)
    tecla = cv2.waitKey(5) & 0xFF
    if tecla == 27:
        break
