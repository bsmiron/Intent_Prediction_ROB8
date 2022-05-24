#include "VisionManager.h"

#include<Eigen/Dense>

#include <opencv2/core/eigen.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include <librealsense2/rs.hpp>

#include <iostream>
#include <vector>

#define GLOBAL_CAM_INDEX (0)
#define LOCAL_CAM_INDEX (1)
#define NR_OF_ITERATIONS (10)

void make_camera_matrix(bool is_local_cam, float cam_mat[3][3])
{
	if (is_local_cam)
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
}

void get_3d_coord_world_frame(std::vector<cv::Point3f>& points_3d)
{
	points_3d.clear();
	for (int i = 0; i < 8; i++)
	{
		for (int j = 0; j < 5; j++)
		{
			points_3d.push_back(cv::Point3f(i * 29, -j * 29, 0));
		}
	}
}

int main()
{
	/*******************************************************************
	 * STEP 1: Initialize translation matrices for left/right cameras  *
	 *******************************************************************/

	Eigen::Matrix4d base_leftGlobalCam;
	base_leftGlobalCam <<
		1, 0, 0, 2.2,
		0, 1, 0, -12.5,
		0, 0, 1, 196.1,
		0, 0, 0, 1;

	Eigen::Matrix4d leftLocalCam_endeff;
	leftLocalCam_endeff <<
		1, 0, 0, 18,
		0, 1, 0, 25,
		0, 0, 1, -43.8,
		0, 0, 0, 1;

	Eigen::Matrix4d base_rightGlobalCam;
	base_rightGlobalCam <<
		1, 0, 0, 52.2,
		0, 1, 0, -12.5,
		0, 0, 1, 196.1,
		0, 0, 0, 1;

	Eigen::Matrix4d rightLocalCam_endeff;
	rightLocalCam_endeff <<
		1, 0, 0, -32,
		0, 1, 0, 25,
		0, 0, 1, -43.8,
		0, 0, 0, 1;

#if 1
	double rotate_to_ur_double[3][1] = { {-1.5708}, {-1.5708}, {0} }; // 90 0 90
	cv::Mat rotate_to_ur_mat(3, 1, CV_64F, &rotate_to_ur_double);
	cv::Mat rmat_to_ur;
	cv::Rodrigues(rotate_to_ur_mat, rmat_to_ur);
	std::cout << "\n rmat_to_ur: \n" << rmat_to_ur << "\n";

	double bottom[1][4] = { 0,0,0,1 };
	cv::Mat bott_zero(1, 4, CV_64F, &bottom);

	double left_pad[3][1] = { {0}, {0}, {0} };
	cv::Mat left_zero(3, 1, CV_64F, &left_pad);
	cv::Mat hconc_first, vconc_first;
	hconcat(rmat_to_ur, left_zero, hconc_first);
	vconcat(hconc_first, bott_zero, vconc_first);

	Eigen::Matrix4d rotation_matrix_1;
	cv::cv2eigen(vconc_first, rotation_matrix_1);
	std::cout << "\n rmat_to_ur_eig: \n" << rotation_matrix_1 << "\n";


	double rottation2_double[3][1] = { {0}, {0}, {0.7854} }; // 45 0 0
	cv::Mat rottation2vect_mat(3, 1, CV_64F, &rottation2_double);
	cv::Mat rottation2_mat;
	cv::Rodrigues(rottation2vect_mat, rottation2_mat);
	std::cout << "\n rottation2_mat: \n" << rottation2_mat << "\n";

	cv::Mat hconc_second, vconc_second;
	hconcat(rottation2_mat, left_zero, hconc_second);
	vconcat(hconc_second, bott_zero, vconc_second);

	Eigen::Matrix4d rotation_matrix_2;
	cv::cv2eigen(vconc_second, rotation_matrix_2);
	std::cout << "\n rmat_to_ur_eig: \n" << rotation_matrix_2 << "\n";
#endif
	/****************************************************************
     * STEP 2: Get information from Cameras                         *
     ****************************************************************/
	int camera_index;

	double position_from_left[NR_OF_ITERATIONS][3];
	double position_from_right[NR_OF_ITERATIONS][3];
	double rotation_left[NR_OF_ITERATIONS][3];
	double rotation_right[NR_OF_ITERATIONS][3];


	float cam_mat[3][3];
	float coeff[5] = { 0, 0, 0, 0, 0 };
	cv::Mat distortion_coeff(1, 5, CV_32F, &coeff);

	VisionManager VisManager = VisionManager();
	bool found_pattern;
	int map[40][2];
	cv::Mat left_img, right_img;
	std::vector<cv::Point2f> corners_left, corners_right;

	std::vector<cv::Point3f> objectPoints2;

	for (int i = 0; i < NR_OF_ITERATIONS; i++)
	{
		std::cout << "\n ITERATION: " << i + 1 << "\n";
		Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic> tmat_global_left;
		Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic> tmat_global_right;
		Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic> tmat_local_left;
		Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic> tmat_local_right;
		/****************************************************************
		 * STEP 2.1: Get information from Global Camera                 *
		 ****************************************************************/
		camera_index = GLOBAL_CAM_INDEX;		
		
		found_pattern = false;
		while (!found_pattern)
		{
			found_pattern = VisManager.get_patten_info_from_device(camera_index, left_img, corners_left, right_img, corners_right, map);

			if (!found_pattern)
			{
				std::cout << "Could not find pattern in global camera.\n";
			}
			else
			{
				make_camera_matrix((camera_index == LOCAL_CAM_INDEX), cam_mat);
				cv::Mat camera_matrix(3, 3, CV_32F, &cam_mat);

				get_3d_coord_world_frame(objectPoints2);

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

				cv::cv2eigen(tmat1, tmat_global_left);
				cv::cv2eigen(tmat2, tmat_global_right);
			}
		}
		
		/****************************************************************
		 * STEP 2.2: Get information from Local Camera                  *
		 ****************************************************************/
		camera_index = LOCAL_CAM_INDEX;

		found_pattern = false;
		while (!found_pattern)
		{
			found_pattern = VisManager.get_patten_info_from_device(camera_index, left_img, corners_left, right_img, corners_right, map);

			if (!found_pattern)
			{
				std::cout << "Could not find pattern in local camera.\n";
			}
			else
			{
				make_camera_matrix((camera_index == LOCAL_CAM_INDEX), cam_mat);
				cv::Mat camera_matrix(3, 3, CV_32F, &cam_mat);

				get_3d_coord_world_frame(objectPoints2);

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

				cv::cv2eigen(tmat1, tmat_local_left);
				cv::cv2eigen(tmat2, tmat_local_right);
			}
		}

		/****************************************************************
		 * STEP 3: Calculate Local camera position                      *
		 ****************************************************************/
		Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic> Base_endeff_left, Base_endeff_right;
		


		rotation_matrix_1 << 0.0007963, 0.0000000, -0.9999997, 0,
			0.9999993, 0.0007963, 0.0007963, 0,
			0.0007963, -0.9999997, 0.0000006, 0,
			0, 0, 0, 1;

		rotation_matrix_2 <<
			0.7292987, -0.6841955, 0.0000000, 0,
			0.6841955, 0.7292987, 0.0000000, 0,
			0.0000000, 0.0000000, 1.0000000, 0,
			0, 0, 0, 1;
		

		//std::cout << "Rotation matrix test" << rotation_matrix_1 << std::endl;
		//std::cout << "Rotation matrix test" << rotation_matrix_2 << std::endl;

		/* Matlab code 
		 * Base_endeff_left = base_leftGlobalCam * leftGlobalCam_pattern * ((leftLocalCam_pattern)^(-1)) * leftLocalCam_endeff */
		Base_endeff_left = rotation_matrix_1 * base_leftGlobalCam * tmat_global_left * (tmat_local_left.inverse()) * leftLocalCam_endeff * rotation_matrix_2;
		//Base_endeff_left = base_leftGlobalCam * tmat_global_left * (tmat_local_left.inverse()) * leftLocalCam_endeff;
		position_from_left[i][0] = Base_endeff_left(0, 3);
		position_from_left[i][1] = Base_endeff_left(1, 3);
		position_from_left[i][2] = Base_endeff_left(2, 3);

		/* Matlab code
		 * Base_endeff_left = base_leftGlobalCam * leftGlobalCam_pattern * ((leftLocalCam_pattern)^(-1)) * leftLocalCam_endeff */
		Base_endeff_right = rotation_matrix_1 * base_rightGlobalCam * tmat_global_right * ((tmat_local_right).inverse()) * rightLocalCam_endeff * rotation_matrix_2;
		//Base_endeff_right = base_rightGlobalCam * tmat_global_right * ((tmat_local_right).inverse()) * rightLocalCam_endeff;
		position_from_right[i][0] = Base_endeff_right(0, 3);
		position_from_right[i][1] = Base_endeff_right(1, 3);
		position_from_right[i][2] = Base_endeff_right(2, 3);

		Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic> rotation_mtx_left;
		rotation_mtx_left = Base_endeff_left.block(0, 0, 3, 3);

		//std::cout << "\n Base_endeff_left: \n" << Base_endeff_left << "\n";
		//std::cout << "\n rotation_mtx_left: \n" << rotation_mtx_left << "\n";
	    cv::Mat rot_mtx_mat_left, rot_v_left;

		cv::eigen2cv(rotation_mtx_left, rot_mtx_mat_left);
		//std::cout << "\n rot_mtx_mat: \n" << rot_mtx_mat_left << "\n";
		cv::Rodrigues(rot_mtx_mat_left, rot_v_left);
		//std::cout << "\n rot_v_left: \n" << rot_v_left << "\n";
		rotation_left[i][0] = rot_v_left.at<double>(0);
		rotation_left[i][1] = rot_v_left.at<double>(1);
		rotation_left[i][2] = rot_v_left.at<double>(2);
		//std::cout << "rotation_left: " << rotation_left[i][0] << " " << rotation_left[i][1] << " " << rotation_left[i][2] << "\n";
		
		Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic> rotation_mtx_right;
		rotation_mtx_right = Base_endeff_right.block(0, 0, 3, 3);

		//std::cout << "\n Base_endeff_right: \n" << Base_endeff_right << "\n";
		//std::cout << "\n rotation_mtx_right: \n" << rotation_mtx_right << "\n";
		cv::Mat rot_mtx_mat_right, rot_v_right;

		cv::eigen2cv(rotation_mtx_right, rot_mtx_mat_right);
		//std::cout << "\n rot_mtx_mat_right: \n" << rot_mtx_mat_right << "\n";
		cv::Rodrigues(rot_mtx_mat_right, rot_v_right);
		//std::cout << "\n rot_v_right: \n" << rot_v_right << "\n";
		rotation_right[i][0] = rot_v_right.at<double>(0);
		rotation_right[i][1] = rot_v_right.at<double>(1);
		rotation_right[i][2] = rot_v_right.at<double>(2);
	}
	/****************************************************************
     * STEP 4: Calculate average position                           *
     ****************************************************************/
	double average_left_X = 0, average_left_Y = 0, average_left_Z = 0;
	double average_right_X = 0, average_right_Y = 0, average_right_Z = 0;
	double avg_rotation_left[3] = {0 ,0, 0};
	double avg_rotation_right[3] = {0 ,0, 0};
	for (int i = 0; i < NR_OF_ITERATIONS; i++)
	{
		average_left_X += position_from_left[i][0];
		average_right_X += position_from_right[i][0];

		average_left_Y += position_from_left[i][1];
		average_right_Y += position_from_right[i][1];

		average_left_Z += position_from_left[i][2];
		average_right_Z += position_from_right[i][2];

		avg_rotation_left[0] += rotation_left[i][0];
		avg_rotation_left[1] += rotation_left[i][1];
		avg_rotation_left[2] += rotation_left[i][2];

		avg_rotation_right[0] += rotation_right[i][0];
		avg_rotation_right[1] += rotation_right[i][1];
		avg_rotation_right[2] += rotation_right[i][2];
	}
	/*
	for (int i = 0; i < NR_OF_ITERATIONS; i++)
	{
		std::cout << "pos left: " << position_from_left[i][0] << " " << position_from_left[i][1] << " " << position_from_left[i][2] << "\n";
	}
	for (int i = 0; i < NR_OF_ITERATIONS; i++)
	{
		std::cout << "pos right: " << position_from_right[i][0] << " " << position_from_right[i][1] << " " << position_from_right[i][2] << "\n";
	}
	*/
	average_left_X = average_left_X / NR_OF_ITERATIONS;
	average_left_Y = average_left_Y / NR_OF_ITERATIONS;
	average_left_Z = average_left_Z / NR_OF_ITERATIONS;

	average_right_X = average_right_X / NR_OF_ITERATIONS;
	average_right_Y = average_right_Y / NR_OF_ITERATIONS;
	average_right_Z = average_right_Z / NR_OF_ITERATIONS;

	std::cout << "Average left X, Y, Z: \n" << average_left_X << " " << average_left_Y << " " << average_left_Z << "\n";
	std::cout << "Average right X, Y, Z: \n" << average_right_X << " " << average_right_Y << " " << average_right_Z << "\n";
	
	avg_rotation_left[0] = avg_rotation_left[0] / NR_OF_ITERATIONS;
	avg_rotation_left[1] = avg_rotation_left[1] / NR_OF_ITERATIONS;
	avg_rotation_left[2] = avg_rotation_left[2] / NR_OF_ITERATIONS;
	std::cout << "Average rot left: \n" << avg_rotation_left[0] << " " << avg_rotation_left[1] << " " << avg_rotation_left[2] << "\n";
	
	avg_rotation_right[0] = avg_rotation_right[0] / NR_OF_ITERATIONS;
	avg_rotation_right[1] = avg_rotation_right[1] / NR_OF_ITERATIONS;
	avg_rotation_right[2] = avg_rotation_right[2] / NR_OF_ITERATIONS;
	std::cout << "Average rot right: \n" << avg_rotation_right[0] << " " << avg_rotation_right[1] << " " << avg_rotation_right[2] << "\n";

	double average_X, average_Y, average_Z;
	average_X = (average_left_X + average_right_X) / 2;
	average_Y = (average_left_Y + average_right_Y) / 2;
	average_Z = (average_left_Z + average_right_Z) / 2;

	double avg_rot[3];
	avg_rot[0] = (avg_rotation_left[0] + avg_rotation_right[0]) / 2;
	avg_rot[1] = (avg_rotation_left[1] + avg_rotation_right[1]) / 2;
	avg_rot[2] = (avg_rotation_left[2] + avg_rotation_right[2]) / 2;

	std::cout << "\nAverage X, Y, Z Rx Ry Rz: \n" << average_X << " " << average_Y << " " << average_Z << " " << avg_rot[0] << " " << avg_rot[1] << " " << avg_rot[2] << "\n";


	//std::cout << "Average rot: \n" << avg_rot[0] << " " << avg_rot[1] << " " << avg_rot[2] << "\n";
	return 1;
}