#include "VisionManager.h"
#include <vector>
#include <iostream>
#include <opencv2/highgui.hpp>
#include <opencv2/calib3d.hpp>
#include <librealsense2/rs.hpp>

int main()
{
	VisionManager VisManager = VisionManager();

	cv::Mat left_img, right_img;
	std::vector<cv::Point2f> corners_left, corners_right;
	int map[40][2];
	
	/* Chose a value between 0 , 1 and 2. This refers to the image pair the OFFLINE_MODE will use. Once
	 * I fix everything, this will be 0 or 1 depending on which camera we want to use. Till then, you can 
	 * use the OFFLINE_MODE which mimics taking a pair of images from the camera. 
	 */
	int image_pair = 0;

	bool found_pattern = VisManager.get_patten_info_from_device(image_pair, left_img, corners_left, right_img, corners_right, map);
	std::cout << "error" << std::endl;
	
	printf("\nFound pattern in both: %s\n", found_pattern ? "true" : "false");
	printf("Corners in the left image:\n");
	int count = 0;
	for (cv::Point2f point : corners_left)
	{
		printf("corner %2d at col: %f row: %f \n", count++, point.x, point.y);
	}

	printf("\nCorners in the right image:\n");
	count = 0;
	for (cv::Point2f point : corners_right)
	{
		printf("corner %2d at col: %f row: %f \n", count++, point.x, point.y);
	}
	rs2_intrinsics intrinsics = VisManager.get_intrinsics_from_device(image_pair);
	std::cout << "Camera intrinsics:\n";
	std::cout << "center of projection x = " << intrinsics.ppx << "\n";
	std::cout << "center of projection y = " << intrinsics.ppy << "\n";
	std::cout << "focal length x = " << intrinsics.fx << "\n";
	std::cout << "focal length y = " << intrinsics.fy << "\n";
	std::cout << "image rows = " << intrinsics.width << "\n";
	std::cout << "image columns = " << intrinsics.height << "\n";
	std::cout << "distortion model type = " << intrinsics.model << "\n";
	for (int i = 0; i < 5; i++)
	{
		std::cout << "distortion model coefficients[ " << i << "] = " << intrinsics.coeffs[i] << "\n";
	}
	// Get the depth frame's dimensions
	//float Width = WIDTH;
	//float height = HEIGHT;

	// Query the distance from the camera to the object in the center of the image
	//float dist_to_center = depth.get_distance(Width / 2, height / 2);
	//std::cout << "Distance to depth image center = " << dist_to_center << "\n";

	cv::Mat dst;
	hconcat(left_img, right_img, dst);
	cv::namedWindow("infrared_stereo_pair", cv::WINDOW_NORMAL);
	imshow("infrared_stereo_pair", dst);

	cv::drawChessboardCorners(left_img, cv::Size(5,8), cv::Mat(corners_left), true);
	cv::drawChessboardCorners(right_img, cv::Size(5, 8), cv::Mat(corners_right), true);

	cv::Mat dst_corner;
	hconcat(left_img, right_img, dst_corner);
	cv::namedWindow("infrared_stereo_pair_w_corners", cv::WINDOW_NORMAL);
	imshow("infrared_stereo_pair_w_corners", dst_corner);
	cv::imwrite("alberto_points.png", dst_corner);
	cv::waitKey(0);


	return 1;
}