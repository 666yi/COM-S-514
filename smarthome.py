import time
import board
import threading
import RPi.GPIO as GPIO

vib_trigger = False
pushbutton_on = False
touchbutton_on = False

class vib_sensor:
    def __init__(self):
        self.sensor_pin = 19 # input pin of the vibrarion sensor
        GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self):
        global vib_trigger
        while(True):
            self.vib_sen = GPIO.input(self.sensor_pin)
            if(self.vib_sen == False):
                #print("Vibrator trigger")
                vib_trigger = True
                time.sleep(0.3)

    def start(self):
        vib_thread = threading.Thread(target=self.run)
        vib_thread.start()

class touch_button():
    def __init__(self):
        self.sensor_pin = 17 # input pin of the vibrarion sensor
        GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self):
        global touchbutton_on
        while(True):
            self.button_sen = GPIO.input(self.sensor_pin)
            if(self.button_sen == False):
                touchbutton_on = True
                time.sleep(0.05)
                touchbutton_on = False
                while(self.button_sen == False):
                    self.button_sen = GPIO.input(self.sensor_pin)
                time.sleep(0.05)

    def start(self):
        tb_thread = threading.Thread(target=self.run)
        tb_thread.start()


class push_button():
    def __init__(self):
        self.sensor_pin = 26 # input pin of the vibrarion sensor
        GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self):
        global pushbutton_on
        do_send = True
        while(True):
            self.button_sen = GPIO.input(self.sensor_pin)
            if(self.button_sen == False):
                time.sleep(0.5)
                if(self.button_sen == False):
                    #print("Button on")
                    if(do_send):
                        pushover("Emergency, the owner triggers the alarm!")
                        do_send = False
                    pushbutton_on = True
            else:
                time.sleep(0.5)
                if(self.button_sen == True):
                    do_send = True
                    #print("Button off")
                    pushbutton_on = False

    def start(self):
        pb_thread = threading.Thread(target=self.run)
        pb_thread.start()



import neopixel
from neopixel_write import neopixel_write
class neo_pixel:
    def __init__(self):
        self.num_pixels = 16
        self.neo_pin = board.D18
        self.ORDER = neopixel.GRBW
        self.pixels = neopixel.NeoPixel(self.neo_pin, self.num_pixels, brightness=0.01, auto_write=False, pixel_order=self.ORDER)
        self.brightness_tab = [0.0 , 0.01, 0.05, 0.2, 0.5, 1.0]
    def rainbow_cycle(self, wait=0.001):
        global vib_trigger, pushbutton_on, touchbutton_on
        def wheel(pos):
            # Input a value 0 to 255 to get a color value.
            # The colours are a transition r - g - b - back to r.
            if pos < 0 or pos > 255:
                r = g = b = 0
            elif pos < 85:
                r = int(pos * 3)
                g = int(255 - pos*3)
                b = 0
            elif pos < 170:
                pos -= 85
                r = int(255 - pos*3)
                g = 0
                b = int(pos*3)
            else:
                pos -= 170
                r = 0
                g = int(pos*3)
                b = int(255 - pos*3)
            return (r, g, b, 0) 
        while(True):
            for j in range(255):
                for i in range(self.num_pixels):
                    pixel_index = (i * 256 // self.num_pixels) + j
                    self.pixels[i] = wheel(pixel_index & 255)
                self.pixels.show()
                if(vib_trigger):
                    vib_trigger = False
                    return
                if(touchbutton_on):
                    while(touchbutton_on):
                        pass
                    return
                if(pushbutton_on):
                    return
                time.sleep(wait)

    def show_alart(self):
        global pushbutton_on
        while(pushbutton_on):
            self.pixels.fill((255,0,0,0))
            neopixel_write(self.pixels.pin, bytearray([int(k*1.0) for k in self.pixels.buf])) # hacked from source file above
            time.sleep(1.00)
            self.pixels.fill((0,0,0,0))
            self.pixels.show()
            time.sleep(1.00)

    def show_white(self, brightness):
        global vib_trigger, pushbutton_on, touchbutton_on
        self.pixels.fill((0,0,0,255))
        #https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel/blob/master/neopixel.py
        neopixel_write(self.pixels.pin, bytearray([int(k*brightness) for k in self.pixels.buf])) # hacked from source file above
        #self.pixels.show()
        while(True):
            if(vib_trigger):
                vib_trigger = False
                break
            if(touchbutton_on):
                while(touchbutton_on):
                    pass
                break
            if(pushbutton_on):
                break

    def run(self):
        # switch between different mode
        global pushbutton_on
        while(True):
            self.rainbow_cycle()
            for i in range(6):
                #brightness = 0.2*i
                brightness = self.brightness_tab[i]
                #print("Set brightness ",brightness)
                self.show_white(brightness)
            if(pushbutton_on):
                self.show_alart()

    def start(self):
        neo_thread = threading.Thread(target=self.run)
        neo_thread.start()


import http.client, urllib
def pushover(msg):
    api_token = "a7rhh5bthdk89i48v7y1nin7pu5kut"
    user_token = "ghgvb4edkz22my22c3ti84x2vtnkx6" #This token is for the pushover "alarm" group users
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": api_token,
            "user": user_token,
            "message": msg,
        }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def main():
    vibs = vib_sensor()
    pb = push_button()
    neop = neo_pixel()
    tb = touch_button()
    vibs.start()
    pb.start()
    tb.start()
    neop.start()

if __name__ == "__main__":
    main()
