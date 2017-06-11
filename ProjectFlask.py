from flask import Flask
from flask import render_template, request
import os
from DbClass import DbClass
from readSensor import readSensor
import RPi.GPIO as GPIO
import time

connection = DbClass()
sensor = readSensor()

knopBinnen = 26
knopBuiten = 19

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(21, GPIO.OUT)
GPIO.setup(knopBinnen, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(knopBuiten, GPIO.IN, pull_up_down=GPIO.PUD_UP)
servoDeur = GPIO.PWM(21, 50)
servoDeur.start(0)

isKnopGedruktVorig = 1
stand = 0

isKnopBuitenGedruktVorig = 1
standBuiten = 0

def openClose(number):
    global isKnopGedruktVorig, stand, isKnopBuitenGedruktVorig, standBuiten
    isKnopGedrukt = GPIO.input(knopBinnen)

    if GPIO.event_detected(knopBinnen):
        if (isKnopGedrukt != isKnopGedruktVorig):
            if (isKnopGedrukt == 0):
                if (stand == 0):
                    print("Gedrukt Binnen")
                    connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperatuur", "Deur manueel gesloten")
                    stand = 1
                    servoDeur.ChangeDutyCycle(7.5)  # turn towards 90 degree
                else:
                    print("Gedrukt Binnen 2")
                    connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperatuur", "Deur manueel geopend")
                    stand = 0
                    servoDeur.ChangeDutyCycle(12.5)  # turn towards 180 degree

        isKnopGedruktVorig = isKnopGedrukt
        time.sleep(0.0025)

    isKnopBuitenGedrukt = GPIO.input(knopBuiten)

    if GPIO.event_detected(knopBuiten):
        if (isKnopBuitenGedrukt != isKnopBuitenGedruktVorig):
            if (isKnopBuitenGedrukt == 0):
                if (standBuiten == 0):
                    print("Gedrukt Buiten ")
                    connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperatuur", "Deur manueel gesloten")
                    standBuiten = 1
                    servoDeur.ChangeDutyCycle(7.5)  # turn towards 90 degree

                else:
                    print("Gedrukt Buiten 2")
                    connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperatuur", "Deur manueel geopend")
                    standBuiten = 0
                    servoDeur.ChangeDutyCycle(12.5)  # turn towards 180 degree

        isKnopBuitenGedruktVorig = isKnopBuitenGedrukt
        time.sleep(0.0025)

@app.route('/')
def onboarding():
    return render_template('onboarding.html')

@app.route('/onboarding1',methods=['post'])
def onboarding1():
    name = request.form['inputName']
    email = request.form['inputEmail']
    password = request.form['inputPass']
    passwordRepeat = request.form['inputRepeatPass']
    signedIn = False

    if password == passwordRepeat:
        connection.setDataToDatabaseGebruikers(name, email, password)
        return render_template('onboarding1.html'), True
    else:
        return "Wachtwoorden komen niet overeen."

@app.route('/index')
def index_login():
    temp = sensor.print_temp()
    vocht = float(sensor.getAdc(0))
    return render_template('index.html', temperatuur=temp, vochtigheid=vocht)

@app.route('/index', methods=['post'])
def index():
    email = request.form['emailLogin']
    password = request.form['passwordLogin']
    data = connection.getDataFromDatabaseMetVoorwaarde(email, password)

    if data is None:
        return "Username or password is wrong"
    else:
        temp = sensor.print_temp()
        vocht = float(sensor.getAdc(0))
        return render_template('index.html', temperatuur=temp, vochtigheid=vocht)

@app.route('/rapporten')
def rapporten():
    # results = []
    results = connection.getDataFromDatabase()
    return render_template('rapporten.html', results=results)

@app.route('/instellingen')
def instellingen():
    return render_template('instellingen.html')

if __name__ == '__main__':
    GPIO.add_event_detect(knopBinnen,GPIO.FALLING,callback=openClose)
    GPIO.add_event_detect(knopBuiten, GPIO.FALLING, callback=openClose)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=False)


