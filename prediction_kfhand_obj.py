import math
from colorobjectdetection import ObjectColorDetector


#                           coordinates                     
color_pos_dict = {'Red': [red_x, red_y, red_z],
                  'Orange': [orange_x, orange_y, orange_z],
                  'Yellow': [orange_x ,orange_y, orange_z],
                  'Green': [green_x, green_y, green_z],
                  'Blue': [blue_x, blue_y, blue_z],
                  'Purple': [purple_x, purple_y, purple_z],
                  'Black': [black_x, black_y, black_z]}


def prediction_hand(color_pos_dict, hand_kf_pos):
    distance = []
    compare = 9999999
    out_color = ' '
    for color, coord_color in color_pos_dict.items():
        distance[color] = math.sqrt((hand_kf_pos[0]-coord_color[0]*2 + hand_kf_pos[1]-coord_color[1]*2 + hand_kf_pos[2]-coord_color[2]*2))
        if distance[color] < compare:
            compare = distance[color]
            out_color = color
        
    
    return out_color



