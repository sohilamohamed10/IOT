from pickletools import uint8
from turtle import right
import cv2
import numpy as np
import math
import serial
from flask import Flask, request, Response 
from datetime import datetime
import urllib.request
from time import sleep
from flask_socketio import SocketIO, send
import socket
from firebase import firebase
firebase = firebase.FirebaseApplication('https://rccar-2a976-default-rtdb.firebaseio.com', None)

# app = Flask(__name__)

url="http://172.28.131.120:8080/shot.jpg"
# while(True):
#     imgresp=urllib.request.urlopen(url)
#     imgnp=np.array(bytearray(imgresp.read()),dtype=np.uint8)
#     frame=cv2.imdecode(imgnp,-1)
#     print(frame)
#     cv2.imshow("test",frame)
#     cv2.waitKey(0)


# with serial.Serial('COM5', 9600) as ser:
# 	x = ser.readline()
# 	print(x)
	
# 	ser.write("This is my second arduino message\n")
	
# 	y = ser.readline()
# 	print(y)
	
	# ser.close()
# global curr_steering_angle
# curr_steering_angle=90

def detect_edges(frame):
    # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([60, 40, 40])
    upper_blue = np.array([150, 255, 255])
    # lowerColors = np.array([0, 0, 0])
    # upperColors = np.array([180, 255, 30])
    mask = cv2.inRange(hsv, lower_blue,upper_blue)
    # detect edges
    edges = cv2.Canny(mask, 200, 400)
    # cv2.imshow("canny",
    

    return edges
def regionOfInterest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus bottom half of the screen
    polygon = np.array([[
        (0, height * 1 / 2),
        (width, height * 1/ 2),
        (width, height),
        (0, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    croppedEdges = cv2.bitwise_and(edges, mask)
    return croppedEdges

def detect_line_segments(edges):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(edges, rho, angle, min_threshold, 
                                    np.array([]), minLineLength=8, maxLineGap=4)

    return line_segments
def average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        return lane_lines

    height, width, _ = frame.shape
    # left_fit_neg= []
    # left_fit_pos= []
    # right_fit_pos = []
    # right_fit_neg= []
    left_fit=[]
    right_fit=[]

    boundary = 1/2
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
                #     left_fit_neg.append((slope, intercept))
                # right_fit_neg.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))
                #     right_fit_pos.append((slope, intercept))
                # left_fit_pos.append((slope, intercept))

    # left_fit=np.concatenate((left_fit_neg,left_fit_pos),axis=0)
    # right_fit=np.concatenate((right_fit_neg,right_fit_pos),axis=0)

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines

def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down
    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def detect_lane(frame):
    
    edges = detect_edges(frame)
    cropped_edges=regionOfInterest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(frame, line_segments)
    lane_lines_image = display_lines(frame, lane_lines)
    # cv2.imshow("lane lines", lane_lines_image)

    return lane_lines

def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=10 ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right 
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))    
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image

def computeSteeringAngle(frame, laneLines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    if len(laneLines) == 0:
        print('No lane lines detected, do nothing')
        #MAKE CAR STOP?
        return -90

    # Get middle line in case of detecting single lane
    height, width, _ = frame.shape
    if len(laneLines) == 1:
        print('Only detected one lane line, just follow it. ', laneLines[0])
        x1, _, x2, _ = laneLines[0][0]
        x_offset = x2 - x1
    else:   # get middle line in case of detecting two lanes
        _, _, left_x2, _ = laneLines[0][0]
        _, _, right_x2, _ = laneLines[1][0]
        cameraMidOffsetPercent = 0.00 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + cameraMidOffsetPercent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angleToMidRadian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angleToMidDeg = int(angleToMidRadian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steeringAngle = angleToMidDeg + 90  # this is the steering angle needed by picar front wheel

    print('new steering angle: ', steeringAngle)
    return steeringAngle

# def stabilizeSteeringAngle(currSteeringAngle, newSteeringAngle, numOfLaneLines, maxAngleDeviationTwoLines=5, maxAngleDeviationOneLane=1):
#     """0
#     Using last steering angle to stabilize the steering angle
#     This can be improved to use last N angles, etc
#     if new angle is too different from current angle, only turn by maxAngleDeviation degrees
#     """
#     if numOfLaneLines == 2 :
#         # if both lane lines detected, then we can deviate more
#         maxAngleDeviation = maxAngleDeviationTwoLines
#     else :
#         # if only one lane detected, don't deviate too much
#         maxAngleDeviation = maxAngleDeviationOneLane
    
#     angleDeviation = newSteeringAngle - currSteeringAngle
#     if abs(angleDeviation) > maxAngleDeviation:
#         stabilizedSteeringAngle = int(currSteeringAngle + maxAngleDeviation * angleDeviation / abs(angleDeviation))
#     else:
#         stabilizedSteeringAngle = newSteeringAngle
#     print('Proposed angle: ',newSteeringAngle, ', stabilized angle: ' ,stabilizedSteeringAngle)
#     return stabilizedSteeringAngle


def move(frame):
    lane_lines=detect_lane(frame)
    new_steering_angle=computeSteeringAngle(frame,lane_lines)
    # steering_angle=stabilizeSteeringAngle(curr_steering_angle, newSteeringAngle=new_steering_angle, numOfLaneLines=len(lane_lines))
    # curr_steering_angle=new_steering_angle

    if(0 < new_steering_angle < 88):
       motion=0
    # elif (new_steering_angle >120):
    #     motion="right"
    # elif (50 <= new_steering_angle < 88):
    #     motion="leftHigh"
    elif (100< new_steering_angle):
        motion=1
    elif(new_steering_angle == -90):
        motion=3
    else :
        motion=2
    print(motion)
    return motion

# while (True):
#     imgresp=urllib.request.urlopen(url)
#     imgnp=np.array(bytearray(imgresp.read()),dtype=np.uint8)
#     frame=cv2.imdecode(imgnp,-1)
while (True):
    for i in range(1,2): 
        frame=cv2.imread("track{}.jpeg".format(i))
        dir=move(frame)
        firebase.put('','dir_auto',dir)
            # firebase.post('rccar-2a976-default-rtdb',dir)
        sleep(3)
# for i in range(1,14):
#     frame=cv2.imread("b{}.jpeg".format(i))
#     dir=move(frame)
 
# frame=cv2.imread("track4.jpeg")
# lane_lines=detect_la///////////////ne(frame)
# lane_lines_image = display_lines(frame, lane_lines)
# angle=computeSteeringAngle(frame,lane_lines)
# heading_image=display_heading_line(frame,angle)
# cv2.imshow("heading",heading_image)
# cv2.imshow("lane lines", lane_lines_image)
# cv2.waitKey(0)

# @app.route('/', methods=['GET'])
# def direction():
#     def motion():
#         while(True):
#             imgresp=urllib.request.urlopen(url)
#             imgnp=np.array(bytearray(imgresp.read()),dtype=np.uint8)
#             frame=cv2.imdecode(imgnp,-1)
#             dir=move(frame)
#             yield (dir+'\n')
#             sleep(10)
#     return Response(motion())

# @app.route("/")
# def motion():
#     def streamer():
#         while True:
#             imgresp=urllib.request.urlopen(url)
#             imgnp=np.array(bytearray(imgresp.read()),dtype=np.uint8)
#             frame=cv2.imdecode(imgnp,-1)
#             dir=move(frame)
#             sleep(15)
#             yield dir + "  "

#     return Response(streamer())

# if __name__ == '__main__':
#     app.run()


# while(True):
#     sleep(5)
#     clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     clientSocket.connect(("127.0.0.1",5000))
#     imgresp=urllib.request.urlopen(url)
#     imgnp=np.array(bytearray(imgresp.read()),dtype=np.uint8)
#     frame=cv2.imdecode(imgnp,-1)
#     # Connect to the server
#     # Send data to server
#     dir=move(frame)
#     data = dir

#     clientSocket.send(data.encode())
#     # Receive data from server

#     dataFromServer = clientSocket.recv(1024)
#     # Print to the console

#     print(dataFromServer.decode())