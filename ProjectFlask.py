from flask import Flask
from flask import render_template, request
import os
from DbClass import DbClass
from readSensor import readSensor
import RPi.GPIO as GPIO
import time
import schedule
from threading import Thread

app = Flask(__name__)

connection = DbClass()
sensor = readSensor()

knopBinnen = 26
knopBuiten = 19

loggedIn = False

condition = "closed"


def writeToDb():
    temp = sensor.print_temp()
    humidity = float(sensor.getAdc(0))
    connection.setDataToDatabaseMetingen(temp, 'temperature')
    connection.setDataToDatabaseMetingen(humidity, 'humidity')

def emptyDb():
    connection.truncateTable("Metingen")

def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led = 16
GPIO.setup(led, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(knopBinnen, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(knopBuiten, GPIO.IN, pull_up_down=GPIO.PUD_UP)

servoDeur = GPIO.PWM(21, 50)
servoRaam = GPIO.PWM(20, 50)
servoRaam2 = GPIO.PWM(12, 50)



def getValue():
    global condition, servoDeur, servoRaam, servoRaam2

    temperature = sensor.print_temp()
    set_temp = 26

    humidity = sensor.getAdc(0)
    set_hum = 50
    try:

        if temperature <= set_temp - 5:
            servoDeur.ChangeFrequency(50)
            servoRaam.ChangeFrequency(50)
            servoRaam2.ChangeFrequency(50)

            servoDeur.start(0)
            servoRaam.start(0)
            servoRaam2.start(0)

            servoDeur.ChangeDutyCycle(2.5)
            servoRaam.ChangeDutyCycle(2.5)
            servoRaam2.ChangeDutyCycle(2.5)
            condition = "closed"
            connection.setDataToDatabaseMetingenMetVerandering(temperature, "temperature", "automatic: closed")
            time.sleep(3)
            servoDeur.stop()
            servoRaam.stop()
            servoRaam2.stop()

        if temperature >= set_temp + 5:
            servoDeur.ChangeFrequency(50)
            servoRaam.ChangeFrequency(50)
            servoRaam2.ChangeFrequency(50)

            servoDeur.start(0)
            servoRaam.start(0)
            servoRaam2.start(0)

            servoDeur.ChangeDutyCycle(6)
            servoRaam.ChangeDutyCycle(6)
            servoRaam2.ChangeDutyCycle(6)
            condition = "open"
            connection.setDataToDatabaseMetingenMetVerandering(temperature, "temperature", "automatic: opened ")
            time.sleep(3)
            servoDeur.stop()
            servoRaam.stop()
            servoRaam2.stop()

        if humidity < set_hum:
            GPIO.output(led, GPIO.HIGH)
            connection.setDataToDatabaseMetingenMetVerandering(humidity, "humidity", "automatic: watering ")
        else:
            GPIO.output(led, GPIO.LOW)
    except KeyboardInterrupt:
        GPIO.cleanup()

def openClose(number):
    global condition, servoDeur

    if GPIO.event_detected(knopBinnen):
        if (condition == "closed"):
            servoDeur.ChangeFrequency(50)
            servoDeur.start(0)
            print("Gedrukt Binnen")
            condition = "opened"
            connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door closed manually")
            servoDeur.ChangeDutyCycle(2.5)
            time.sleep(3)
            servoDeur.stop()
        else:
            servoDeur.ChangeFrequency(50)
            servoDeur.start(0)
            print("Gedrukt Binnen 2")
            condition = "closed"
            connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door opened manually")
            servoDeur.ChangeDutyCycle(6)
            time.sleep(3)
            servoDeur.stop()
    time.sleep(0.0025)


    if GPIO.event_detected(knopBuiten):
        if (condition == "opened"):
            servoDeur.ChangeFrequency(50)
            servoDeur.start(0)
            print("Gedrukt Buiten ")
            condition = "opened"
            connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door opened manually")
            servoDeur.ChangeDutyCycle(6)
        else:
            servoDeur.ChangeFrequency(50)
            servoDeur.start(0)
            print("Gedrukt Buiten 2")
            condition = "opened"
            connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door closed manually")
            servoDeur.ChangeDutyCycle(2.5)  # turn towards 180 degree
    time.sleep(3)
    servoDeur.stop()
    time.sleep(0.0025)

@app.route('/')
def onboarding():
    return render_template('onboarding.html')


@app.route('/onboarding1', methods=['post'])
def onboarding1():
    global loggedIn
    name = request.form['inputName']
    email = request.form['inputEmail']
    password = request.form['inputPass']
    passwordRepeat = request.form['inputRepeatPass']
    loggedIn = False
    unique = connection.getDataFromDatabaseEmail(email)

    if unique == []:
        if password == passwordRepeat:
            connection.setDataToDatabaseGebruikers(name, email, password)
            return render_template('onboarding1.html'), True
        else:
            error = "Passwords do not match."
    else:
        error = "Account with e-mailaddress " + email + " already exists."
    return render_template('onboarding.html', error=error)


@app.route('/index', methods=['post'])
def index():
    global loggedIn, condition
    error = None
    if request.method == 'POST':
        email = request.form['emailLogin']
        password = request.form['passwordLogin']
        data = connection.getDataFromDatabaseMetVoorwaarde(email, password)

        if data == []:
            loggedIn = False
            error = "Invalid Credentials. Please try again."
        else:
            temp = sensor.print_temp()
            humi = float(sensor.getAdc(0))
            loggedIn = True
            return render_template('index.html', temperature=temp, humidity=humi, condition=condition)
    return render_template('onboarding.html', error=error)


@app.route('/onboarding2', methods=['post'])
def onboarding2():
    if request.method == 'POST':
        reports = request.form['reports']
        unit = request.form['unit']
        connection.updateTable(unit, reports)
        return render_template('onboarding2.html')


@app.route('/index', methods=['post'])
def onboardingDone():
    global loggedIn, condition
    # temp_ = sensor.print_temp()
    # humi = float(sensor.getAdc(0))
    if request.method == 'POST':
        temp = request.form['temp']
        hum = request.form['hum']
        connection.insertConfig(hum, temp)

        temp_ = sensor.print_temp()
        humi_ = float(sensor.getAdc(0))
        loggedIn = True
        return render_template('index.html', temperature=temp_, humidity=humi_, condition=condition)
    else:
        error=""
    return render_template('onboarding.html', error=error)

@app.route('/index')
def index_loggedIn():
    global loggedIn, condition
    if loggedIn == True:
        temp = sensor.print_temp()
        humi = float(sensor.getAdc(0))
        return render_template('index.html', temperature=temp, humidity=humi, condition=condition)
    else:
        error = "Please sign in."
    return render_template('onboarding.html', error=error)


@app.route('/logout')
def logout():
    global loggedIn
    loggedIn = False
    return render_template('onboarding.html')


@app.route('/report')
def report():
    global loggedIn
    if loggedIn == True:
        results = connection.getDataFromDatabase()
        return render_template('report.html', results=results)
    else:
        error = "Please sign in."
    return render_template('onboarding.html', error=error)


@app.route('/settings')
def settings():
    global loggedIn
    temp = connection.getDesiredTemp(20)
    hum = connection.getDesiredHum(20)

    if loggedIn == True:

        return render_template('settings.html', temperature=temp, humidity=hum)
    else:
        error = "Please sign in."
    return render_template('onboarding.html', error=error)


schedule.run_pending()

if __name__ == '__main__':
    schedule.every(15).minutes.do(writeToDb)
    schedule.every(15).minutes.do(getValue)
    schedule.every(24).hours.do(emptyDb)
    t = Thread(target=run_schedule)
    t.start()
    GPIO.add_event_detect(knopBinnen, GPIO.FALLING, callback=openClose,bouncetime=300)
    GPIO.add_event_detect(knopBuiten, GPIO.FALLING, callback=openClose,bouncetime=300)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=False)
