#pragma once

#ifndef VISION_MANAGER_H
#define VISION_MANAGER_H

#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <iostream>
#include <vector>

#include <opencv2/core.hpp>

#include <librealsense2/rs.hpp>

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                     These parameters are reconfigurable                                        //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define STREAM          RS2_STREAM_INFRARED  // rs2_stream is a types of data provided by RealSense device        //
#define FORMAT          RS2_FORMAT_Y8       // rs2_format identifies how binary data is encoded within a frame   //
#define WIDTH           1280                 // Defines the number of columns for each frame                      //
#define HEIGHT          800               // Defines the number of lines for each frame                           //
#define FPS             0                // Defines the rate of frames per second                                //
#define STREAM_INDEX_LEFT  1              // Defines the stream index, used for multiple streams of the same type //
#define STREAM_INDEX_RIGHT 2              // Defines the stream index, used for multiple streams of the same type //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#if 0
#define OFFLINE_MODE
#endif

class VisionManager
{
private:
	int nr_of_devices;
	std::vector<std::string> serials;
	cv::Size patternsize;

	/* Realsesnse Camera variables */
	rs2::context ctx;
	rs2::device_list dev_list;
	std::vector<rs2::pipeline> pipelines;

#ifdef OFFLINE_MODE
	std::vector<cv::Mat> left_images;
	std::vector<cv::Mat> right_images;
#endif

	void get_stereo_pair_from_device(int dev_idx, cv::Mat& left_img, cv::Mat& right_img);
	void init_devices();
	void configure_video_stream();
	void configure_IR_projector();

public:
	VisionManager();

	/* Return the serial ID of each device, the index of the serial is the index of the device. */
	void get_devices_serials(std::vector<std::string> serials);
	
	int get_nr_of_devices();

	/**
	 * Get the pattern onformation from the stereo camera. 
	 * 
	 * [out] img_left       The left image in grayscale. 
	 * [out] corners_left   All the points in the pattern for the left image
	 * [out] img_right      The right image in grayscale. 
	 * [out] corners_right  All the points in the pattern for the right image
	 * [out] map            The mapping between the two set of point vecotrs.
	 * return               True if a checkerboard pattern was found in both images.
	 */
	bool get_patten_info_from_device(int dev_idx, cv::Mat& img_left, std::vector<cv::Point2f>& corners_left, cv::Mat& img_right, std::vector<cv::Point2f>& corners_right, int map[16][2]);

	rs2_intrinsics get_intrinsics_from_device(int dev_idx);
};

#endif