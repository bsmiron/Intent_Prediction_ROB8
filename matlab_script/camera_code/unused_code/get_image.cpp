// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2017 Intel Corporation. All Rights Reserved.

/* Include the librealsense C header files */
#include <librealsense2/rs.h>
#include <librealsense2/h/rs_pipeline.h>
#include <librealsense2/h/rs_frame.h>
#include "../example.h"

#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

#include <opencv2/imgproc.hpp>
#include <opencv2/core.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/calib3d.hpp>

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                     These parameters are reconfigurable                                        //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define STREAM          RS2_STREAM_INFRARED  // rs2_stream is a types of data provided by RealSense device           //
#define FORMAT          RS2_FORMAT_Y16   // rs2_format identifies how binary data is encoded within a frame      //
#define WIDTH           1280               // Defines the number of columns for each frame                         //
#define HEIGHT          800               // Defines the number of lines for each frame                           //
#define FPS             15                // Defines the rate of frames per second                                //
#define STREAM_INDEX_LEFT  1              // Defines the stream index, used for multiple streams of the same type //
#define STREAM_INDEX_RIGHT 2              // Defines the stream index, used for multiple streams of the same type //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <librealsense2/rs.hpp>

using namespace cv;

static std::string get_sensor_name(const rs2::sensor& sensor)
{
    // Sensors support additional information, such as a human readable name
    if (sensor.supports(RS2_CAMERA_INFO_NAME))
        return sensor.get_info(RS2_CAMERA_INFO_NAME);
    else
        return "Unknown Sensor";
}

int main3()
{
    rs2::context ctx;
    rs2::device_list dev_list = ctx.query_devices();

    printf("There are %d devices \n", dev_list.size());
    
    // Capture serial numbers before opening streaming
    std::vector<std::string> serials;
    serials.clear();
    for (rs2::device dev : dev_list)
    {
        printf("Device serial nr is %s \n", dev.get_info(RS2_CAMERA_INFO_SERIAL_NUMBER));
        serials.push_back(dev.get_info(RS2_CAMERA_INFO_SERIAL_NUMBER));

        // Given a device, we can query its sensors using:
        std::vector<rs2::sensor> sensors = dev.query_sensors();

        printf("Device consists of %d ensors:\n", (int)sensors.size());

        /* Disable the IR sensor. We do not want the dotted pattern. */
        rs2::sensor stereo_sensor = sensors[0];
        stereo_sensor.set_option(RS2_OPTION_EMITTER_ENABLED, 0.f);
    }

    /* For now we will only use 1 camera so just use the first serial. */
    std::string cam1_serial = serials.back();

    rs2::pipeline pipe1(ctx);
    rs2::config cfg1;
    cfg1.enable_stream(STREAM, STREAM_INDEX_LEFT,  WIDTH, HEIGHT, FORMAT, FPS);
    cfg1.enable_stream(STREAM, STREAM_INDEX_RIGHT, WIDTH, HEIGHT, FORMAT, FPS);
    cfg1.enable_device(cam1_serial);
    
    pipe1.start(cfg1);

    while (1)
    {
        rs2::frameset frames = pipe1.wait_for_frames();
        printf("There are %d frames found\n", (int)frames.size());
        rs2::video_frame left_frame = frames.get_infrared_frame(STREAM_INDEX_LEFT);
        rs2::video_frame right_frame = frames.get_infrared_frame(STREAM_INDEX_RIGHT);

        Mat dMat_left = Mat(cv::Size(WIDTH, HEIGHT), CV_16UC1, (void*)left_frame.get_data());
        Mat dMat_right = Mat(cv::Size(WIDTH, HEIGHT), CV_16UC1, (void*)right_frame.get_data());
        
        Mat dst;
        hconcat(dMat_left, dMat_right, dst);
        namedWindow("infrared_stereo_pair", WINDOW_NORMAL);
        imshow("infrared_stereo_pair", dst);
        
        waitKey(0);
        imwrite("left_img_yaw9.197.png", dMat_left);
        imwrite("right_img_yaw9.197.png", dMat_right);
    }

    return EXIT_SUCCESS;
}