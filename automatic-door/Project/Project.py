from flask import Flask, render_template, request, send_file
import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from werkzeug import secure_filename
import os

app = Flask(__name__)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

led_w = 20
led_b = 21
PIR = 4
servo_pin = 18
finger = 16

led_r = 26
buz = 12

TRIG = 23
ECHO = 25

GPIO.setup(finger, GPIO.IN)
GPIO.setup(servo_pin, GPIO.OUT)
GPIO.setup(led_w, GPIO.OUT)
GPIO.setup(led_b, GPIO.OUT)
GPIO.setup(PIR, GPIO.IN, GPIO.PUD_UP)

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

GPIO.setup(led_r, GPIO.OUT)
GPIO.setup(buz,GPIO.OUT)
b = GPIO.PWM(12,10)
Fre = [392,262]
speed = 0.5
b.start(5)

app = Flask(__name__)
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)

GPIO.output(TRIG, False)

@app.route('/')
def home_page():
	return render_template('home.html')

@app.route("/open")
def open_page():
    return render_template('open.html')

@app.route("/door/open")
def door_open():
    print("Ready!")
    try:
        while True:
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)
            while GPIO.input(ECHO) == False:
                start = time.time()
            while GPIO.input(ECHO) == True:
                stop = time.time()
            check_time = stop - start
            distance = check_time * 34300 / 2
            if distance >20:
                print("System in operation!")
                GPIO.output(led_w, 1)
                GPIO.output(led_b, 0)
            if GPIO.input(PIR) == 1 and 11 < distance < 20:
                camera = PiCamera()
                counter = 1
                servo = GPIO.PWM(servo_pin,50)
                servo.start(0)
                print("Distance : %.1f cm"%(distance))
                t = time.localtime()
                print("%d:%d:%d Open!"%(t.tm_hour, t.tm_min, t.tm_sec))
                GPIO.output(led_r,0)
                GPIO.output(led_b, 1)
                GPIO.output(led_w, 0)
                servo.ChangeDutyCycle(7)
                time.sleep(3)
                servo.ChangeDutyCycle(9)
                time.sleep(1)
                servo.ChangeDutyCycle(11.5)

                camera.start_preview()
                camera.capture('/home/pi/CCTV%s.png' % counter)
                counter = counter + 1
                camera.stop_preview()
                camera.close()
                servo.stop()
                break;
            if distance < 11:
                print("Stop!")
                GPIO.output(26,GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(26,GPIO.LOW)
    except KeyboardInterrupt:
        camera.close()
    return render_template('open.html')


@app.route("/sensor/open")
def sensor_open():
    try:
        while True:
            if GPIO.input(finger) == 0:
                print("System in operation!")
                GPIO.output(led_b, 0)
                GPIO.output(led_w, 1)
            if GPIO.input(finger) == 1:
                camera = PiCamera()
                counter = 2
                servo = GPIO.PWM(servo_pin,50)
                servo.start(0)
                td = time.localtime()
                print("%d:%d:%d Open!"%(td.tm_hour, td.tm_min, td.tm_sec))
                GPIO.output(led_r,0)
                GPIO.output(led_b, 1)
                GPIO.output(led_w, 0)
                servo.ChangeDutyCycle(7)
                time.sleep(3)
                servo.ChangeDutyCycle(9)
                time.sleep(1)
                servo.ChangeDutyCycle(11.5)

                camera.start_preview()
                camera.capture('/home/pi/CCTV%s.png' % counter)
                counter = counter + 1
                camera.stop_preview()
                camera.close()
                servo.stop()
                break;
                return render_template('seosor.html')
    except KeyboardInterrupt:
        camera.close()
    return render_template('sensor.html')


@app.route("/sensor")
def sensor_page():
    return render_template('sensor.html')

@app.route('/list')
def list_page():
	file_list = os.listdir("/home/pi/upload")
	html = """<center><a href="/">홈페이지</a><br><br>""" 
	html += "file_list: {}".format(file_list) + "</center>"
	return html

@app.route("/buz1/on")
def buz_on1():
    try:
            GPIO.output(26,GPIO.HIGH)
            time.sleep(0.4)
            GPIO.output(26,GPIO.LOW)
            time.sleep(0.4)
            GPIO.output(26,GPIO.HIGH)
            time.sleep(0.4)
            GPIO.output(26,GPIO.LOW)
            for fr in Fre:
                b.ChangeFrequency(fr)
                time.sleep(speed)
            print("System Off")
    except KeyboardInterrupt:
        pass
    b.stop()
    return render_template('open.html')

@app.route("/buz2/on")
def buz_on2():
    try:
            GPIO.output(26,GPIO.HIGH)
            time.sleep(0.4)
            GPIO.output(26,GPIO.LOW)
            time.sleep(0.4)
            GPIO.output(26,GPIO.HIGH)
            time.sleep(0.4)
            GPIO.output(26,GPIO.LOW)
            for fr in Fre:
                b.ChangeFrequency(fr)
                time.sleep(speed)
            print("System Off")
    except KeyboardInterrupt:
        pass
    b.stop()
    return render_template('sensor.html')


@app.route('/downfile')
def down_page():
	files = os.listdir("/home/pi/upload/")
	return render_template('filedown.html',files=files)

@app.route('/fileDown', methods = ['GET', 'POST'])
def down_file():
	if request.method == 'POST':
		sw=0
		files = os.listdir("/home/pi/upload/")
		for x in files:
			if(x==request.form['file']):
				sw=1
				path = "/home/pi/upload/" 
				return send_file(path + request.form['file'],
						attachment_filename = request.form['file'],
						as_attachment=True)

		return render_template('home.html')


@app.route('/upload')
def upload_page():
	return render_template('upload.html')

@app.route('/download')
def download_page():
	return render_template('filedown.html')

@app.route('/fileUpload', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f = request.files['file']
		f.save('/home/pi/upload/' + secure_filename(f.filename))
		return render_template('check.html')


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug = True)