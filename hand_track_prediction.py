# from numpy.core.arrayprint import array2string
# from pickle import TRUE
import numpy as np
import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D

F = 640
Sx = 1
Sy = 1
FX = -F / Sx
FY = -F / Sy
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

    def estimate_2d(self, pixel_x, pixel_y):
        measured = np.array([[np.float32(pixel_x)], [np.float32(pixel_y)]])
        self.kf.correct(measured)
        predicted = self.kf.predict()
        int_predicted = predicted.astype(int)
        return int_predicted[0], int_predicted[1]


class KalmanFilter3D:
    def __init__(self, delta_t=1):
        self.kf = cv2.KalmanFilter(6, 3)
        self.delta_t = delta_t

        self.kf.measurementMatrix = np.array([[1, 0, 0, 0, 0, 0],
                                              [0, 1, 0, 0, 0, 0],
                                              [0, 0, 1, 0, 0, 0]], np.float32)

        self.kf.transitionMatrix = self.constructTransitionMatrix()

        # System (A) covariance matrix the lower the value the heigher the trust
        self.kf.processNoiseCov = np.array([[1, 0, 0, 0, 0, 0],
                                            [0, 1, 0, 0, 0, 0],
                                            [0, 0, 1, 0, 0, 0],
                                            [0, 0, 0, 1, 0, 0],
                                            [0, 0, 0, 0, 1, 0],
                                            [0, 0, 0, 0, 0, 1]], np.float32)

        # Measurement (H) covariance matrix the lower the value the heigher the trust
        self.kf.measurementNoiseCov = np.array([[1, 0, 0],
                                                [0, 1, 0],
                                                [0, 0, 1]], np.float32) * 0.1

    def constructTransitionMatrix(self):
        return np.array([[1, 0, 0, self.delta_t, 0, 0],
                         [0, 1, 0, 0, self.delta_t, 0],
                         [0, 0, 1, 0, 0, self.delta_t],
                         [0, 0, 0, 1, 0, 0],
                         [0, 0, 0, 0, 1, 0],
                         [0, 0, 0, 0, 0, 1]], np.float32)

    def estimate_3d(self, camera_frame_x, camera_frame_y, camera_frame_z):
        # prediction
        measured = np.asanyarray([camera_frame_x, camera_frame_y, camera_frame_z]).astype("float32")
        self.kf.correct(measured)

        # correction
        predicted = self.kf.predict().astype("int16")
        return predicted[0][0], predicted[1][0], predicted[2][0]


def get_coordinate(POI, depth_image, matrix=CamMatrix, shittyRecording=False):
    if shittyRecording:
        Z = depth_image[POI[1], POI[0]] * 40
    else:
        Z = depth_image[POI[1], POI[0]]
    u = POI[0] * Z
    v = POI[1] * Z
    X = (u - matrix[0, 2] * Z) / (matrix[0, 0])
    Y = (v - matrix[1, 2] * Z) / (matrix[1, 1])
    return [int(X), int(Y), int(Z)]


def get_pixels(xyz):
    pixel_u = 0
    pixel_v = 0
    uvw = np.matmul(CamMatrix, xyz)
    # print(uvw)
    # print("uvw: ", uvw)
    if uvw[2] != 0:
        # pixel_u = color_image.shape[1] - uvw[0]/uvw[2]
        # pixel_v = color_image.shape[0] - uvw[1]/uvw[2]
        pixel_u = uvw[0] / uvw[2]
        pixel_v = uvw[1] / uvw[2]

    return int(pixel_u), int(pixel_v)


# Check if the path is correct
rgb_cap = cv2.VideoCapture('depth_video_kf/project_color.avi')
depth_cap = cv2.VideoCapture('depth_video_kf/project_color_depth.avi')

# Check if I'm capturing
if not rgb_cap.isOpened() or not depth_cap.isOpened():
    print('Problem with captureing frames, procede further investigations')

# MediaPipe Magic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

kfobj2d = KalmanFilter2D()
kfobj3d = KalmanFilter3D()
kfupdate3D = KalmanFilter3D()
kfuupdate3D = KalmanFilter3D()

measured_points = []
predicted_points = []
predicted_points_update1 = []
predicted_points_update2 = []
velocities = []
x_line = []
y_line = []
z_line = []

frame = 0

d2_measured = []
d2_predicted = []
d2_predicted1 = []
d2_predicted2 = []
kf_points = []

with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while rgb_cap.isOpened() and depth_cap.isOpened():
        # print(rgb_cap.isOpened(), depth_cap.isOpened())
        success, color_image = rgb_cap.read()
        _, depth_image = depth_cap.read()
        if depth_image is None or color_image is None:
            break
        depth_image_gray = cv2.cvtColor(depth_image, cv2.COLOR_RGB2GRAY)
        if not success or not _:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            break

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        color_image.flags.writeable = False
        # color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        results = hands.process(color_image)

        # Draw the hand annotations on the image.
        color_image.flags.writeable = True
        # color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                # mp_drawing.draw_landmarks(
                # color_image,
                # hand_landmarks,
                # mp_hands.HAND_CONNECTIONS,
                # mp_drawing_styles.get_default_hand_landmarks_style(),
                # mp_drawing_styles.get_default_hand_connections_style())

                for id, lm in enumerate(hand_landmarks.landmark):
                    # print(id,lm) id = type of landmark; lm coordinates of the landmark
                    h, w, c = color_image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    if id == 9:  # and (cx - 20) < color_image.shape[0] and cx > 20 and (cy - 20) < color_image.shape[1] and cy > 20 :
                        # print(cx, cy)
                        update = 0
                        cv2.circle(color_image, (cx, cy), 2, (255, 0, 255), 2)
                        # print([cx, cy])
                        d2_measured.append([cx, cy])
                        hand_x, hand_y, hand_z = get_coordinate([cx, cy], depth_image_gray, shittyRecording=True)
                        measured_points.append([hand_x, hand_y, hand_z])
                        # print("Hand: ", hand_x, hand_y, hand_z)

                        # 3D KF
                        pred3_x, pred3_y, pred3_z = kfobj3d.estimate_3d(hand_x, hand_y, hand_z)
                        # convert real world coordinates in pixels to show the dot in image
                        XYZ1_pred = np.asanyarray([pred3_x, pred3_y, pred3_z, 1])
                        predicted_points.append(XYZ1_pred[:-1])

                        # Future update estimation
                        if update == 0:
                            # print(pred3_x, pred3_y, pred3_z)

                            pred3_1_x, pred3_1_y, pred3_1_z = kfupdate3D.estimate_3d(pred3_x, pred3_y, pred3_z)
                            XYZ1_1_pred = np.asanyarray([pred3_1_x, pred3_1_y, pred3_1_z, 1])
                            predicted_points_update1.append(XYZ1_1_pred[:-1])
                            up_x, up_y = get_pixels(XYZ1_1_pred)
                            cv2.circle(color_image, (int(up_x), int(up_y)), 2, (255, 60, 0), 2)
                            d2_predicted1.append([up_x, up_y])
                            update = 1

                            if update == 1:
                                pred3_2_x, pred3_2_y, pred3_2_z = kfuupdate3D.estimate_3d(pred3_1_x, pred3_1_y,
                                                                                          pred3_1_z)
                                XYZ1_2_pred = np.asanyarray([pred3_2_x, pred3_2_y, pred3_2_z, 1])
                                predicted_points_update2.append(XYZ1_2_pred[:-1])
                                up_x_2, up_y_2 = get_pixels(XYZ1_2_pred)
                                cv2.circle(color_image, (int(up_x_2), int(up_y_2)), 2, (255, 165, 0), 2)
                                d2_predicted2.append([up_x_2, up_y_2])
                                #
                                # kf_points.append(XYZ1_2_pred[:-1])
                                # print(kf_points[0, 1])
                                # for fps in range(1, 28):
                                #
                                #     kf_points[fps, 0], kf_points[fps, 1], kf_points[fps, 2] = kfupdate3D.estimate_3d(
                                #                                                              kf_points[fps-1, 0],
                                #                                                              kf_points[fps-1, 1],
                                #                                                              kf_points[fps-1, 2])
                                # print(kf_points[28][0], kf_points[28, 1], kf_points[28, 2])
                                # print(' ')
                                update = 2
                        # print(XYZ1_pred)
                        uvw = np.matmul(CamMatrix, XYZ1_pred)
                        # print(uvw)
                        # print("uvw: ", uvw)
                        if uvw[2] != 0:
                            # pixel_u = color_image.shape[1] - uvw[0]/uvw[2]
                            # pixel_v = color_image.shape[0] - uvw[1]/uvw[2]
                            pixel_u = uvw[0] / uvw[2]
                            pixel_v = uvw[1] / uvw[2]
                            cv2.circle(color_image, (int(pixel_u), int(pixel_v)), 2, (255, 255, 0), 2)
                            d2_predicted.append([int(pixel_u), int(pixel_v)])

        # print(frame)

        cv2.imshow("color", color_image)
        frame += 1
        # cv2.imwrite("test.jpg", color_image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

# figg = plt.figure()
# axx = plt.axes()

# d2_measured = np.asanyarray(d2_measured)[10:]
# d2_predicted = np.asanyarray(d2_predicted)[10:]
# d2_predicted1 = np.asanyarray(d2_predicted1)[10:]
# d2_predicted2 = np.asanyarray(d2_predicted2)[10:]

# axx.scatter(d2_measured[40][0], d2_measured[40][1], 'pink')
# axx.scatter(d2_predicted[40][0], d2_predicted[40][1], 'green')
# axx.scatter(d2_predicted1[40][0], d2_predicted1[40][1], 'blue')
# axx.scatter(d2_predicted2[40][0], d2_predicted2[40][1], 'orange')

# axx.set_xlabel('x')
# axx.set_ylabel('y')

fig = plt.figure()
ax = plt.axes(projection='3d')
# ax = fig.ax_subplot(projection='3d')

array_measured = np.asanyarray(measured_points)[10:]
array_predicted = np.asanyarray(predicted_points)[10:]
array_predicted_update1 = np.asanyarray(predicted_points_update1)[10:]
array_predicted_update2 = np.asanyarray(predicted_points_update2)[10:]

# Extract data for calculating errors

# DF = pd.DataFrame(array_predicted)
# DF.to_csv("array_predicted.csv")
#
# DF = pd.DataFrame(array_predicted_update1)
# DF.to_csv("array_predicted_update1.csv")

# print(array_measured[140][0], array_measured[140][1], array_measured[140][2])
# one frame

# ax.scatter3D(array_measured[140, 0], array_measured[140, 1], array_measured[140, 2], 'pink', label='hand position k')
# ax.scatter3D(array_predicted[140, 0], array_predicted[140, 1], array_predicted[140, 2], 'turquoise',
#              label='prediction k+1')
# ax.scatter3D(array_predicted_update1[140, 0], array_predicted_update1[140, 1], array_predicted_update1[140, 2], 'blue',
#              label='prediction k+2')
# ax.scatter3D(array_measured[44, 0], array_measured[44, 1], array_measured[44, 2], 'pink',
#              label='hand position k+3')
#
# ax.scatter3D(array_predicted_update2[41, 0], array_predicted_update2[41, 1], array_predicted_update2[183, 2],
#              'orange', label='prediction k+3')

# ax.plot3D(array_measured[:, 0], array_measured[:, 1], array_measured[:, 2], 'blue', label="hand trajectory")

# ax.plot3D(array_predicted[:, 0], array_predicted[:, 1], array_predicted[:, 2], 'green', label="k+1 trajectory")
# ax.plot3D(array_predicted[:, 0], array_predicted[:, 1], array_predicted[:, 2], 'green', label="k+1 trajectory")
# ax.plot3D(array_predicted_update1[:, 0], array_predicted_update1[:, 1], array_predicted_update1[:, 2], 'yellow', label="k+2 trajectory")
# ax.plot3D(array_predicted_update2[:, 0], array_predicted_update2[:, 1], array_predicted_update2[:, 2], 'red', label="k+3 trajectory")
# ax.scatter([array_measured[:, 0], array_predicted[:, 0]],[array_measured[:, 1], array_predicted_update2[:, 1]],
#            [array_predicted_update2[:, 2], array_predicted_update2[:, 2]], c = "red", s=1)
#
# line_x = np.stack((array_measured[:, 0], array_predicted[:, 0]), axis=-1)
# # print(line_x)
# line_y = np.stack((array_measured[:, 1], array_predicted[:, 1]), axis=-1)
# # print(line_y)
# line_z = np.stack((array_measured[:, 2], array_predicted[:, 2]), axis=-1)
# # print(line_z)

# for x_measured, x_predicted in array_measured[:, 0], array_predicted[:,0]:
#     x_line = [x_measured, x_predicted]
#     print(x_line)


# ax.plot3D(line_x, line_y, line_z, color = "black")


# ax.set_xlabel("x in mm")
# ax.set_ylabel("y in mm")
# ax.set_zlabel("Depth in mm")
# plt.legend(loc="upper left")
# plt.show()
rgb_cap.release()
depth_cap.release()