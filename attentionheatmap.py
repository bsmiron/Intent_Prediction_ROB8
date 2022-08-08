import numpy as np
from scipy import signal


# Class for handling the heatmap. self.map is where the heatmap lives, with a lot of variables for construction
# and run-time settings. Defaults are to be set to the experimentally found values.
class AttentionHeatMap:
    def __init__(self, dim, discountingFactor=0.943, KernelLength=None, KernelGain=1, GaussianSigma=None,
                 GaussianMean=None):
        # 0.988 is half-life of 60 discounts
        # 0.954 is half-life of 15 discounts
        # 0.943 is half-life of 12  discounts i.e. a 1/5 of a second
        if GaussianSigma is None:
            GaussianSigma = 9.5
        if GaussianMean is None:
            GaussianMean = 15.63
        if KernelLength is None:
            KernelLength = 21
        self.map = np.full([dim[0], dim[1]], 0.0)
        self.currentGazePoint = [15, 15]
        self.currentGazeConfidence = 0
        self.pastDiscountFactor = discountingFactor
        self.Gain = KernelGain
        self.Mean = GaussianMean
        self.Sigma = GaussianSigma
        self.KernelLength = KernelLength
        self.Kernel = np.ones([KernelLength, KernelLength], int)
        self.constructKernel()

    # Construct gaussian kernel for updating the heatmap around detections.
    # Run this everytime kernel parameters change.
    def constructKernel(self):
        kern1d = signal.gaussian(self.KernelLength, std=self.Sigma).reshape(self.KernelLength, 1)
        kern2d = np.outer(kern1d, kern1d)
        self.Kernel = (kern2d / kern2d.sum()) * self.Gain
        # print(kern2d.sum())
        return self.Kernel

    # Discount all values in the map by the past discount factor. This ensures old detections go away.
    def pastDiscountingWholeMap(self):
        self.map = self.map * self.pastDiscountFactor
        return self.map

    # Generate a region of interest around the current detected gaze point, in which the kernel is used
    # to increment values. This is how measurements are logged in the heatmap. Purely additive on it's own.
    def attentionScoreUpdateWholeMap(self):
        lower_y = int((self.currentGazePoint[0] - int(np.floor(self.KernelLength / 2))))
        upper_y = int((self.currentGazePoint[0] + int(np.floor((self.KernelLength + 1) / 2))))
        lower_x = int((self.currentGazePoint[1] - int(np.floor(self.KernelLength / 2))))
        upper_x = int((self.currentGazePoint[1] + int(np.floor((self.KernelLength + 1) / 2))))
        ROI = self.map[lower_y:upper_y, lower_x:upper_x]
        ROI_added = np.add(ROI, self.Kernel * self.currentGazeConfidence)
        self.map[lower_y:upper_y, lower_x:upper_x] = ROI_added
        return self.map

    # Using the specified gaze data update with the above function.
    def gazePointAndScoreUpdateWholeMap(self, gazePointAndConfidence):
        self.currentGazePoint[0] = gazePointAndConfidence[0]
        self.currentGazePoint[1] = gazePointAndConfidence[1]
        self.currentGazeConfidence = gazePointAndConfidence[2]
        return self.attentionScoreUpdateWholeMap()

    # return the sum of a region of interest. Typically this would be the object detection location, with a parameter
    # for setting a square radius around the center.
    def sumOfSubsection(self, subsection, heightWidth=None):
        if heightWidth is None:
            heightWidth = self.KernelLength
        lower_y = int((subsection[1] - int(np.floor(heightWidth / 2))))
        upper_y = int((subsection[1] + int(np.floor((heightWidth + 1) / 2))))
        lower_x = int((subsection[0] - int(np.floor(heightWidth / 2))))
        upper_x = int((subsection[0] + int(np.floor((heightWidth + 1) / 2))))
        ROI = self.map[lower_y:upper_y, lower_x:upper_x]
        SumInSubsection = ROI.sum()
        return SumInSubsection
