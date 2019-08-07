# globals.py
# Contains the global variables used for communication
# between image processing and server

def initialize():
    global image_processing_begin
    global image_processing_send
    global image_processing_abort
    global latitude
    global longitude
    global altitude
    global abort
    latitude = 0
    longitude = 0
    altitude = 0
    image_processing_begin = False
    image_processing_send = True
    image_processing_abort = False
