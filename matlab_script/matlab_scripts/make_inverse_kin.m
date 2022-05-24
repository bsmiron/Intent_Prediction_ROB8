
pos = [-216.7490  108.5270  387.5140];
pos = pos/1000
%         X         Y          Z
eul = [1.4330 -0.8778 -2.1431];
%eul = [1.41186 -0.963398 -2.07946];
qPrevious = [-3.1431   -1.0472   -2.0657   -3.6635   -1.7692   -3.7415];

% pos = [216.3 301.35 499.79]; %pose 5
% pos = pos /1000;
% eul = [0.397 -0.051  -1.463];
% qPrevious = [-3.1431   -1.0472   -2.0657   -3.6635   -1.7692   -3.7415]; %pose 4


inv_angles = ikSolverUR5All_new(pos, eul,qPrevious);
inv_angles = transpose(inv_angles)
