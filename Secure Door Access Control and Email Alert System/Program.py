import RPi.GPIO as GPIO
import time as t
from mfrc522 import SimpleMFRC522
import smtplib
import picamera
import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(12,GPIO.OUT)

pwm=GPIO.PWM(12,50)
pwm.start(0)

def SetAngle(angle):
	duty = angle / 18 + 2
	GPIO.output(12, True)
	pwm.ChangeDutyCycle(duty)
	t.sleep(1)
	GPIO.output(12, False)
	pwm.ChangeDutyCycle(0)
	

def validation():
    valid = [1081313927759, 764207711048]
    if id in valid:
        print("Entry Accepted")
        SetAngle(180)
        t.sleep(1)
        SetAngle(0)
        return "Person Entry Accepted"
    else:
        print("Entry Denied")
        return "Person Entry Denied"

def email(message):
    # Define email credentials and recipient
    to_email = 't.o.stark2728@gmail.com'
    password = '*************'
    from_email = 'vasuadireddy2001@gmail.com'
    # Take a picture with the Raspberry Pi camera module
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    camera.capture('/home/pi/image.jpg')
    # Create the email message
    camera.close()
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = message
    with open('/home/pi/image.jpg', 'rb') as f:
        img = MIMEImage(f.read())
        msg.attach(img)
    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print('Email sent successfully')
    except Exception as e:
        print('Something went wrong:', e)

# reading Tag
reader = SimpleMFRC522()

while 1:
    print('Place Your Tag')
    id,text= reader.read()
    m=validation()
    email(m)
    print("ID : ",id)
    print("Name : ",text)
    print('-------------------')
    print('-------------------')
