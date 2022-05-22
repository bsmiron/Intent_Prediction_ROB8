import time
import math

# Get an attention score_depth
def get_score_attention(x_hand, y_hand, z_hand, x_obj, y_obj, z_obj):
    score = math.sqrt((x_hand - x_obj)*(x_hand - x_obj) + (y_hand - y_obj)*(y_hand - y_obj)+ (z_hand - z_obj)*(z_hand - z_obj))
    return score

# test if picked 
# 0 = no
#         0   1       2        3    4     5
#        red,orange, yellow, green, blue ,purple
picked = [0,   0,      0,      0,    0,    0]

# test if gaze is fixed on this objects 
# 0 = no
#         0   1       2        3    4     5
#        red,orange, yellow, green, blue ,purple
gaze =   [0,   0,      0,      0,    0,    0]

what_color = input("On what color is the gazed fixed on? Choose between red, orange, yellow, green, blue, purple: ")

if what_color == 'red':
    gaze[0] = 1
elif what_color == 'orange':
    gaze[1] = 1
elif what_color == 'yellow':
    gaze[2] = 1
elif what_color == 'green':
    gaze[3] = 1
elif what_color == 'blue':
    gaze[4] = 1
elif what_color == 'purple':
    gaze[5] = 1
else:
    print('no fixed gaze')

hand_x,hand_y,hand_z, = []
x_blue, y_blue, z_blue = [] 
x_red, y_red, z_red = []
x_green, y_green, z_green = []
x_orange, y_orange, z_orange = []
x_yellow, y_yellow, z_yellow = []
x_purple, y_purple, z_purple = []


obj_blue_score = get_score_attention(hand_x,hand_y,hand_z, x_blue, y_blue, z_blue)
obj_red_score = get_score_attention(hand_x,hand_y,hand_z, x_red, y_red, z_red)
obj_green_score = get_score_attention(hand_x,hand_y,hand_z, x_green, y_green, z_green)
obj_orange_score = get_score_attention(hand_x, hand_y, hand_z, x_orange, y_orange, z_orange)
obj_yellow_score = get_score_attention(hand_x, hand_y, hand_z, x_yellow, y_yellow, z_yellow)
obj_purple_score = get_score_attention(hand_x, hand_y, hand_z, x_purple, y_purple, z_purple) 

if what_color == 'red':
    obj_red_score = obj_red_score + obj_red_score % 20
elif what_color == 'orange':
    obj_orange_score = obj_orange_score - obj_orange_score %20
elif what_color == 'yellow':
    obj_yellow_score = obj_yellow_score - obj_yellow_score % 20
elif what_color == 'green':
    obj_green_score = obj_green_score - obj_green_score %20
elif what_color == 'blue':
    obj_blue_score = obj_blue_score - obj_blue_score % 20
elif what_color == 'purple':
    obj_purple_score = obj_purple_score - obj_purple_score % 20
else:
    print('no fixed gaze')


 #BLUE             
if (obj_blue_score < obj_red_score) and (obj_blue_score < obj_green_score)and (obj_blue_score < obj_yellow_score) and (obj_blue_score < obj_orange_score) and (obj_blue_score < obj_purple_score) and picked[4] == 0:
    print("Obj blue")
    picked[4] = 1
    max = max(obj_green_score, obj_red_score, obj_yellow_score, obj_orange_score, obj_purple_score)
    if max == obj_green_score and picked[3] == 0:
            ur5_coordinates = x_green, y_green, z_green
            time.sleep(15) # wait 15 seconds
            picked[3] = 1
            ok = 0
    elif max == obj_red_score and picked[0] == 0:
                ur5_coordinates = x_red, y_red, z_red
                time.sleep(15)
                picked[0] = 1
                ok = 0
    elif max == obj_yellow_score and picked[2] == 0:
                ur5_coordinates = x_yellow, y_yellow, z_yellow
                time.sleep(15)
                picked[2] = 1
                ok = 0
    elif max == obj_orange_score and picked[1] == 0:
                ur5_coordinates = x_orange, y_orange, z_orange
                time.sleep(15)
                picked[1] = 1
                ok = 0
    elif max == obj_purple_score and picked[5] == 0:
                ur5_coordinates = x_purple, y_purple, z_purple
                time.sleep(15)
                picked[5] = 1
                ok = 0
            #RED
elif (obj_red_score < obj_blue_score) and (obj_red_score < obj_green_score) and (obj_red_score < obj_yellow_score) and (obj_red_score < obj_orange_score) and (obj_red_score < obj_purple_score) and picked[0] == 0:
    print("obj red")
    picked[0]= 1
    max = max(obj_green_score, obj_blue_score, obj_yellow_score, obj_orange_score, obj_purple_score)
    if max == obj_green_score:
        ur5_coordinates = x_green, y_green, z_green
        time.sleep(15) # wait 15 seconds
        picked[3] = 1
        ok = 0
    elif max == obj_blue_score:
        ur5_coordinates = x_blue, y_blue, z_blue
        time.sleep(15)
        picked[4] = 1
        ok = 0
    elif max == obj_yellow_score:
        ur5_coordinates = x_yellow, y_yellow, z_yellow
        time.sleep(15)
        picked[2] = 1
        ok = 0
    elif max == obj_orange_score:
        ur5_coordinates = x_orange, y_orange, z_orange
        time.sleep(15)
        ok = 0
    elif max == obj_purple_score:
        ur5_coordinates = x_purple, y_purple, z_purple
        time.sleep(15)
        picked[5] = 1
        ok = 0
#Orange
elif (obj_orange_score < obj_blue_score) and (obj_orange_score < obj_green_score) and (obj_orange_score < obj_yellow_score) and (obj_orange_score < obj_red_score) and (obj_orange_score < obj_purple_score):
    print("obj orange")
    max = max(obj_green_score, obj_blue_score, obj_yellow_score, obj_red_score, obj_purple_score)
    if max == obj_green_score:
        ur5_coordinates = x_green, y_green, z_green
        time.sleep(15) # wait 15 seconds
        picked[3] = 1
        ok = 0
    elif max == obj_blue_score:
        ur5_coordinates = x_blue, y_blue, z_blue
        time.sleep(15)
        picked[4] = 1
        ok = 0
    elif max == obj_yellow_score:
        ur5_coordinates = x_yellow, y_yellow, z_yellow
        time.sleep(15)
        picked[2] = 1
        ok = 0
    elif max == obj_red_score:
        ur5_coordinates = x_red, y_red, z_red
        time.sleep(15)
        picked[0] = 1
        ok = 0
    elif max == obj_purple_score:
        ur5_coordinates = x_purple, y_purple, z_purple
        time.sleep(15)
        picked[5] = 1
        ok = 0
#Yellow
elif (obj_yellow_score < obj_blue_score) and (obj_yellow_score < obj_green_score) and (obj_yellow_score < obj_orange_score) and (obj_yellow_score < obj_red_score) and (obj_yellow_score < obj_purple_score):
    print("obj yellow")
    max = max(obj_green_score, obj_blue_score, obj_orange_score, obj_red_score, obj_purple_score)
    if max == obj_green_score:
        ur5_coordinates = x_green, y_green, z_green
        time.sleep(15) # wait 15 seconds
        picked[3] = 1
        ok = 0
    elif max == obj_blue_score:
        ur5_coordinates = x_blue, y_blue, z_blue
        time.sleep(15)
        picked[4] = 1
        ok = 0
    elif max == obj_orange_score:
        ur5_coordinates = x_orange, y_orange, z_orange
        time.sleep(15)
        picked[1] = 1
        ok = 0
    elif max == obj_red_score:
        ur5_coordinates = x_red, y_red, z_red
        time.sleep(15)
        picked[0] = 1
        ok = 0
    elif max == obj_purple_score:
        ur5_coordinates = x_purple, y_purple, z_purple
        time.sleep(15)
        picked[5] = 1
        ok = 0
#Purple
elif (obj_purple_score < obj_blue_score) and (obj_purple_score < obj_green_score) and (obj_purple_score < obj_orange_score) and (obj_purple_score < obj_red_score) and (obj_purple_score < obj_yellow_score):
    print("obj purple")
    max = max(obj_green_score, obj_blue_score, obj_orange_score, obj_red_score, obj_yellow_score)
    if max == obj_green_score:
        ur5_coordinates = x_green, y_green, z_green
        time.sleep(15) # wait 15 seconds
        picked[3] = 1
        ok = 0
    elif max == obj_blue_score:
        ur5_coordinates = x_blue, y_blue, z_blue
        time.sleep(15)
        picked[4] = 1
        ok = 0
    elif max == obj_orange_score:
        ur5_coordinates = x_orange, y_orange, z_orange
        time.sleep(15)
        picked[1] = 1
        ok = 0
    elif max == obj_red_score:
        ur5_coordinates = x_red, y_red, z_red
        time.sleep(15)
        picked[0] = 1
        ok = 0
    elif max == obj_yellow_score:
        ur5_coordinates = x_yellow, y_yellow, z_yellow
        time.sleep(15)
        picked[2] = 1
        ok = 0
#GREEN
elif (obj_green_score < obj_blue_score) and (obj_green_score < obj_green_score) and (obj_green_score < obj_orange_score) and (obj_green_score < obj_red_score) and (obj_green_score < obj_yellow_score) and picked[3]==0:
    print("obj green")
    max = max(obj_purple_score, obj_blue_score, obj_orange_score, obj_red_score, obj_yellow_score) 
    picked[3] = 1
    if max == obj_purple_score:
        ur5_coordinates = x_purple, y_purple, z_purple
        time.sleep(15)
        picked[5] = 0
        ok = 0
    elif max == obj_blue_score:
        ur5_coordinates = x_blue, y_blue, z_blue
        time.sleep(15)
        picked[4] = 0
        ok = 0
    elif max == obj_orange_score:
        ur5_coordinates = x_orange, y_orange, z_orange
        time.sleep(15)
        picked[1] = 0
        ok = 0
    elif max == obj_red_score:
        ur5_coordinates = x_red, y_red, z_red
        time.sleep(15)
        picked[0] = 0
        ok = 0
    elif max == obj_yellow_score:
        ur5_coordinates = x_yellow, y_yellow, z_yellow
        time.sleep(15)
        picked[2] = 0
        ok = 0

else: 
    print("Pyramid is done")
    ok = 0