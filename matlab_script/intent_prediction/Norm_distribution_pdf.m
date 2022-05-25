%accuracy
%beta = (2*pi)/180

%distance between glasses and gaze point
c = 66

%length of b
%b = c*sin(beta)

%standard deviation
%sigma = b/3
sigma = 1.562940373


%mean value
mu = 0

%normal distribution
x = [-6:.01:6];
f = normpdf(x,mu,sigma);

accuracy=sigma*3

%accuracy in degrees
alpha = asin(accuracy/c);

accdeg = alpha*180/pi

%intent prediction
x_d = 21;
y_d = 5;
hyp = sqrt(x_d^(2)+y_d^(2))

%plot
plot(x,f)

