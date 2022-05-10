#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

#include <opencv2/imgproc.hpp>
#include <opencv2/core.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/core/types_c.h>

using namespace cv;

int mainzs()
{
	Mat left_img = imread("pattern_left.png", IMREAD_GRAYSCALE);
	if (left_img.empty())
	{
		printf("Could not open or find pattern_left.png\n");
		waitKey(0); //wait for any key press
		return -1;
	}

	Mat right_img = imread("pattern_right.png", IMREAD_GRAYSCALE);
	if (right_img.empty())
	{
		printf("Could not open or find pattern_right.png\n");
		waitKey(0); //wait for any key press
		return -1;
	}

	namedWindow("left", WINDOW_NORMAL);
	imshow("left", left_img);

	namedWindow("right", WINDOW_NORMAL);
	imshow("right", right_img);
	waitKey(0);

	Size patternsize(4, 4); //interior number of corners
	std::vector<Point2f> corners; //this will be filled by the detected corners

	bool patternfound = findChessboardCorners(left_img, patternsize, corners,
		CALIB_CB_ADAPTIVE_THRESH + CALIB_CB_NORMALIZE_IMAGE
		+ CALIB_CB_FAST_CHECK);

	printf("Pattern has been found %d\n", patternfound ? 1 : 0);

	if (patternfound)
	{
		int count = 0;
		for (Point2f point : corners)
		{

			printf("corner %2d at x: %f y: %f \n",count++, point.x, point.y);
		}
		//Mat result;
		cornerSubPix(left_img, corners, Size(11, 11), Size(-1, -1),
			TermCriteria(CV_TERMCRIT_EPS + CV_TERMCRIT_ITER, 30, 0.1));

		drawChessboardCorners(left_img, patternsize, Mat(corners), patternfound);

		namedWindow("left_with_corners", WINDOW_NORMAL);
		imshow("left_with_corners", left_img);
		waitKey(0);
	}


	return 1;
}