import numpy as np
import cv2 as cv
import pandas as pd
import os
import glob
import time
from colorobjectdetection import ObjectColorDetector
from attentionheatmap import AttentionHeatMap

# Let's take the video and see if we can find the appropriate objects consistently
video = cv.VideoCapture(r'pupil_test_003/pupil_above_brick_test.mp4')
detector = ObjectColorDetector(targets=glob.glob("*.png"))
heatmap = AttentionHeatMap([720, 1280], KernelLength=31, KernelGain=10)

result = cv.VideoWriter('objects_detected.avi',
                        cv.VideoWriter_fourcc(*'MJPG'),
                        30, [1280, 720])
heatmap_result = cv.VideoWriter('heatmap.avi',
                                cv.VideoWriter_fourcc(*'FFV1'),
                                30, [1280, 720], isColor=False)
gaze_raw_csv = pd.read_csv(r'gaze_positions_pupil_test_003.csv')
gaze_df = pd.DataFrame(gaze_raw_csv,
                       columns=['gaze_timestamp', 'world_index', 'norm_pos_x', 'norm_pos_y', 'confidence'])
gaze_df['norm_pos_x'] = gaze_df['norm_pos_x'].multiply(heatmap.map.shape[1]).round().astype(int)
gaze_df['norm_pos_y'] = gaze_df['norm_pos_y'].multiply(heatmap.map.shape[0]).round().astype(int).multiply(-1)
i = 0
attentionScores = {}
# cv2.putText(img, 'OpenCV', (10, 500), font, 4, (255, 255, 255), 2, cv2.LINE_AA)
# https://docs.opencv.org/3.1.0/dc/da5/tutorial_py_drawing_functions.html
while video.isOpened():
    ret, frame = video.read()
    if frame is None:
        break
    object_centers = detector.searchForAllObjects(frame)
    for index, row in gaze_df.loc[gaze_df['world_index'] == i].iterrows():
        updatestuff = [row['norm_pos_y'], row['norm_pos_x'], row['confidence']]
        heatmap.gazePointAndScoreUpdateWholeMap(updatestuff)
    heatmap.pastDiscountingWholeMap()
    for center in object_centers:
        cv.circle(frame, object_centers[center], 0, [255, 255, 255], 5)
        cv.circle(frame, object_centers[center], 2, 0, 1)
        attentionScores[center] = heatmap.sumOfSubsection(object_centers[center], heightWidth=51)
    bestScore = max(attentionScores, key=attentionScores.get)
    print(bestScore)
    cv.putText(frame, bestScore, (10, 700), cv.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 2, cv.LINE_AA)
    cv.imshow("The video feed: ", frame)
    cv.imshow("the heatmap: ", heatmap.map)
    result.write(frame)
    heatmap_video_frame = np.array(heatmap.map*3)
    heatmap_result.write(heatmap_video_frame)
    i += 1
    if cv.waitKey(25) & 0xFF == ord('q'):
        break

video.release()
cv.destroyAllWindows()
