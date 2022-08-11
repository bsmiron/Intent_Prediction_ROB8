from pickle import TRUE
import numpy as np
import cv2
import mediapipe as mp
import math
import time

FX = 640
FY = 640
PPX = 320
PPY = 240
CamMatrix = np.asarray([[FX, 0.0, PPX, 0],
                        [0.0, FY, PPY, 0],
                        [0.0, 0.0, 1.0, 0]])


def get_coordinate(pixel_x, pixel_y, depth_image, matrix=CamMatrix):
    
    z = depth_image[pixel_y, pixel_x] * 40 # the result of depth is in mm
    # print(z) # = [2 2 2] should be 2
    cam_coord = [pixel_x, pixel_y]
    Z = depth_image[cam_coord[1], cam_coord[0]] * 40
    # print(Z)
    
    u = cam_coord[0] * Z
    v = cam_coord[1] * Z
    X = -(u - matrix[0, 2] * Z) / (matrix[0, 0])
    Y = -(v - matrix[1, 2] * Z) / (matrix[1, 1])
    return [int(X), int(Y), int(Z)]

# Check if the path is correct
rgb_cap = cv2.VideoCapture('depth_videos_for_bogdan/color_video_of_hand.avi')
depth_cap = cv2.VideoCapture('depth_videos_for_bogdan/depth_video_of_hand.avi')

#Check if I'm capturing
if(rgb_cap.isOpened() == False or depth_cap.isOpened() == False):
    print('Problem with captureing frames, procede further investigations')


# MediaPipe Magic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while rgb_cap.isOpened() and depth_cap.isOpened():
    success, color_image = rgb_cap.read()
    _, depth_image = depth_cap.read()
    depth_image_gray = cv2.cvtColor(depth_image, cv2.COLOR_RGB2GRAY)
    if not success and not _:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      break

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    color_image.flags.writeable = False
    color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
    results = hands.process(color_image)

    # Draw the hand annotations on the image.
    color_image.flags.writeable = True
    color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        
        # mp_drawing.draw_landmarks(
            # color_image,
            # hand_landmarks,
            # mp_hands.HAND_CONNECTIONS,
            # mp_drawing_styles.get_default_hand_landmarks_style(),
            # mp_drawing_styles.get_default_hand_connections_style())

        for id, lm in enumerate(hand_landmarks.landmark):
                    #print(id,lm) id = type of landmark; lm coordinates of the landmark
                    h, w, c = color_image.shape
                    cx, cy = int(lm.x *w), int(lm.y*h)
                         
                    if id == 9 and (cx - 20) < color_image.shape[0] and cx > 20 and (cy - 20) < color_image.shape[1] and cy > 20 :
                        print(cx, cy)
                        cv2.circle(color_image,(cx, cy), 2, (255, 0, 255), 2)
                        hand_x, hand_y, hand_z = get_coordinate(cx, cy, depth_image_gray) #x and y
                        print(f'hand_x = {hand_x}, hand_y = {hand_y}, hand_z = {hand_z}')
          
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('test',color_image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
rgb_cap.release()
depth_cap.release()