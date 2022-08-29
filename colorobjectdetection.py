import numpy as np
import cv2 as cv
import glob


# import matplotlib.pyplot as plt

# red
red_lower_range = np.array([171, 102, 102])
red_upper_range = np.array([9, 255, 255])
# orange
orange_lower_range = np.array([10, 102, 102])
orange_upper_range = np.array([20, 255, 255])
# yellow
yellow_lower_range = np.array([19, 102, 102])
yellow_upper_range = np.array([31, 255, 255])
# green
green_lower_range = np.array([59, 102, 102])
green_upper_range = np.array([76, 255, 255])
# blue
blue_lower_range = np.array([88, 102, 102])
blue_upper_range = np.array([106, 255, 255])
# purple
purple_lower_range = np.array([119, 102, 102])
purple_upper_range = np.array([133, 255, 255])
# black
black_lower_range = np.array([0, 0, 0])
black_upper_range = np.array([180, 64, 64])
color_dict = {'Red': [red_lower_range, red_upper_range],
              'Orange': [orange_lower_range, orange_upper_range],
              'Yellow': [yellow_lower_range, yellow_upper_range],
              'Green': [green_lower_range, green_upper_range],
              'Blue': [blue_lower_range, blue_upper_range],
              'Purple': [purple_lower_range, purple_upper_range],
              'Black': [black_lower_range, black_upper_range]}


class ObjectColorDetector:
    def __init__(self, targets=None, K=7, T_sl=1000, T_su=4000):
        self.targets_c_h_s = {}
        self.kernelLength = K
        self.sizeThresholdDefault = [T_sl, T_su]
        self.openKernel = np.ones((self.kernelLength, self.kernelLength), np.uint8)
        self.closeKernel = np.ones((self.kernelLength*2, self.kernelLength*2), np.uint8)
        self.histograms_available = False
        sum_of_widths = 0
        if targets is None:
            keys = ['Red', 'Orange', 'yellow', 'Green', 'Blue', 'Purple', 'Black']
            target_dict = {}
            for key in keys:
                target_dict.update({key: [color_dict[key], [], self.sizeThresholdDefault]})
            print("No histograms available for precise search.")

            self.targets_c_h_s = target_dict
        else:
            for imagePath in targets:
                key = imagePath[:-4]
                target_img = cv.imread(imagePath)
                sum_of_widths += target_img.shape[1]
                target_hsv = cv.cvtColor(target_img, cv.COLOR_BGR2HSV)
                # histogram generation
                if key == 'Black':
                    histogram = cv.calcHist([target_hsv], [1, 2], None, [64, 64], [0, 256, 0, 256])
                else:
                    histogram = cv.calcHist([target_hsv], [0, 1], None, [45, 64], [0, 180, 0, 256])
                cv.normalize(histogram, histogram, alpha=0, beta=1, norm_type=cv.NORM_MINMAX)
                # size measurement
                if key == 'Red':
                    mask1 = cv.inRange(target_hsv, np.array([
                        0, color_dict[key][0][1], color_dict[key][0][2]]),
                                       color_dict[key][1])
                    mask2 = cv.inRange(target_hsv, color_dict[key][0],
                                       np.array(
                                           [180, color_dict[key][1][1], color_dict[key][1][2]]))
                    threshold_image = cv.bitwise_or(mask1, mask2)
                else:
                    threshold_image = cv.inRange(target_hsv, color_dict[key][0],
                                                 color_dict[key][1])
                cn, h = cv.findContours(threshold_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
                M00 = max(cv.moments(element)['m00'] for element in cn)
                sizeThresholds = [M00/2, M00*2]
                # update with final values
                self.targets_c_h_s.update({key: [color_dict[key], histogram, sizeThresholds]})
            self.histograms_available = True
            self.average_widths = np.floor(sum_of_widths / len(targets))

    def searchForAllObjects(self, image):
        best_matches_center_dict = {}
        hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        m_blurred_image = cv.medianBlur(hsv_image, self.kernelLength)
        for target in self.targets_c_h_s:
            best_matches_center_dict.update({target: self.searchForOneColor(m_blurred_image, target)})
        return best_matches_center_dict

    def searchForOneColor(self, hsv_blurred_image, key):
        if key == 'Red':
            mask1 = cv.inRange(hsv_blurred_image, np.array([
                0, self.targets_c_h_s[key][0][0][1], self.targets_c_h_s[key][0][0][2]]), self.targets_c_h_s[key][0][1])
            mask2 = cv.inRange(hsv_blurred_image, self.targets_c_h_s[key][0][0],
                               np.array([180, self.targets_c_h_s[key][0][1][1], self.targets_c_h_s[key][0][1][2]]))
            threshold_image = cv.bitwise_or(mask1, mask2)
        else:
            threshold_image = cv.inRange(hsv_blurred_image, self.targets_c_h_s[key][0][0], self.targets_c_h_s[key][0][1])
        opened_image = cv.morphologyEx(threshold_image, cv.MORPH_OPEN, self.openKernel)
        closed_image = cv.morphologyEx(opened_image, cv.MORPH_CLOSE, self.closeKernel)
        cn, hierarchy = cv.findContours(closed_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        possible_match_center = list()
        for contour in cn:
            M = cv.moments(contour)
            if self.targets_c_h_s[key][2][0] < M['m00'] < self.targets_c_h_s[key][2][1]:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                possible_match_center.append([cx, cy])

        if len(possible_match_center) > 1:
            similarities = {(-1, -1): "delete"}
            # print(possible_match_center)
            for detectionCoordinate in possible_match_center:
                lower_y = int((detectionCoordinate[0] - int(np.floor(self.average_widths / 2))))
                upper_y = int((detectionCoordinate[0] + int(np.floor((self.average_widths + 1) / 2))))
                lower_x = int((detectionCoordinate[1] - int(np.floor(self.average_widths / 2))))
                upper_x = int((detectionCoordinate[1] + int(np.floor((self.average_widths + 1) / 2))))
                ROI = hsv_blurred_image[lower_x:upper_x, lower_y:upper_y, :]
                detectionHistogram = cv.calcHist([ROI], [0, 1], None, [45, 64], [0, 180, 0, 256])
                if key == 'Black':
                    detectionHistogram = cv.calcHist([ROI], [1, 2], None, [64, 64], [0, 256, 0, 256])
                cv.normalize(detectionHistogram, detectionHistogram, alpha=0, beta=1, norm_type=cv.NORM_MINMAX)
                similarity_score = cv.compareHist(self.targets_c_h_s[key][1], detectionHistogram, cv.HISTCMP_BHATTACHARYYA)
                # print(similarity_score)
                key_value_pair = {tuple(detectionCoordinate): similarity_score}
                similarities.update(key_value_pair)
            del similarities[(-1, -1)]
            best_match_center = min(similarities, key=similarities.get)
            best_match_center = [best_match_center[0], best_match_center[1]]  # this line is purely an as-array
            return best_match_center
        elif len(possible_match_center) == 1:
            return possible_match_center[0]
        else:
            return -1


detector = ObjectColorDetector(glob.glob("*.png"))
print(detector.targets_c_h_s.keys())
# test_image = cv.imread(r'pupil_test_003/00200.jpg')
test_image = cv.imread('tests_and_results/test_pictures_2022_05_21/data/data1.jpeg')
object_centers = detector.searchForAllObjects(test_image)
print(object_centers)
for center in object_centers.values():
    if len(center) == 1:
        center = center[0]
    cv.circle(test_image, center, 0, [255, 255, 255], 5)
    cv.circle(test_image, center, 2, 0, 1)
cv.imshow("centers", test_image)
cv.waitKey()

