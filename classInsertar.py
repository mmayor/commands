import json

import requests


class ConsultaInsert(object):
    def __init__(self, user, idMotor, data):

        super().__init__()
        self.__user= user
        self.__motorId= idMotor
        self.__data= data
        self.__statusCode= None



    def getStatusCode(self):
        return self.__statusCode

    def ranDom(self):

        tempCorriente = []
        tempVoltaje = []
        tempVoltajeOther = []
        tempFrecuenciaOther = []
        tempFrecuenciaTeoricaOther = []
        tempCorrienteOther = []
        tempResistenciaOther = []
        tempRuido = []
        tempVibracion = []
        stCorriente = ""
        stVoltaje = ""
        stRuido = ""
        stVibracion = ""

        tempALL = self.__data
        tempVoltajeOther = tempALL[0]
        tempFrecuenciaOther = tempALL[1]
        tempCorrienteOther = tempALL[2]
        tempResistenciaOther = tempALL[3]
        tempFrecuenciaTeoricaOther = tempALL[4]

        if (float(tempCorrienteOther[6]) >= 0.01 and float(tempCorrienteOther[6]) <= 0.03) or (
                float(tempCorrienteOther[7]) >= 0.01 and float(tempCorrienteOther[7]) <= 0.03):
            statusCorriente = "GOOD"
        else:
            statusCorriente = "BAD"

        if (float(tempResistenciaOther[6]) >= 4.0 and float(tempResistenciaOther[6]) <= 5.0) or (
                float(tempResistenciaOther[7]) >= 4.0 and float(tempResistenciaOther[7]) <= 5.0):
            statusRuido = "GOOD"
        else:
            statusRuido = "BAD"

        '''
        if (float(tempFrecuenciaTeoricaOther[7]) >= 4.0 and float(tempResistenciaOther[7]) <= 5.0) or (float(tempResistenciaOther[8]) >= 4.0 and float(tempResistenciaOther[8]) <= 5.0):
            statusRuido = "GOOD"
        else:
            statusRuido = "BAD"

        '''

        '''
        statusNumber = random.randrange(0,2)
        if statusNumber == 0:
            status = 'GOOD'
        else:
            status = 'BAD'
        '''

        statusVoltaje = "GOOD"
        # statusRuido = validarStatus(tempRuido, 1)
        statusVibracion = "GOOD"
        statusVibracionTeorica = "GOOD"

        if statusVoltaje == "GOOD" and statusCorriente == "GOOD" and statusRuido == "GOOD" and statusVibracion == "GOOD":
            status = "GOOD"
        else:
            status = "BAD"

        stCorriente = ','.join(tempCorriente)
        stVoltaje = ','.join(tempVoltaje)
        stRuido = ','.join(tempRuido)
        stVibracion = ','.join(tempVibracion)

        stVoltajeOther = ','.join(tempVoltajeOther)
        stFrecuenciaOther = ','.join(tempFrecuenciaOther)
        stFrecuenciaTeoricaOther = ','.join(tempFrecuenciaTeoricaOther)
        stCorrienteOther = ','.join(tempCorrienteOther)
        stResistenciaOther = ','.join(tempResistenciaOther)

        print(tempCorrienteOther)
        print(tempALL)

        return tempCorriente, tempVoltaje, tempVibracion, tempVoltaje, status, stCorrienteOther, stVoltajeOther,\
               stResistenciaOther, stFrecuenciaOther, status, statusCorriente, statusVoltaje, statusRuido, \
               statusVibracion, stFrecuenciaTeoricaOther, statusVibracionTeorica

    def insertData(self):



        # statusNew = "GOOD"
        # statusNew = "BAD"
        # id = scanIDMotor()
        # tempMotor = None
        # body = request.get_json()

        # tempMotorNew = scanIDMotor()

        # tempMotorNew = cam.camIdMotor()
        # global waitTime
        # waitTime = tempMotorNew
        # print(waitTime)
        # tempMotor = db.session.query(Motor).filter(Motor.serial == body["motor_id"]).first()
        # tempMotor = db.session.query(Motor).filter(Motor.serial == tempMotorNew).first()
        # tempUser = db.session.query(User).filter(User.username == body["user_id"]).first()
        # tempUser = body["user_id"]
        tempVariables = self.ranDom()

        # URL = "https://3000-cafdb876-64bf-48b9-b2f1-4cafa3ff31ef.ws-us02.gitpod.io/hello"
        # PARAMS = {"send":"OK"}
        # r = requests.get(url=URL)
        # data = r.json()
        # c = httplib2.HTTPS("https://3000-cafdb876-64bf-48b9-b2f1-4cafa3ff31ef.ws-us02.gitpod.io/add_testNew")

        headerNew = {"content-type": "aplication/json"}
        apiEndPoint = "https://3000-cafdb876-64bf-48b9-b2f1-4cafa3ff31ef.ws-us02.gitpod.io/add_testNewNew"

        data = {
            "IdMotor": self.__motorId,
            "IdUser": self.__user,
            "tempVariables": tempVariables
        }

        dataNew = {
            "idMotor": "10",
            "idUser": "pepe"
        }

        r = requests.post(url=apiEndPoint, data=json.dumps(data), headers=headerNew)

        # print("CODE_STATUS", r.status_code)
        self.__statusCode= r.status_code
        pastebin_url = r.text

        # test1 = Test(voltaje=body["voltaje"], corriente=body["corriente"], ruido=body["ruido"], vibracion=body["vibracion"], motor_id=body["motor_id"], user_id=tempUser.id, status=body["status"])
        # test1 = Test(voltaje=tempVariables[6], corriente=tempVariables[5], ruido=tempVariables[7], vibracion=tempVariables[8], motor_id=tempMotor, user_id=tempUser.id,
        # status=tempVariables[9], statusCorriente=tempVariables[10], statusVoltaje=tempVariables[11], statusRuido=tempVariables[12], statusVibracion=tempVariables[13])


        # db.session.commit()
        return "ok", 200