import RPi.GPIO as GPIO
import time

knopBinnen = 26
knopBuiten = 19


GPIO.setmode(GPIO.BCM)
GPIO.setup(knopBinnen, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(knopBuiten, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_callback(knopBinnen, GPIO.FALLING)
GPIO.add_event_callback(knopBuiten, GPIO.FALLING)

isKnopGedruktVorig = 1
stand = 0

isKnopBuitenGedruktVorig = 1
standBuiten = 0

GPIO.setup(21, GPIO.OUT)

servoDeur = GPIO.PWM(21, 50)

servoDeur.start(0)

try:
    while True:
        isKnopGedrukt = GPIO.input(knopBinnen)

        if GPIO.event_detected(knopBinnen):
            if(isKnopGedrukt != isKnopGedruktVorig):
                if(isKnopGedrukt == 0):
                    if(stand == 0):
                            print("Gedrukt")
                            stand = 1
                            servoDeur.ChangeDutyCycle(7.5)  # turn towards 90 degree
                    else:
                        print("Gedrukt2")
                        stand = 0
                        servoDeur.ChangeDutyCycle(12.5)  # turn towards 180 degree

            isKnopGedruktVorig = isKnopGedrukt
            time.sleep(0.0025)

        isKnopBuitenGedrukt = GPIO.input(knopBuiten)

        if GPIO.event_detected(knopBuiten):
            if (isKnopBuitenGedrukt != isKnopBuitenGedruktVorig):
                if (isKnopBuitenGedrukt == 0):
                    if (standBuiten == 0):
                            print("Gedrukt")
                            standBuiten = 1
                            servoDeur.ChangeDutyCycle(7.5)  # turn towards 90 degree

                    else:
                        print("Gedrukt2")
                        standBuiten = 0
                        servoDeur.ChangeDutyCycle(12.5)  # turn towards 180 degree

            isKnopBuitenGedruktVorig = isKnopBuitenGedrukt
            time.sleep(0.0025)

except KeyboardInterrupt:
    servoDeur.start(0)
    servoDeur.stop()
    GPIO.cleanup()