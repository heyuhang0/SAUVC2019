"""" This program allows users to use keyboard to control the cv car
and steam back the camera image at port 3333 (use monitor.py to watch)
"""
import sys
import select
import termios # only on Linux
import tty
import threading
import time
from imutils.video import VideoStream
from tracking import CVManager
from tracking import Blank
from cvcar import MCU


class KeyListener(threading.Thread):
    """ Listens all keyboard events """
    def __init__(self):
        threading.Thread.__init__(self)
        self.key = 0
        self.time_stamp = 0
        self.stopped = True

    def __get_key(self):
        # redirect stdin to read the last keyboared event
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1) # read key
        # restore stdin setting
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.setting)
        return key

    def get_key(self):
        return (self.key, self.time_stamp)

    def run(self):
        self.stopped = False
        self.setting = termios.tcgetattr(sys.stdin) # save original stdin setting
        try:
            while True:
                self.key = self.__get_key() # wait for next key (like getch)
                if self.key == '\x03': # in case ctrl-c is pressed
                    self.stopped = True # exit the program
                    break
                self.time_stamp = time.time()
        except Exception:
            pass
        finally:
            # restore stdin setting
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.setting)


def main():
    """ main body """
    mcu = MCU("/dev/ttyUSB0", 100, 40)
    key_listener = KeyListener()
    key_listener.start()
    # prepare video streaming
    cv = CVManager(VideoStream(src=0), server_port=3333)
    cv.add_core("Stream", Blank(), True)
    cv.start()
    while not key_listener.stopped:
        key, t = key_listener.get_key()

        # if the key is released more than 0.05s
        # stop the car
        if time.time() - t > 0.05:
            mcu.set_motors(0, 0)

        # map keyboared to mcu actions
        elif key == 'w':
            mcu.set_motors(1, 0)
        elif key == 'q':
            mcu.set_motors(1, -1)
        elif key == 'e':
            mcu.set_motors(1, 1)

        elif key == 's':
            mcu.set_motors(-1, 0)
        elif key == 'a':
            mcu.set_motors(0, -1)
        elif key == 'd':
            mcu.set_motors(0, 1)

        elif key == 'x':
            mcu.set_motors(-1, 0)
        elif key == 'z':
            mcu.set_motors(-1, -1)
        elif key == 'c':
            mcu.set_motors(-1, 1)
        time.sleep(0.04)
    cv.stop()

if __name__ == "__main__":
    main()
