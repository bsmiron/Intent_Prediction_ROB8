classdef CameraIntrinsics
    properties
        % Horizontal coordinate of the principal point of the image, as a pixel offset from the left edge
        ppx {mustBeNumeric}
        % Vertical coordinate of the principal point of the image, as a pixel offset from the top edge
        ppy {mustBeNumeric}
        % Focal length of the image plane, as a multiple of pixel width
        focal_length_x {mustBeNumeric}
        % Focal length of the image plane, as a multiple of pixel height
        focal_length_y {mustBeNumeric}
        % Width of the image in pixels
        image_width {mustBeNumeric}
        % Height of the image in pixels
        image_height {mustBeNumeric}
        % Distortion model of the image
        distortion_model
        % Distortion coefficients. Order for Brown-Conrady: [k1, k2, p1, p2, k3]. Order for F-Theta Fish-eye: [k1, k2, k3, k4, 0]. Other models are subject to their own interpretations
        coeffs
    end

    methods
        function obj = BasicClass(executable_location, camera_index)
            command = strcat(executable_location, " ", num2str(camera_index));
            [status, cmdout] = system(command);
            if status ~= 1
                error('Failed to execute app!')
            end
            command_split = split(cmdout);
            nr_of_lines = size(command_split, 1);
            obj.coeff = zeros(1,5);

            param_count = 0;
            expected_params = 12;
            for i = 1 : (nr_of_lines-1)
                if strcmp(command_split(i), '#3')
                    obj.ppx = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#4')
                    obj.ppy = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#5')
                    obj.focal_length_x = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#6')
                    obj.focal_length_y = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#7')
                    obj.image_width = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#8')
                    obj.image_height = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#9')
                    obj.distortion_model = command_split(i+1);
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#10')
                    obj.coeff(1) = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#11')
                    obj.coeff(2) = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#12')
                    obj.coeff(3) = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#13')
                    obj.coeff(4) = str2double(command_split(i+1));
                    param_count = param_count +1;
                elseif strcmp(command_split(i), '#14')
                    obj.coeff(5) = str2double(command_split(i+1));
                    param_count = param_count +1;
                end
            end

            if param_count ~= expected_params
                error('Not enough parameters have been found!')
            end
        end
    end
end