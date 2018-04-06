from serial import Serial
from threading import Thread
# import requests
from multiprocessing import Queue
# from Queue import Queue
import signal
import sys
import json
import csv
import os
import time
import requests

class serialWatcher (Thread, Serial):
    def __init__(self, q, port = '/dev/ttyACM0', baudrate = 115200):
        Thread.__init__(self)
        Serial.__init__(self, port, baudrate)
        self.daemon = True
        self.queue = q
    def run(self):
        self.running = True
        while self.running:
            if self.in_waiting:
                line = self.readline()[0:-1];
                try:
                    data = json.loads(line)
                    self.queue.put(data)
                    # print "Sensor data in Queue"
                except:
                    # print "Invalid data discarted"
                    pass
    def stop(self):
        self.running = False

data_queue = Queue(10)
sensor = serialWatcher(q = data_queue)
sensor.start()
credentials="$$$$" #write here your credentials

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def data_process(data):
    print ("Dato siendo procesado...\n")
    print (data)


def data_csv(data):
    with open('data.csv', 'a') as outf:
        dw = csv.DictWriter(outf, fieldnames=['current', 'voltage', 'temperature'], extrasaction='ignore')
        # dw.writeheader()
        dw.writerow(data)

def data_ubidots(data,credentials):
        r=requests.post('https://things.ubidots.com/api/v1.6/devices/demo/?token=' + credentials, data=data)

try:
    os.remove('data.csv')
except OSError:
    pass
while True:
    if not data_queue.empty():
        data = data_queue.get()
        data_process(data)
        data_csv(data)
        data_ubidots(data,credentials)
