import webbrowser
import cv2
from threading import Thread
import imutils
from imutils.video import VideoStream
import win32api
# import win32com.client
import win32con
import time
from motion_detector import MDetector

"""
Class that allows us to launch google chrome with python on a thread
Inherits from the thread class
"""


class Chrome(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        chrome_path = "C:/Users/DELL/dinosour_project %s"
        webbrowser.get(chrome_path).open("http://www.google.com")


"""
class which inherits from class Thread allows to control the game (this task also is launched on a different thread).
if we detect that the 5 fingers of the hand are all stretched an event of type 0x20 (pressed on the space bar)
is generated thanks to the win32api and win32con APIs from python and go to the thread that launched google chrome (the Chrome class)
NB: after launching the pilot script.py leave the focus on the google chrome window otherwise you will have bugs
"""


class Job(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        t, r, b, l = (10, 350, 225, 590)
        vs = VideoStream(src=0).start()
        md = MDetector()
        num_fram = 0
        while True:
            img = vs.read()
            img = cv2.flip(img, 1)
            img = imutils.resize(img, 600)
            copy = img.copy()
            roi = img[t:b, r:l]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            if num_fram < 32:
                md.update(gray)
            else:
                rs = md.process(gray)
                if rs is not None:
                    event, mask, cr, ct, c, hull, ll, rr, tt, bb = rs
                    if event == 1:
                        win32api.keybd_event(0x20, 0, 0, 0)
                        time.sleep(.05)
                        win32api.keybd_event(0x20, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(0.8)
                    cv2.imshow("mask", mask)
                    cv2.drawContours(copy, [c + (r, t)], -1, (0, 255, 0), 2)
                    cv2.circle(copy, (ll[0] + r, ll[1] + t), 5, (255, 0, 0), -1)
                    cv2.circle(copy, (rr[0] + r, rr[1] + t), 5, (255, 0, 0), -1)
                    cv2.circle(copy, (tt[0] + r, tt[1] + t), 5, (255, 0, 0), -1)
                    cv2.circle(copy, (bb[0] + r, bb[1] + t), 5, (255, 0, 0), -1)
                    cv2.circle(copy, (ct[0] + r, ct[1] + t), 5, (255, 0, 0), -1)
                    cv2.imshow("cr", cr)
            cv2.rectangle(copy, (l, t), (r, b), (0, 0, 255), 2)
            cv2.imshow("img", copy)
            key = cv2.waitKey(1) & 0xff
            if key == ord("q"):
                break
            num_fram += 1


t = Chrome()
job = Job()
t.start()
job.start()
t.join()
job.join()

# shell=win32com.client.Dispatch("WScript.shell")
# shell. ("chrome")

while True:
    win32api.keybd_event(0x20, 0, 0, 0)
    time.sleep(.05)
    win32api.keybd_event(0x20, 0, win32con.KEYEVENTF_KEYUP, 0)
