from flask import Flask
from flask import render_template, request
import os
import mysql.connector as mc
import spidev
import time
import RPi.GPIO as GPIO
from DbClass import DbClass

connection = DbClass()

sensor_file = '/sys/bus/w1/devices/28-051673ac35ff/w1_slave'

spi = spidev.SpiDev()
spi.open(0, 0)

led = 16

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(led, GPIO.OUT)
#
# GPIO.setup(21, GPIO.OUT)
# GPIO.setup(20, GPIO.OUT)
#
# servoDeur = GPIO.PWM(21, 50)
# servoRaam = GPIO.PWM(20, 50)
#
# servoDeur.start(7.5)
# servoRaam.start(7.5)


def getAdc(channel):
    # check valid channel
    if ((channel > 7) or (channel < 0)):
        return -1
    # Preform SPI transaction and store returned bits in 'r'
    r = spi.xfer([1, (8 + channel) << 4, 0])
    # Filter data bits from retruned bits
    adcOut = ((r[1] & 3) << 8) + r[2]
    percent = int(round(adcOut / 10.24))
    # print out 0-1023 value and percentage
    return percent
    # time.sleep(0.1)

def read_temp_raw():
    f = open(sensor_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        return lines[1]

def print_temp():
    line = read_temp()
    temp = line.split('t=')[1]
    temp = float(temp) / 1000.0
    return temp

app = Flask(__name__)

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
        temp = print_temp()
        vocht = float(getAdc(0))
        return render_template('index.html', temperatuur=temp, vochtigheid=vocht)

@app.route('/index', methods=['post'])
def index():
    email = request.form['emailLogin']
    password = request.form['passwordLogin']
    data = connection.getDataFromDatabaseMetVoorwaarde(email, password)

    if data is None:
        return "Username or password is wrong"
    else:
        temp = print_temp()
        vocht = float(getAdc(0))
        return render_template('index.html', temperatuur=temp, vochtigheid=vocht)


@app.route('/rapporten')
def rapporten():
    # results = []
    results = connection.getDataFromDatabase()
    return render_template('rapporten.html', results=results)

@app.route('/instellingen')
def instellingen():
    return render_template('instellingen.html')

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=True)
