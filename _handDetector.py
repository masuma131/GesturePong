"""
Hand Detection Module using OpenCV and MediaPipe

This module defines a `HandDetector` class that leverages MediaPipe's hand-tracking capabilities to detect and track hands in real-time. 
The class provides methods to:
1. Detect hands and draw landmarks on an input image.
2. Extract pixel coordinates for all hand landmarks or specific landmarks by index.

Methods:
- `processHandImg(img)`: Processes an image to detect hands.
- `showLandMarks(img)`: Draws hand landmarks on the image if hands are detected.
- `getAllLandmarksPos(img, handNum=0)`: Returns a list of pixel coordinates for all landmarks of a specified hand.
- `getLandmarksPosByIndex(img, handNum=0, index=[0], drawIndex=True, radius=25, color=(255,0,123))`: Returns coordinates for specific landmarks by index and optionally draws them on the image.

Usage: This class can be used in real-time applications for hand detection and gesture-based interactions.
"""

import cv2 as cv
import mediapipe as mp


class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_conf=0.5, track_conf=0.5):
        # hand object
        self.mpHand = mp.solutions.hands
        self.hands = self.mpHand.Hands(
            static_image_mode=mode,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=track_conf
        )

        # Draw LandMarks object
        self.mpDraw = mp.solutions.drawing_utils

    # process hand
    def processHandImg(self, img):
        # Convert BGR image to RGB
        rgb_img = cv.cvtColor(src=img, code=cv.COLOR_BGR2RGB)

        # Process the Image
        self.result = self.hands.process(rgb_img)

        # return img

    def showLandMarks(self, img):
        if self.result.multi_hand_landmarks:
            # Extract landmarks for each hands
            for handLandmarks in self.result.multi_hand_landmarks:
                # Draw landmarks on the image
                self.mpDraw.draw_landmarks(
                    img, handLandmarks, self.mpHand.HAND_CONNECTIONS)

    # x, y pixel co-ordinate of all the indexes (0-20) of a certain hand
    def getAllLandmarksPos(self, img, handNum=0):

        landmark_List = []

        if self.result.multi_hand_landmarks:
            # choose one hand
            hand = self.result.multi_hand_landmarks[handNum]


            # Get landmarks for each detected hand
            for Id, landmark in enumerate(hand.landmark):
                # Note: landmark has normalized x, y, and z coordinates (values between 0 and 1)
                height, width, _channels = img.shape  # Get image dimensions
                # Convert normalized coordinates to pixel values
                cx, cy = int(landmark.x * width), int(landmark.y * height)

                # Append landmark ID and pixel coordinates to the list
                landmark_List.append([Id, cx, cy])

        return landmark_List
    
    # x, y pixel co-ordinate of ceratin indexes of a certain hand
    def getLandmarksPosByIndex(self, img, handNum=0, index=[0], drawIndex=True, radius=25, color=(255,0,123)):

        landmark_List = []

        if self.result.multi_hand_landmarks:
            # choose one hand
            hand = self.result.multi_hand_landmarks[handNum]


            # Get landmarks for each detected hand
            for Id, landmark in enumerate(hand.landmark):
                # Note: landmark has normalized x, y, and z coordinates (values between 0 and 1)
                height, width, _channels = img.shape  # Get image dimensions
                # Convert normalized coordinates to pixel values
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                
                if Id in index:
                    # Append landmark ID and pixel coordinates to the list
                    landmark_List.append([Id, cx, cy])
                    
                    if drawIndex:
                        cv.circle(img=img, center=(cx,cy), radius=radius, color=color, thickness=3)

        return landmark_List
