#include "VisionManager.h"
#include <vector>
#include <iostream>
#include <opencv2/highgui.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <librealsense2/rs.hpp>

#define GLOBAL_CAM_INDEX (0)
#define LOCAL_CAM_INDEX (1)

#define CAMERA_IDX (GLOBAL_CAM_INDEX)

std::vector <float> disparity;
std::vector <float> depth;
std::vector <float> azimuth;
std::vector <float> inclination;


void depth_calc(float k1_x, float k2_x, int i) {

	float focal_length = 2.0162;
	int baseline = 50;

	float x_disp = (k1_x - k2_x) * focal_length / 634.846;


	float x_depth = (focal_length * baseline) / x_disp;
	depth.push_back(x_depth);

	//std::cout << "depth for point " << i << " is = " << depth[i] << std::endl;
}
// 848x 480y actually 1280 by 800 in the images somehow
//    depth imager  // 74 horizontal FOV;   62 vertical FOV;    88 diagonal FOV
// standard imager  // 69 horizontal FOV; 42.5 vertical FOV;    77 diagonal FOV
//  WIDE imager   // 91.2 horizontal FOV; 65.5 vertical FOV; 100.6 diagonal FOV
float degToRad(float deg) {
	float rad = deg * 3.141592 / 180;
	return rad;
}
float radToDeg(float rad) {
	float deg = rad / 3.141592 * 180;
	return deg;
}

void angle_calc(int x1, int y1, int x2, int y2, int i) {

	float x_angle = ((x1 - 640) * (91.2 / 1280) + (x1 - 640) * (91.2 / 1280)) / 2;
	float y_angle = (((y1 - 400) * (65.5 / 800)) + ((y1 - 400) * (65.5 / 800))) / 2;
	azimuth.push_back(x_angle);
	inclination.push_back(y_angle);
	/*
	std::cout << "x angle for point " << i << " is = " << x_angle << std::endl;
	std::cout << "y angle for point " << i << " is = " << y_angle << std::endl;
	std::cout << " " << std::endl;
	*/
}

void get_3d_coordinated(std::vector<cv::Point3f> &points_3d)
{
	points_3d.clear();
	for (int i = 0; i < 40; i++)
	{
		float x = depth[i] * cos(degToRad(azimuth[i])) * sin(degToRad(inclination[i]));
		float y = depth[i] * sin(degToRad(azimuth[i])) * sin(degToRad(inclination[i]));
		float z = depth[i] * cos(degToRad(inclination[i]));
		
		//std::cout << "x = " << x << " y = " << y << " z = " << z << "\n";

		points_3d.push_back(cv::Point3f(x, y, z));
	}
}

void get_3d_coord_world_frame(std::vector<cv::Point3f>& points_3d)
{
	points_3d.clear();
	for (int i = 0; i < 8; i++)
	{
		for (int j = 0; j < 5; j++)
		{
			points_3d.push_back(cv::Point3f(i*29, -j*29, 0));
		}
	}
}


int main()
{
	VisionManager VisManager = VisionManager();
	int count = 0;

	std::cout << "Iteration: " << ++count << "\n";
	cv::Mat left_img, right_img;
	std::vector<cv::Point2f> corners_left, corners_right;
	int map[40][2];
	bool found_pattern = VisManager.get_patten_info_from_device(CAMERA_IDX, left_img, corners_left, right_img, corners_right, map);

	printf("\nLocal found pattern in both: %s\n", found_pattern ? "true" : "false");

	cv::Mat dst;
	hconcat(left_img, right_img, dst);
	//cv::imwrite("local_left_img5.png", left_img);
	//cv::imwrite("local_right_img5.png", right_img);
	cv::namedWindow("infrared_stereo_pair", cv::WINDOW_NORMAL);
	imshow("infrared_stereo_pair", dst);
	if (found_pattern)
	{
		cv::drawChessboardCorners(left_img, cv::Size(5, 8), cv::Mat(corners_left), true);
		cv::drawChessboardCorners(right_img, cv::Size(5, 8), cv::Mat(corners_right), true);


		cv::Mat local_dst_corner;
		hconcat(left_img, right_img, local_dst_corner);
		cv::namedWindow("local_infrared_stereo_pair_w_corners", cv::WINDOW_NORMAL);
		imshow("local_infrared_stereo_pair_w_corners", local_dst_corner);

		std::vector<cv::Point3f> objectPoints;
		std::vector<cv::Point3f> objectPoints2;

		for (int i = 0; i < 40; i++)
		{
			float x_l = corners_left[map[i][0]].x;
			float x_r = corners_right[map[i][1]].x;

			//cout << "corner x positions = " << x_l << " and " << x_r << endl;
			depth_calc(x_l, x_r, i);
			angle_calc(corners_left[i].x, corners_left[i].y, corners_right[i].x, corners_right[i].y, i);
		}
		get_3d_coordinated(objectPoints);
		get_3d_coord_world_frame(objectPoints2);
		for (int i = 0; i < 40; i++)
		{
			std::cout << "x = " << objectPoints[i].x << " y = " << objectPoints[i].y << " z = " << objectPoints[i].z << "\n";
		}

		float cam_mat[3][3];
		if (CAMERA_IDX == LOCAL_CAM_INDEX)
		{
			std::cout << "\n Use local camera intrinsics \n";
			cam_mat[0][0] = 646.908;// fx
			cam_mat[0][1] = 0;
			cam_mat[0][2] = 641.877; // cx

			cam_mat[1][0] = 0;
			cam_mat[1][1] = 646.908; //fy
			cam_mat[1][2] = 405.522; //cy

			cam_mat[2][0] = 0;
			cam_mat[2][1] = 0;
			cam_mat[2][2] = 1;
		}
		else
		{
			std::cout << "\n Use global camera intrinsics \n";
			cam_mat[0][0] = 634.637;// fx
			cam_mat[0][1] = 0;
			cam_mat[0][2] = 636.179; // cx

			cam_mat[1][0] = 0;
			cam_mat[1][1] = 634.637; //fy
			cam_mat[1][2] = 393.432; //cy

			cam_mat[2][0] = 0;
			cam_mat[2][1] = 0;
			cam_mat[2][2] = 1;
		}
		

		cv::Mat camera_matrix(3, 3, CV_32F, &cam_mat);

		float coeff[5] = { 0, 0, 0, 0, 0 };
		cv::Mat distortion_coeff(1, 5, CV_32F, &coeff);

		cv::Mat rvec1, tvec1, outjac, rvec2, tvec2, rmat1, rmat2, jacobian1, jacobian2, conc1, conc2, tmat1, tmat2;
		std::vector<cv::Point2f> outimg;

		cv::solvePnP(objectPoints2, corners_left, camera_matrix, distortion_coeff, rvec1, tvec1);
		cv::solvePnP(objectPoints2, corners_right, camera_matrix, distortion_coeff, rvec2, tvec2);

		cv::projectPoints(objectPoints2, rvec1, tvec1, camera_matrix, distortion_coeff, outimg, outjac);

		cv::Rodrigues(rvec1, rmat1, jacobian1);
		cv::Rodrigues(rvec2, rmat2, jacobian2);

		double bott2[1][4] = { {0.0, 0.0, 0.0, 1.0} };
		cv::Mat bott(1, 4, rmat1.type(), &bott2);

		hconcat(rmat1, tvec1, conc1);
		hconcat(rmat2, tvec2, conc2);
		
		vconcat(conc1, bott, tmat1);
		vconcat(conc2, bott, tmat2);

		std::cout << "\nOrientation:\n";
		std::cout << "Pitch = " << radToDeg(rvec1.at<double>(0)) << " roll = " << radToDeg(rvec1.at<double>(1)) << " yaw = " << radToDeg(rvec1.at<double>(2)) << std::endl;
		/*
		std::cout << "\n" << "regular coordinates" << std::endl;
		std::cout << corners_left << std::endl;
		std::cout << "\n" << "Projected plane coordinates" << std::endl;
		std::cout << outimg << std::endl;
		std::cout << "rvec:\n";
		std::cout << rvec1;
		std::cout << "\ntvec:\n";
		std::cout << tvec1;
		std::cout << "\nconc1:\n";
		std::cout << conc1;
		std::cout << "\nbott:\n";
		std::cout << bott;
		std::cout << "\nrmat1:\n";
		std::cout << rmat1;
		std::cout << "\njacobian1:\n";
		std::cout << jacobian1;
		*/
		std::cout << "\ntmat1:\n";
		std::cout << tmat1;
		std::cout << "\ntmat2:\n";
		std::cout << tmat2;
		/*
		std::vector<cv::Mat> channels;
		channels.push_back(left_img);
		channels.push_back(left_img);
		channels.push_back(left_img);
		cv::Mat gray_3chan;
		cv::merge(channels, gray_3chan);
		cv::namedWindow("gray 3 chan", cv::WINDOW_NORMAL);
		imshow("gray 3 chan", gray_3chan);

		
		float squareSize = 50;
		cv::drawFrameAxes(gray_3chan, camera_matrix, distortion_coeff, rvec, tvec, 2 * squareSize);

		cv::namedWindow("coord_axes", cv::WINDOW_NORMAL);
		imshow("coord_axes", gray_3chan);
		*/

		/*
		std::vector<cv::Point2f> img_points;
		cv::projectPoints(objectPoints, rvec, tvec, camera_matrix, distortion_coeff, img_points);
		std::cout << "\n" << img_points << "\n";
		cv::Mat draw_axis = left_img.clone();

		cv::line(draw_axis, corners_left[12], img_points[0], cv::Scalar(255, 0, 0), 5);
		cv::line(draw_axis, corners_left[12], img_points[1], cv::Scalar(0, 255, 0), 5);
		cv::line(draw_axis, corners_left[12], img_points[2], cv::Scalar(0, 0, 255), 5);
		cv::namedWindow("coord_axes", cv::WINDOW_NORMAL);
		imshow("coord_axes", draw_axis);
		*/
	}


	cv::waitKey(0);

	return 1;
}