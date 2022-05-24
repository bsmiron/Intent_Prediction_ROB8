% t is the Socket Connection handle
function P = read_actual_joint_positions(t)

    if t.BytesAvailable>0
        fscanf(t,'%c',t.BytesAvailable);
    end
    
    % task = 7 : read_actual joint positions.
    % Note: the value of 7 is hard-coded and was chosen at
    % random.
    fprintf(t,'(7)'); 
    
    while t.BytesAvailable==0
    end
    rec = fscanf(t,'%c',t.BytesAvailable);
    if ~strcmp(rec(1),'[') || ~strcmp(rec(end),']')
        error('robotpose read error')
    end
    rec(end) = ',';
    Curr_c = 1;
    for i = 1 : 6
        C = [];
        Done = 0;
        while(Done == 0)
            Curr_c = Curr_c + 1;
            if strcmp(rec(Curr_c) , ',')
                Done = 1;
            else
                C = [C,rec(Curr_c)];
            end
        end
        P(i) = str2double(C);   
    end
    for i = 1 : length(P)
        if isnan(P(i))
            error('robotpose read error (Nan)')
        end
    end
end