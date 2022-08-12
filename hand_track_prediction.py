from pickle import TRUE
import numpy as np
import cv2
import mediapipe as mp
import math
import time
import os
import subprocess

# folder = 'folder'

# def generate_video():
#     os.chdir(folder)
#     subprocess.call([
#         'ffmpeg', '-framerate', '30', '-i', 'file%02d.png', '-r', '30', '-pix_fmt', 'yuv420p',
#         'video_name.mp4'
#     ])

FX = 640
FY = 640
PPX = 320
PPY = 240
CamMatrix = np.asarray([[FX, 0.0, PPX, 0],
                        [0.0, FY, PPY, 0],
                        [0.0, 0.0, 1.0, 0]])


# Initialize KF from OpenCV

class KalmanFilter2D:
  kf = cv2.KalmanFilter(4, 2)
  kf.measurementMatrix = np.array([[1, 0, 0, 0], 
                                   [0, 1, 0, 0]], np.float32)

  kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                  [0, 1, 0, 1],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]], np.float32)
  

  def estimamte_2d(self, pixel_x, pixel_y):
    measured = np.array([[np.float32(pixel_x)], [np.float32(pixel_y)]])
    self.kf.correct(measured)
    predicted = self.kf.predict()
    int_predicted = predicted.astype(int)
    return int_predicted[0], int_predicted[1]

class KalmanFilter3D:
  kf = cv2.KalmanFilter(6, 3)

  # H matrix 
  kf.measurementMatrix = np.array([[1, 0, 0, 0, 0 ,0], 
                                   [0, 1, 0, 0, 0, 0], 
                                   [0, 0, 1, 0, 0, 0]], np.float32)

  # A matrix
  kf.transitionMatrix = np.array([[1, 0, 0, 1, 0, 0], 
                                  [0, 1, 0, 0, 1, 0], 
                                  [0, 0, 1, 0, 0, 1],
                                  [0, 0, 0, 1, 0, 0],
                                  [0, 0, 0, 0, 1, 0],
                                  [0, 0, 0, 0, 0, 1]], np.float32)
                              
  kf.processNoiseCov = np.array([[1, 0, 0, 0, 0, 0],
                                 [0, 1, 0, 0, 0, 0],
                                 [0, 0, 1, 0, 0, 0], 
                                 [0, 0, 0, 1, 0, 0],
                                 [0, 0, 0, 0, 1, 0],
                                 [0, 0, 0, 0, 0, 1]], np.float32) * 0.007

  kf.measurementNoiseCov = np.array([[1, 0, 0],
                                     [0, 1, 0],
                                     [0, 0, 1]], np.float32) * 0.1


  

  def estimamte_3d(self, pixel_x, pixel_y, pixel_z):
    measured = np.array([[np.float32(pixel_x)], [np.float32(pixel_y)], [np.float32(pixel_z)]])
    self.kf.correct(measured)
    predicted = self.kf.predict()
    int_predicted = predicted.astype(int)
    return int_predicted[0], int_predicted[1], int_predicted[2]
    # return int_predicted[2]

def get_pixels(coord_x, coord_y, coord_z):

  u = -(coord_x / coord_z) * FX + PPX
  v = -(coord_y / coord_z) * FY + PPY
  return u, v

def get_coordinate(pixel_x, pixel_y, depth_image, matrix=CamMatrix):
    
    # the result of depth is in mm
    cam_coord = [pixel_x, pixel_y]
    Z = depth_image[cam_coord[1], cam_coord[0]] * 40
  
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

kfobj2d = KalmanFilter2D()
kfobj3d = KalmanFilter3D()
# predicted_coord = np.zeros((2,1), np.float32) 


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
                    #print(id,lm) id = type of landmark; lm coordinateGIITf the landmark
                    h, w, c = color_image.shape
                    cx, cy = int(lm.x *w), int(lm.y*h)
                         
                    if id == 9: #and (cx - 20) < color_image.shape[0] and cx > 20 and (cy - 20) < color_image.shape[1] and cy > 20 :
                        # print(cx, cy)
                        cv2.circle(color_image,(cx, cy), 2, (255, 0, 255), 2)
                        hand_x, hand_y, hand_z = get_coordinate(cx, cy, depth_image_gray) #x and y
                        
                        # 2D KF

                        #predicted_x, predicted_y = kfobj2d.estimamte_2d(cx, cy)
                        # print(f'predicted 2d coord piexels x = {predicted_x}, y = {predicted_y} real pixel coord x = {cx} y = {cy}')
                        # if (predicted_x - 25) < color_image.shape[0] and predicted_x > 25 and (predicted_y - 25) < color_image.shape[0] and predicted_y > 25:
                          # cv2.circle(color_image, (int(predicted_x), int(predicted_y)), 2, (255, 255, 0), 2)
                        # hand_x_pred, hand_y_pred, hand_z_pred = get_coordinate(predicted_x, predicted_y, depth_image_gray)
                        # print(f'hand_x_pred2d = {hand_x_pred}, hand_y_pred2d = {hand_y_pred}, hand_z_pred = {hand_z_pred}')
                        
                        # 3D KF
                        pred3_x, pred3_y, pred3_z = kfobj3d.estimamte_3d(hand_x, hand_y, hand_z)

                        #convert real world coordinates in pixels to show the dot in image
                        kf_x, kf_y = get_pixels(pred3_x, pred3_y, pred3_z)
                        if (kf_x - 25) < color_image.shape[0] and kf_x > 25 and (kf_y - 25) < color_image.shape[0] and kf_y > 25:
                           cv2.circle(color_image, (int(kf_x), int(kf_y)), 2, (255, 255, 0), 2)
                        
                        # show the results to compare real coordinates with KF coordinates
                        print(f'hand_x = {hand_x}, hand_y = {hand_y}, hand_z = {hand_z}')
                        print(f'hand_x_pred3d = {pred3_x}, hand_y_pred3d = {pred3_y}, hand_z_pred3d = {pred3_z}')  




    # Flip the image horizontally for a selfie-view display.
    # generate_video()
    cv2.imshow('test',color_image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
rgb_cap.release()
depth_cap.release()