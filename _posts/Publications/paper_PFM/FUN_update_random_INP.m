function [outputfile] = FUN_update_random_INP(filename, str_position, remain_position,crack_ratio,shape)
    %操作说明：1. inp文件统计设置不含part和assembly信息的，一般以** PART INSTANCE:分割
    %         2. 单元set编号包含连续和不连续的，通过generate来辨别
    %         3. 这里的surface在part上建立的
    %         4. 生成完成随机选取之后的inp
    %--------------inp文件读取(没有随机选取单元的inp)-------------------
%     filename = 'R10D0_Nx6_Ny6_preCrack.inp';  % INP 文件的名称
%     str_position = 'vertical';
%     remain_position = 'Horizontal';
%     crack_ratio = 0.99;
%     shape = 5;
    setName = ['ASS-1_' str_position]; % 你要处理的 elset 的名称
    [remainingElements, selectedElements] = FUN_read_random_eleset(filename, setName,crack_ratio,shape);

    inputPath = filename;

    if isempty(inputPath) == 1
        [FileName, PathName, FilterIndex] = uigetfile('*.inp');
        inputPath = [PathName FileName];
    end

    %% 新建一个指定inp文件对应的 _UE.inp 文件，用于后面改写
    % ---------------- Initializing output file -------------------
    inputName = inputPath;
    outputfile = [inputPath(1:end - 4) '_random_crackRatio' num2str(crack_ratio*100) '_shape' num2str(shape) '.inp'];
    fid = fopen(inputName, 'rt'); % %读入原inp文件
    fout1 = fopen(outputfile, 'wt'); % %写入新的_UEL.inp文件
    %% 开始按行读取文件
    a = fgets(fid); % % 读指定inp文件的第一行
    %原样输出*Elset,vertical之前的所有语句
    while (ischar(a))

        if contains(a, str_position)||contains(a, remain_position)
            break
        end

        fprintf(fout1, a);
        a = fgets(fid);
    end
    
    while (ischar(a))

        if contains(a, str_position)
            break
        end

        fprintf(fout1, a);
        a = fgets(fid);
    end

    fprintf(fout1, ('*Elset, elset=random_set\n'));
    %------------------------------------------------随机选取单元------------------
    % 计算 selectedElements 的行数并输出
    numSelected = numel(selectedElements);
    % 输出剩余的未选中的元素
    numRemaining = numel(remainingElements);

    numFullRowsSelected = floor(numSelected / 16);

    for i = 1:numFullRowsSelected
        fprintf(fout1, '%s\n', strjoin(arrayfun(@num2str, selectedElements((i - 1) * 16 + 1:i * 16), 'UniformOutput', false), ', '));
    end

    % 输出 selectedElements 中不足16个元素的行
    if mod(numSelected, 16) ~= 0
        remainingSelected = selectedElements(numFullRowsSelected * 16 + 1:end);
        fprintf(fout1, '%s\n', strjoin(arrayfun(@num2str, remainingSelected, 'UniformOutput', false), ', '));
    end

    numFullRowsRemaining = floor(numRemaining / 16);

    fprintf(fout1, ('*Elset, elset=remaining_set\n'));

    for i = 1:numFullRowsRemaining
        fprintf(fout1, '%s\n', strjoin(arrayfun(@num2str, remainingElements((i - 1) * 16 + 1:i * 16), 'UniformOutput', false), ', '));
    end

    % 输出 remainingElements 中不足16个元素的行
    if mod(numRemaining, 16) ~= 0
        remainingUnselected = remainingElements(numFullRowsRemaining * 16 + 1:end);
        fprintf(fout1, '%s\n', strjoin(arrayfun(@num2str, remainingUnselected, 'UniformOutput', false), ', '));
    end

    while (ischar(a))

        if contains(a, remain_position)||contains(a,'** Section:')
            break
        end

        a = fgets(fid);
    end

    while (ischar(a))

        if strfind(a, '** Section:') ~= 0
            fprintf(fout1, '** Section: P\n');
            fprintf(fout1, '*Solid Section, elset=ASS-1_P, material=P\n');
            fprintf(fout1, ',\n');
            fprintf(fout1, '** Section: M\n');
            fprintf(fout1, '*Solid Section, elset=ASS-1_%s_M, material=M\n', remain_position);
            fprintf(fout1, '*Solid Section, elset=remaining_set, material=M\n');
            fprintf(fout1, '*Solid Section, elset=random_set, material=random\n');
            break
        end

        fprintf(fout1, a);
        a = fgets(fid);
    end

    while (ischar(a))

        if strfind(a, '*System') ~= 0
            break
        end

        a = fgets(fid);
    end

    while (ischar(a))

        fprintf(fout1, a);
        a = fgets(fid);
    end

    fclose('all');
end
