leftGlobalCam_pattern = [0.999391  0.00669528   0.0342565    -50.8759
-0.00608816    0.999823  -0.0177965    -34.3387
 -0.0343696   0.0175771    0.999255     657.118
          0           0           0           1];

rightGlobalCam_pattern = [   0.999232    0.006093    0.038716    -100.566
-0.00547736    0.999857  -0.0159877    -34.3606
 -0.0388079   0.0157634    0.999122     658.069
          0           0           0           1];

leftLocalCam_pattern = [ 0.899596  -0.322262   0.294745   -146.337
  0.433482   0.740971  -0.512889    30.5109
-0.0531134   0.589159   0.806269    573.393
         0          0          0          1];

rightLocalCam_pattern = [0.899506   -0.32073   0.296682   -195.414
  0.433374   0.741171  -0.512692    30.8829
-0.0554562   0.589744   0.805684    574.002
         0          0          0          1];

rot =     [0.9995,    0.0307,   -0.0026;
           -0.0308,    0.9995,   -0.0067; 
            0.0024,    0.0068,    1.0000];

eul = rad2deg(rotm2eul(rot));
    

%%displacement values in x y z. in relation to left imager and flat front
%%of camera. 202cm z, 5.8mm x -12 y
base_leftGlobalCam =    [1, 0, 0, 2.2;
                         0, 1, 0, -12.5;
                         0, 0, 1, 196.1;
                         0, 0, 0, 1];

leftLocalCam_endeff =   [1, 0, 0, 18;
                         0, 1, 0, 25;
                         0, 0, 1, -43.8;
                         0, 0, 0, 1];
 
base_rightGlobalCam =   [1, 0, 0, 52.2;
                         0, 1, 0, -12.5;
                         0, 0, 1, 196.1;
                         0, 0, 0, 1];
         
rightLocalCam_endeff =  [1, 0, 0, -32;
                         0, 1, 0, 25;
                         0, 0, 1, -43.8;
                         0, 0, 0, 1];


  
Base_endeff_left = base_leftGlobalCam * leftGlobalCam_pattern * ((leftLocalCam_pattern)^(-1)) * leftLocalCam_endeff
Base_endeff_right = base_rightGlobalCam * rightGlobalCam_pattern * ((rightLocalCam_pattern)^(-1)) * rightLocalCam_endeff      

