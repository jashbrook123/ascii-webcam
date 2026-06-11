import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
import math


start_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(base_options = start_options,num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)


def get_rot(hand):
    wrist = hand[0]
    middle_finger = hand[9]
    dx = middle_finger.x - wrist.x
    dy = middle_finger.y - wrist.y
    yaw = math.degrees(math.atan2(dy,dx))
    return yaw

def dist(a,b):
    return math.hypot(a.x-b.x,a.y-b.y)

def is_thumb_folded(hand):
    return dist(hand[4],hand[5]) < 0.07

def fist_check(hand):
    tips = [4,8,12,16,20]
    mcps = [2,5,9,13,17]
    folded_fingers = 0
    for t,m in zip(tips[1:],mcps[1:]):
        if hand[t].y > hand[m].y:
            folded_fingers +=1
    thumb_folded = is_thumb_folded(hand)
    return folded_fingers >=3 and thumb_folded

def get_image(img):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,data=img)
    result = detector.detect(mp_image)
    yaw = None
    fist = False
    if result.hand_landmarks:
        for handLms in result.hand_landmarks:
            for lm in handLms:
                x = int(lm.x * img.shape[1])
                y = int(lm.y * img.shape[0])
            yaw = get_rot(handLms)
            if fist_check(handLms): fist = True
    
    return yaw, fist


    
