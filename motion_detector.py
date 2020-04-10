import cv2
import imutils
from sklearn.metrics import pairwise
import numpy as np

"""
Business class which allows the segmentation of the background and foreground.
This allows us to detect, analyze and interpret the movement of the hand to control the game.
"""
class MDetector:
	#constructor
    def __init__(self, aw=0.5):
        self.aw=aw
        self.bg=None

    # background modeling
    def update(self, img):
        if self.bg is None:
            self.bg=img.copy().astype("float")
            return
        cv2.accumulateWeighted(img, self.bg, self.aw)

    #detection of hand movements
    def detector(self, img, tval=25):
        mask=cv2.absdiff(img, self.bg.astype("uint8"))
        seuil=cv2.threshold(mask, tval, 255, cv2.THRESH_BINARY)[1]
        cnts=cv2.findContours(seuil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts=imutils.grab_contours(cnts)
        if len(cnts)==0:
            return None
        else:
            return(seuil, max(cnts, key=cv2.contourArea))

    #analysis and interpretation of hand movements to control the game
    def process(self, img):
        rs=self.detector(img)
        if rs is not None:
            (mask, c)=rs
            hull=cv2.convexHull(c)
            l=tuple(hull[hull[:, :, 0].argmin()][0])
            r=tuple(hull[hull[:, :, 0].argmax()][0])
            t=tuple(hull[hull[:, :, 1].argmin()][0])
            b=tuple(hull[hull[:, :, 1].argmax()][0])

            cx=(l[0]+r[0])//2
            cy=(t[1]+b[1])//2
            cy+=0.15*cy
            cy=int(cy)
            d=pairwise.euclidean_distances([(cx, cy)], Y=[l, r, t, b])[0]
            max_dist=d[d.argmax()]
            rr=int(max_dist*0.70)
            cir=2*np.pi*rr
            circle=np.zeros(mask.shape[:2], dtype="uint8")
            cv2.circle(circle, (cx, cy), rr, 255, 1)
            circle=cv2.bitwise_and(mask, mask, mask=circle)
            cnts=cv2.findContours(circle, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts=imutils.grab_contours(cnts)
            if len(cnts)>2:
                return (1, mask, circle, (cx, cy), c, hull, l, r, t, b)
            else:
                return (0, mask, circle, (cx, cy), c, hull, l, r, t, b)
