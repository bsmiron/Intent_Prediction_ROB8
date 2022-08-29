import math
from colorobjectdetection import ObjectColorDetector

# test
# 
# #red_x = 20
# 
# #red_y = 30
# 
# #red_z = 23
# 
# #orange_x, orange_y, orange_z = 20, 30, 40
# 
# #green_x, green_y, green_z = 50, 40, 70
# 
# #blue_x, blue_y, blue_z = 23, 234, 25
# 
# #purple_x, purple_y, purple_z = 23, 63, 643
# black_x, black_y, black_z= 0, 0, 0 

#                           coordinates                     
# color_pos_dict = {'Red': [red_x, red_y, red_z],
#                   'Orange': [orange_x, orange_y, orange_z],
#                   'Yellow': [orange_x ,orange_y, orange_z],
#                   'Green': [green_x, green_y, green_z],
#                   'Blue': [blue_x, blue_y, blue_z],
#                   'Purple': [purple_x, purple_y, purple_z],
#                   'Black': [black_x, black_y, black_z]}

# test
# hand_kf_pos = [65, 24, 90]


def prediction_hand(color_pos_dict, hand_kf_pos):
    distance = []
    compare = 9999999
    out_color = ' '
    for color, coord_color in color_pos_dict.items():
        distance = math.sqrt((hand_kf_pos[0]-coord_color[0])**2 + (hand_kf_pos[1]-coord_color[1])**2 + (hand_kf_pos[2]-coord_color[2])**2)
        
        if distance < compare:
            compare = distance
            out_color = color
        
    return out_color

# print(prediction_hand(color_pos_dict, hand_kf_pos))


