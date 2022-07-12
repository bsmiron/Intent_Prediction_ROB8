import pyrealsense2 as rs
import numpy as np
import cv2 as cv
import mediapipe as mp
import math
import time

# red
red_lower_range = np.array([175, 50, 100])
red_upper_range = np.array([5, 255, 255])

# orange
orange_lower_range = np.array([10, 50, 100])
orange_upper_range = np.array([20, 255, 255])

# yellow
yellow_lower_range = np.array([22, 50, 100])
yellow_upper_range = np.array([27, 255, 255])

# green
green_lower_range = np.array([68, 50, 100])
green_upper_range = np.array([73, 255, 255])

# blue 140 - 180
blue_lower_range = np.array([101, 50, 100])
blue_upper_range = np.array([110, 255, 255])

# purple
purple_lower_range = np.array([119, 50, 0])
purple_upper_range = np.array([133, 255, 255])

# color_image = cv.imread("good.jpeg")
# color_image = cv.imread("alberto1.png")

color_image = cv.imread("smoltest.png")
color_image = cv.resize(color_image, (1600, 600))

# color_image = cv.resize(color_image, (640, 480))
color_image_hsv = cv.cvtColor(color_image, cv.COLOR_BGR2HSV)
# blurred_color_image_hsv = cv.GaussianBlur(color_image_hsv, (9, 9), 0)


def get_color(img_hsv, lower, upper, isitred=False):
    if isitred:
        kernel = np.ones((2, 2), np.uint8)
        kernel_1 = np.ones((5, 5), np.uint8)
        mask1 = cv.inRange(img_hsv, np.array([0, lower[1], lower[2]]), upper)
        mask1 = cv.morphologyEx(mask1, cv.MORPH_OPEN, kernel)
        mask1 = cv.morphologyEx(mask1, cv.MORPH_CLOSE, kernel_1)
        mask2 = cv.inRange(img_hsv, lower, np.array([180, upper[1], upper[2]]))
        mask2 = cv.morphologyEx(mask2, cv.MORPH_OPEN, kernel)
        mask2 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernel_1)
        binary_image = cv.bitwise_or(mask1, mask2)
    else:
        kernel = np.ones((7, 7), np.uint8)
        kernel_1 = np.ones((8, 8), np.uint8)
        mask = cv.inRange(img_hsv, lower, upper)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel_1)
        binary_image = mask
    cn, hierarchy = cv.findContours(binary_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    center_points = list()
    i = 0
    x = 0
    y = 0
    z = 0
    # print(len(cn))
    while i < len(cn):
        M = cv.moments(cn[i])
        if M['m00'] != 0 and 50 < M['m00']:
            cv.drawContours(color_image, cn, -1, (0, 255, 0), 3)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            # center_points += [int(xg+np.floor(wg/2)), int(yg+np.floor(hg/2))]
            center_points.append([cx, cy])
        i += 1
    # print(center_points)
    for center in center_points:
        # print(center)
        cv.circle(color_image, tuple(center), 0, 0, 5)
    return binary_image, center_points


all_contours = 0
img_bin1, contour_stuff = get_color(color_image_hsv, red_lower_range, red_upper_range, isitred=True)
all_contours += len(contour_stuff)
red_contours = contour_stuff
img_bin2, contour_stuff = get_color(color_image_hsv, orange_lower_range, orange_upper_range, isitred=False)
all_contours += len(contour_stuff)
orange_contours = contour_stuff
img_bin3, contour_stuff = get_color(color_image_hsv, yellow_lower_range, yellow_upper_range, isitred=False)
all_contours += len(contour_stuff)
yellow_contours = contour_stuff
img_bin4, contour_stuff = get_color(color_image_hsv, green_lower_range, green_upper_range, isitred=False)
all_contours += len(contour_stuff)
green_contours = contour_stuff
img_bin5, contour_stuff = get_color(color_image_hsv, blue_lower_range, blue_upper_range, isitred=False)
all_contours += len(contour_stuff)
blue_contours = contour_stuff
img_bin6, contour_stuff = get_color(color_image_hsv, purple_lower_range, purple_upper_range, isitred=False)
all_contours += len(contour_stuff)
purple_contours = contour_stuff
print(all_contours)

i = 0
for contour in [red_contours, orange_contours, yellow_contours, green_contours, blue_contours, purple_contours]:
    i += 1
    if len(contour) != 1:
        print(i, "and the content:", contour)

# mask1, center_points1 = get_color(color_image_hsv, red_top_lower_range, red_top_upper_range)
# mask1 = cv.resize(mask1, (640, 480))
# mask2, center_points2 = get_color(color_image_hsv, red_bottom_lower_range, red_bottom_upper_range)
# mask2 = cv.resize(mask2, (640, 480))
# color_image = cv.resize(color_image, (640, 480))
# combined = cv.bitwise_or(mask1, mask2)
# kernel = np.ones((5, 5), np.uint8)
# kernel_1 = np.ones((6, 6), np.uint8)
# combined = cv.morphologyEx(combined, cv.MORPH_OPEN, kernel)
# combined = cv.morphologyEx(combined, cv.MORPH_CLOSE, kernel_1)

# cv.imshow("mask1", mask1)
# cv.imshow("mask2", mask2)
# cv.imshow("result", combined)
cv.imshow("binary2", img_bin2)
cv.imshow("binary3", img_bin3)
cv.imshow("binary5", img_bin5)
cv.imshow("original", color_image)
cv.waitKey()
