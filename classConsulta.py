from PyQt5.QtCore import QObject
# from PyQt5.QtCore.QJsonValue import Object
import json
import requests


class ConsultaMotors(object):
    def __init__(self):

        super().__init__()


    def consultaMotors(self, id=None):

        print(id)
        if id is None or id=='':

            URL = "https://3000-cafdb876-64bf-48b9-b2f1-4cafa3ff31ef.ws-us02.gitpod.io/motor"
        else:
            URL = "https://3000-cafdb876-64bf-48b9-b2f1-4cafa3ff31ef.ws-us02.gitpod.io/motorId/" + id

        PARAMS = {"send": "OK"}
        r = requests.get(url=URL)
        data = r.json()
        # print(data)
        return data

    def consultaTests(self, id=None):

        if id is None or id=='':
            URL = "https://3000-cafdb876-64bf-48b9-b2f1-4cafa3ff31ef.ws-us02.gitpod.io/tests"
        else:
            URL = "https://3000-cafdb876-64bf-48b9-b2f1-4cafa3ff31ef.ws-us02.gitpod.io/motorId/"+ id

        PARAMS = {"send": "OK"}
        r = requests.get(url=URL)

        data = r.json()
        # print(data)
        return data

if __name__ == '__main__':
    tempConsulta= ConsultaMotors()
    tempConsulta.consultaMotors()
    tempConsulta.consultaTests()
