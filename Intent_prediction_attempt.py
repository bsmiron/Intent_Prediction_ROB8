import numpy as np
from scipy import signal
import cv2 as cv
import pandas as pd
import os
import glob
import subprocess
import matplotlib.pyplot as plt
plt.ion()

# Brick locations
#
# red = [np.array([0, 0, 0]), "red"]
# yellow = [np.array([10, 0, 0]), "yellow"]
# green = [np.array([0, 10, 0]), "green"]
# blue = [np.array([10, 10, 0]), "blue"]
# purple = [np.array([20, 0, 0]), "purple"]


class AttentionMap:
    def __init__(self, dim, discountingFactor=0.988, KernelLength=None, KernelGain=5, GaussianSigma=None, GaussianMean = None):
        # 0.988 is half-life of 60 updates
        if GaussianSigma is None:
            GaussianSigma = 9.5
        if GaussianMean is None:
            GaussianMean = 15.63
        if KernelLength is None:
            KernelLength = 21
        self.map = np.full([dim[0], dim[1]], 0.0)
        self.currentGazePoint = [15, 15]
        self.pastDiscountFactor = discountingFactor
        self.Gain = KernelGain
        self.Mean = GaussianMean
        self.Sigma = GaussianSigma
        self.KernelLength = KernelLength
        self.Kernel = np.ones([KernelLength, KernelLength], int)
        self.constructKernel()

    def constructKernel(self):
        # magic = np.linspace(-self.Sigma, self.Sigma, self.KernelLength + 1)
        kern1d = signal.gaussian(self.KernelLength, std=self.Sigma).reshape(self.KernelLength, 1)
        kern2d = np.outer(kern1d, kern1d)
        self.Kernel = (kern2d / kern2d.sum())
        print(kern2d.sum())
        return self.Kernel

    def pastDiscountingWholeMap(self):
        self.map = self.map * self.pastDiscountFactor
        return self.map

    def attentionScoreUpdateWholeMap(self):
        lower_y = int((self.currentGazePoint[0] - int(np.floor(self.KernelLength / 2))))
        upper_y = int((self.currentGazePoint[0] + int(np.floor((self.KernelLength + 1) / 2))))
        lower_x = int((self.currentGazePoint[1] - int(np.floor(self.KernelLength / 2))))
        upper_x = int((self.currentGazePoint[1] + int(np.floor((self.KernelLength + 1) / 2))))
        ROI = self.map[lower_y:upper_y, lower_x:upper_x]
        ROI_added = np.add(ROI, self.Kernel)
        self.map[lower_y:upper_y, lower_x:upper_x] = ROI_added
        return self.map


def whatAmIAttentionAt(gaze_location, bricks):
    minimum_of_distances = 100000000000000000
    color = "no clue"
    for Brick in bricks:
        distance_gaze_brick = np.linalg.norm(Brick[0] - gaze_location)
        if distance_gaze_brick < minimum_of_distances:
            color = Brick[1]
        minimum_of_distances = min(distance_gaze_brick, minimum_of_distances)
    closest = [minimum_of_distances, color]
    return closest


zerosMap = AttentionMap([720, 1280])
zerosMap.KernelLength = 31
zerosMap.constructKernel()

# gaze_raw_csv = pd.read_csv(r'gaze_positions_error_testing.csv')
gaze_raw_csv = pd.read_csv(r'gaze_positions_looking_at_bricks.csv')
gaze_df = pd.DataFrame(gaze_raw_csv, columns=['gaze_timestamp', 'world_index', 'norm_pos_x', 'norm_pos_y'])

# get pixel value
gaze_df['norm_pos_x'] = gaze_df['norm_pos_x'].multiply(zerosMap.map.shape[1]).round().astype(int)
gaze_df['norm_pos_y'] = gaze_df['norm_pos_y'].multiply(zerosMap.map.shape[0]).round().astype(int).multiply(-1)


# drop same world index recordings
# gaze_df = gaze_df.drop_duplicates(subset=['world_index'], keep='first').set_index('world_index')
print(gaze_df)

print(zerosMap.map.shape)

world_index_current = 0
folder = "frames_for_video_looking_at_bricks"
fig, ax = plt.subplots()
image_object = ax.imshow(zerosMap.map, interpolation=None, vmin=0, vmax=0.3)
plt.title("map")
recording = False
if recording:
    for index, row in gaze_df.iterrows():
        zerosMap.currentGazePoint = [row['norm_pos_y'], row['norm_pos_x']]
        zerosMap.attentionScoreUpdateWholeMap()
        if world_index_current != row['world_index']:
            zerosMap.pastDiscountingWholeMap()
            # stuff for making video
            image_object.set_data(zerosMap.map)
            fig.canvas.flush_events()
            plt.savefig(folder + "/file%02d.png" % world_index_current)
            print("up to: ", world_index_current)
        world_index_current = row['world_index']


#
#
#


def generate_video():
    os.chdir(folder)
    subprocess.call([
        'ffmpeg', '-framerate', '30', '-i', 'file%02d.png', '-r', '30', '-pix_fmt', 'yuv420p',
        'video_name.mp4'
    ])


# generate_video()

# plt.imshow(zerosMap.map, interpolation=None)
# plt.title("Map")
# plt.show()

# zerosMap.KernelLength = 21
# zerosMap.constructKernel()
# plt.imshow(zerosMap.Kernel, interpolation='none', )
# plt.waitforbuttonpress()


exit()

#
# zerosMap = AttentionMap([48, 64])
# # onesMap.pastDiscountingWholeMap()
# # print(onesMap.pastDiscountingWholeMap())
# zerosMap.KernelLength = 10
# zerosMap.constructKernel()
# # plt.imshow(zerosMap.Kernel, interpolation='none', )
# # plt.waitforbuttonpress()
#
# # plt.imshow(zerosMap.map, interpolation='none', )
# # plt.waitforbuttonpress()
# i = 0
# while True:
#     if input("gaze or just time? G T") == "G":
#         zerosMap.currentGazePoint = [i+15, i+15]
#         print(zerosMap.currentGazePoint)
#         zerosMap.attentionScoreUpdateWholeMap()
#     zerosMap.pastDiscountingWholeMap()
#     plt.imshow(zerosMap.map, interpolation=None)
#     plt.title("Map")
#     plt.show()
#     i += 1
#     if i > 32:
#         i = 0
