#include "VisionManager.h"

#include <vector>
#include <iostream>

#include <opencv2/highgui.hpp>
#include <opencv2/calib3d.hpp>

#include <librealsense2/rs.hpp>

#define GLOBAL_CAM_INDEX (0)
#define LOCAL_CAM_INDEX (1)
int main()
{
	VisionManager VisManager = VisionManager();
	int count = 0;
	//while (1)
	//{
		std::cout << "Iteration: " << ++count << "\n";
		cv::Mat local_left_img, local_right_img;
		std::vector<cv::Point2f> local_corners_left, local_corners_right;
		int local_map[16][2];
		bool found_pattern = VisManager.get_patten_info_from_device(LOCAL_CAM_INDEX, local_left_img, local_corners_left, local_right_img, local_corners_right, local_map);

		printf("\nLocal found pattern in both: %s\n", found_pattern ? "true" : "false");

		cv::Mat dst;
		hconcat(local_left_img, local_right_img, dst);
		cv::imwrite("local_left_img5.png", local_left_img);
		cv::imwrite("local_right_img5.png", local_right_img);
		//cv::namedWindow("infrared_stereo_pair", cv::WINDOW_NORMAL);
		//imshow("infrared_stereo_pair", dst);
		if (found_pattern)
		{
			cv::drawChessboardCorners(local_left_img, cv::Size(4, 4), cv::Mat(local_corners_left), true);
			cv::drawChessboardCorners(local_right_img, cv::Size(4, 4), cv::Mat(local_corners_right), true);


			cv::Mat local_dst_corner;
			hconcat(local_left_img, local_right_img, local_dst_corner);
			cv::namedWindow("local_infrared_stereo_pair_w_corners", cv::WINDOW_NORMAL);
			imshow("local_infrared_stereo_pair_w_corners", local_dst_corner);
		}
		//====================================================================

		cv::Mat global_left_img, global_right_img;
		std::vector<cv::Point2f> global_corners_left, global_corners_right;
		int global_map[16][2];
		found_pattern = VisManager.get_patten_info_from_device(GLOBAL_CAM_INDEX, global_left_img, global_corners_left, global_right_img, global_corners_right, global_map);

		printf("\nGlobal found pattern in both: %s\n", found_pattern ? "true" : "false");

		cv::Mat global_dst;
		hconcat(global_left_img, global_right_img, global_dst);
		cv::imwrite("global_left_img5.png", global_left_img);
		cv::imwrite("global_right_img5.png", global_right_img);
		//cv::namedWindow("infrared_stereo_pair", cv::WINDOW_NORMAL);
		//imshow("infrared_stereo_pair", global_dst);
		if (found_pattern)
		{
			cv::drawChessboardCorners(global_left_img, cv::Size(4, 4), cv::Mat(global_corners_left), true);
			cv::drawChessboardCorners(global_right_img, cv::Size(4, 4), cv::Mat(global_corners_right), true);

			cv::Mat global_dst_corner;
			hconcat(global_left_img, global_right_img, global_dst_corner);
			cv::namedWindow("global_infrared_stereo_pair_w_corners", cv::WINDOW_NORMAL);
			imshow("global_infrared_stereo_pair_w_corners", global_dst_corner);
		}

		cv::waitKey(0);
	//}


	return 1;
}