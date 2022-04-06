import pyrealsense2 as rs
import numpy as np
import cv2
import mediapipe as mp

FX = 386.953
FY = 386.953
PPX = 319.307
PPY = 241.853

CamMatrix = np.asarray([[FX, 0.0, PPX, 0],
            		    [0.0, FY, PPY, 0],
             		    [0.0, 0.0, 1.0, 0]])


fPixels = CamMatrix[0,0]


TRASHOLD = 15


# Get real world coordinates, not sure if in meter since depthmap is given in mm
def get_coordinate(pixel_x, pixel_y, depth_map):
     
    matrix = CamMatrix
    u = int(pixel_x)
    v = int(pixel_y)
    depth = depth_map

    # Can substituate depth with depth_f and eliminate function distance_depth
    # depth_f = int(depth_image[pixel_x, pixel_y]) #this is in mm
    

    # X and Y might be in meters
    X = depth*(u-matrix[0][2])/(matrix[0][0])
    Y = depth*(v-matrix[1][2])/(matrix[1][1])
    # Z = depth_f
    return [X,Y]

# Create function that calculates Depth Distance aka Z from the middle of a ROI
def distance_depth(point_x, point_y):
    return int(depth_image[point_x, point_y])/10

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

# Start streaming
pipeline.start(config)

try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # Drawing hand landmarks
        mp_hand = mp.solutions.hands
        hands = mp_hand.Hands(max_num_hands=1)
        mp.draw = mp.solutions.drawing_utils
        results = hands.process(color_image)
    
        # Drawing the landmark and find the distance centimeter
        if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        #print(id,lm) id = type of landmark; lm coordinates of the landmark
                        h, w, c = color_image.shape
                        cx, cy = int(lm.x *w), int(lm.y*h)
                        if id == 9:
                            cv2.circle(color_image, (cx,cy), 10, (255,0,255), cv2.FILLED)
                            distance_lm = depth_image[cx,cy]
                            cv2.putText(color_image, "{}cm".format(int(distance_lm)), (cx, cy-10), 0, 1, (255,182,193), 2)
                          

        # Print real-world coordinates of a given point/s
        distance_roi = distance_depth(309, 408)
        rw_x, rw_y = get_coordinate(309, 408, distance_roi)
        print(rw_x, rw_y, distance_roi)

        # Drawing ROI for cup and find the distance in centimeter
        cv2.rectangle(color_image, (170,340), (448,477), (0,0,255), 4) 
        cv2.circle(color_image, (309, 408), 5, (255,0,.0), 2, cv2.FILLED)
        cv2.putText(color_image, (rw_x, rw_y, distance_roi), (309, 408-10), 0, 1, (255,182,193), 2)
        
        if distance_lm - distance_roi > TRASHOLD:
            print("is NOT going to pick up")
        else:
            print("IS GOING TO PICK UP")


        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))
                            
        
        # Show images
        cv2.namedWindow('Project', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Project', images)
        key = cv2.waitKey(30)
        
        # Esc button
        if key == 27:
            break
            

finally:

    # Stop streaming
    pipeline.stop()