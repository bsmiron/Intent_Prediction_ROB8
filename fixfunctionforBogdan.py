import pyrealsense2 as rs
import numpy as np
import cv2 as cv
import mediapipe as mp
import math
import time


FX = 386.953 * 2
FY = 386.953 * 2
PPX = 319.307
PPY = 241.853
print(PPY, PPX)
CamMatrix = np.asarray([[FX, 0.0, PPX, 0],
                        [0.0, FY, PPY, 0],
                        [0.0, 0.0, 1.0, 0]])


def get_coordinate(POI, depth_image, matrix=CamMatrix):
    Z = depth_image[POI[1], POI[0]]
    u = POI[0] * Z
    v = POI[1] * Z
    X = -(u - matrix[0, 2] * Z) / (matrix[0, 0])
    Y = -(v - matrix[1, 2] * Z) / (matrix[1, 1])
    return [int(X), int(Y), int(Z)]


def changePOI(action, x, y, flags, *userdata):
    global POI
    if action == cv.EVENT_LBUTTONDOWN:
        POI = [x, y]
        # When left mouse button is released, mark bottom right corner
    elif action == cv.EVENT_LBUTTONUP:
        pass


# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)


config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)


align_to = rs.stream.color
align = rs.align(align_to)

# Start streaming
cfg = pipeline.start(config)
px = 320
py = 120
POI = [px, py]
POI_T = [POI[1], POI[0]]
output = "You done fucked up"
cv.namedWindow("rgb", 1)
cv.setMouseCallback("rgb", changePOI)
profile = cfg.get_stream(rs.stream.depth)
intr = profile.as_video_stream_profile().get_intrinsics()
print(intr.fx, intr.fy, )
while True:
    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    # Convert images to numpy arrays
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    # Apply color map to depth
    depth_color_image = cv.applyColorMap(cv.convertScaleAbs(depth_image, alpha=0.03), cv.COLORMAP_JET)
    # Do the function
    output = get_coordinate(POI, depth_image)
    # Draw circles and range and stuff
    cv.circle(color_image, POI, 5, [255, 255, 255])
    cv.putText(color_image, f"depth here: {depth_image[POI[1], POI[0]]}", POI, cv.FONT_HERSHEY_PLAIN, 1,
               (0, 255, 0), 2, cv.LINE_AA)
    cv.putText(color_image, f"output here: {output} at: {[POI[0] - 320, (POI[1] - 240)]}", [20, 450], cv.FONT_HERSHEY_PLAIN, 1,
               (0, 255, 0), 2, cv.LINE_AA)
    # Show images
    cv.imshow("rgb", color_image)
    cv.imshow("depth", depth_color_image)
    if cv.waitKey(25) & 0xFF == ord('q'):
        break


