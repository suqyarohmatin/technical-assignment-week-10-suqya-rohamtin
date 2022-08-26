import time
import requests
import math
import random
import time
import RPi.GPIO as GPIO

TOKEN = "BBFF-lmy4IoKn1R0shP19aYZPzb2UlwV2ea"  # Put your TOKEN here
DEVICE_LABEL = "ubi_jarak"  # Put your device label here
VARIABLE_LABEL_1 = "distance"  # Put your first variable label here

GPIO.setmode(GPIO.BCM)  # set penomeran board ke mode broadcom
GPIO.setwarnings(False)
 
# Set mode pin sebagai input untuk trigger, dan output untuk echo
GPIO_TRIGGER = 18 #sesuaikan pin trigger
GPIO_ECHO = 24 #sesuaikan pin echo
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_ECHO,GPIO.IN)  
 
# Set trigger ke False (Low) untuk awal
GPIO.output(GPIO_TRIGGER, GPIO.LOW)


def get_range():
    # Kirim 10us sinyal high ke trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
     
    #Stop trigger
    GPIO.output(GPIO_TRIGGER, False)
    timeout_counter = int(time.time())
    start = time.time()
 
    #dapatkan waktu start
    while GPIO.input(GPIO_ECHO)==0 and (int(time.time()) - timeout_counter) < 3:
        start = time.time()
 
    timeout_counter = int(time.time())
    stop = time.time()
    #dapatkan waktu stop
    while GPIO.input(GPIO_ECHO)==1 and (int(time.time()) - timeout_counter) < 3:
        stop = time.time()
 
    #Hitung waktu tempuh bolak-balik
    elapsed = stop-start
 
    #Hitung jarak, waktu tempuh dikalikan dengan kecepata suara (dalam centi meter)
    distance = elapsed * 34320
 
    #Jaraknya masih dalam hitungan bolak-balik, bagi dua untuk tahu jarak ke halangan
    distance = distance / 2
 
    #selesai
    return distance


def build_payload(variable_1):
    # Creates two random values for sending data
    val = get_range()
    #value_1 = float("{0:.2f}".format(val))
    value_1 = float("{0:.2f}".format(val))
    payload = {variable_1: value_1}

    return payload


def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    payload = build_payload(VARIABLE_LABEL_1)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")


if __name__ == '__main__':
    while (True):
        main()
        time.sleep(1)
