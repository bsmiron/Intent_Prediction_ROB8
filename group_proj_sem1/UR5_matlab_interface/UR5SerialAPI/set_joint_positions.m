% Tell the UR5 to move to the desired joint positions
%
% The funtion requires a socket pointer and an array
% of 6 float numbers, each representing the the angle
% radians of each joint.
%
% Input:
% t - socket pointer (already opened) to the robot.
% P - an array of 6 float numbers.
function set_joint_positions(t, P)
    if nargin ~= 2
        error('error; not enough input arguments')

    end
    P_char = ['(',num2str(P(1)),',',...
        num2str(P(2)),',',...
        num2str(P(3)),',',...
        num2str(P(4)),',',...
        num2str(P(5)),',',...
        num2str(P(6)),...
        ')'];
    success = '0';
    while strcmp(success,'0')
        % task = 8 : ReadAndStoreJointPositionsFormSocket()
        % Value of 8 was hard-coded and chosen at random.
        fprintf(t,'(8)'); 
        pause(0.01);% Tune this to meet your system
        fprintf(t,P_char);
        while t.BytesAvailable==0
            %t.BytesAvailable
        end
        success  = readrobotMsg(t);
    end
    if ~strcmp(success,'1')
        error('error sending robot pose')
    end