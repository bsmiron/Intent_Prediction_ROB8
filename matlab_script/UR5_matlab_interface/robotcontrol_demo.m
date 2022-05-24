% Code template for UR5 by Fereshteh Feb. 2015
% This demo reads current robot pose, then translates and rotates
% endeffector

% Note: 
% Copy the Polyscope folder to UR5 Controller using a USB drive
% Set UR5 IP
% Set PC IP in Polyscope program
% First run Matlab code; then run the Polyscope program
clear all
format compact
% Connect to robot
Robot_IP = '192.168.87.101';
Socket_conn = tcpip(Robot_IP, 30006,'NetworkRole','server');
fclose(Socket_conn);
disp('Press Play on Robot...')
fopen(Socket_conn);
disp('Connected!');

%% Read actual joint positions

Joint_Positions = read_actual_joint_positions(Socket_conn)

%% Poses list

poses = [-3.1431   -1.0472   -2.4657   -3.0634   -1.7690   -2.8415;
         -3.1431   -1.0472   -2.5657   -2.8635   -1.5690   -2.8415;
         -3.1431   -1.0472   -2.2657   -3.4635   -1.6691   -3.5415;
         -3.1431   -1.0472   -2.0657   -3.6635   -1.7692   -3.7415;
         -3.1431   -1.0472   -1.9657   -3.6635   -1.5692   -3.1415;
         -3.1431   -1.0472   -1.7656   -4.0635   -1.6693   -2.9415;
         -3.1431   -1.0472   -1.6655   -4.1635   -1.7693   -3.4416;
         -3.1431   -1.0472   -1.5655   -4.3635   -1.6693   -3.3416;
         -3.1431   -1.0472   -1.4655   -4.5634   -1.7693   -3.5417;
         -3.1431   -1.0472   -1.2655   -4.6635   -1.8693   -2.9417;];

%% Set joint positions
 %Joint_Positions(5) = Joint_Positions(5) - 0.10
 Joint_Positions(4) = Joint_Positions(4) - deg2rad(5);
 %Joint_Positions = [-3.1431   -1.0472   -2.4657   -3.0634   -1.7690   -2.8415];
 %Joint_Positions = poses(10, :);

 %Joint_Positions = [-3.1431   -1.0472   -1.9657   -3.6635   -1.5692   -3.1415];
 %Joint_Positions = poses(10, :);
 %Joint_Positions(2) = Joint_Positions(2) + deg2rad(15);
set_joint_positions(Socket_conn, Joint_Positions)

%% Read robot pose
Robot_Pose = readrobotpose(Socket_conn)
%Translation = Robot_Pose(1:3); % in mm
%Translation(3) = Translation(3) - 50
%Orientation = Robot_Pose(4:6);
Robot_Pose(2) = Robot_Pose(2) - 50
%GoalPose = [Translation Orientation]
moverobot(Socket_conn,Robot_Pose )