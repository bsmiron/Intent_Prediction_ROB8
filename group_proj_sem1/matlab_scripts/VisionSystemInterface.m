classdef VisionSystemInterface
    properties
        Command
    end

    methods
        function obj = VisionSystemInterface(exe_location)
            Command = exe_location;
        end
        
        function [x, y, z] = get_end_effector_location()
            [status, cmdout] = system(Command);
            
            if status == 0
                command_split = split(cmdout);
                nr_of_lines = size(command_split, 1);
    
                param_count = 0;
                expected_params = 3;
                for i = 1 : (nr_of_lines-1)
                    if strcmp(command_split(i), '#1')
                        x = str2double(command_split(i+1));
                        param_count = param_count +1;
                    elseif strcmp(command_split(i), '#2')
                        y = str2double(command_split(i+1));
                        param_count = param_count +1;
                    elseif strcmp(command_split(i), '#3')
                        z = str2double(command_split(i+1));
                        param_count = param_count +1;
                    end
                end
    
                if param_count ~= expected_params
                    error('Not enough parameters have been found!')
                end
            else
                error('Failed to execute app!')
            end 
        end
    end
end