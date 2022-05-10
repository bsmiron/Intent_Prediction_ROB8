app_location = 'S:\AAU\Year1\StereoCamVS\x64\Debug\matlab_get_intrinsics_cpp.exe';

cam_idx = 0;

command = strcat(app_location, " ", num2str(cam_idx))

[status,cmdout] = system('S:\AAU\Year1\StereoCamVS\x64\Debug\matlab_get_intrinsics_cpp.exe');

cmdout

