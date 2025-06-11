%---------------注意，这里非连续编号，所以应该在第二层单元上加上最大的单元号，以避免重复2023-11-30----------
%--------------inp文件读取-------------------

function Fun_Random_processInputFile(inputPath,step_length)

    if isempty(inputPath)==1
        [FileName,PathName,FilterIndex] = uigetfile('*.inp');
        inputPath=[PathName FileName];
    end
    %% 新建一个指定inp文件对应的 _UEL.inp 文件，用于后面改写
    % ---------------- Initializing output file -------------------
    inputName=inputPath;
    
    step_length_str = strrep(sprintf('%.0e', step_length), 'e-0', 'E-');
    output=[inputPath(1:end-4) '_' step_length_str '_UE.inp'];

    fid=fopen(inputName,'rt'); %%读入原inp文件
    fout1 = fopen(output, 'wt'); %%写入新的_UEL.inp文件
    a=fgets(fid); %% 读指定inp文件的第一行
    % 开始对指定inp文件进行改写
    step_length = step_length * 10;
    % 将数字转换为字符串并拼接
    str_step_length = ['step_length=' num2str(step_length) '\n'];
    % ---------------- Sart reading input file -------------------
    cntE = 1;%每个part内的单元类型数
    ElMat = cell(0, 0);
    nMat1 = 0;
    %% 开始按行读取文件
    while(ischar(a))
        if strfind(a,'** PART INSTANCE:')~=0 %在** PART INSTANCE:之前添加下面几行
            fprintf(fout1,['*Parameter\n']);
            fprintf(fout1,['Plc=0.02\n']);
            fprintf(fout1,['PGc=0.1\n']);
            fprintf(fout1,['Mlc=0.02\n']);
            fprintf(fout1,['MGc=0.01\n']);
            fprintf(fout1,['MDlc=0.02\n']);
            fprintf(fout1,['MDGc=0.01\n']);
            fprintf(fout1,[str_step_length]);
            break
        end
        fprintf(fout1,a);    
        a=fgets(fid);    
    end
    % 接着读之后的内容，遇到特定标志（*System）停止读取，跳出循环
    while(ischar(a))
        while(ischar(a)) %L119 在*Element之前循环，遇到标志时退出
            while(ischar(a))
                if strfind(a,'*Element,')~=0 %遇到*Element停止循环
                    break
                end
                fprintf(fout1,a);
                a=fgets(fid);
            end
            a=fgets(fid); %对*Element之后的部分进行操作  
            fprintf(fout1,['*Element, type=CPE4,elset=Visualization\n']);%设置单元类型
            NnodeE(cntE)=4;
            % 初始化计数器和单元类型内部单元矩阵
            cnt = 0;
            ElMat{cntE} = [];

            while ~contains(a, '*Nset,') && ~contains(a, '*Element,') % 遇到*Nset跳出循环，也就是说对*Element与*Nset之间的内容进行操作
                cnt = cnt + 1; % 每个单元类型内部的单元数
                fprintf(fout1, '%s', a); % 将element之后的Nset之前的内容打印出来

                % 使用textscan读取当前行的数值
                rowData = textscan(a, '%d', 'Delimiter', ',');
                ElMat{cntE}(cnt, :) = rowData{1};

                % 读取下一行
                a = fgets(fid);
            end
            nElem(cntE) = length(ElMat{cntE}(:, 1)); % 每个part内部element的个数，也是行数
            fprintf(fout1,['***************************************************************\n']);

            if ~contains(a,'*Element,')==0    %判断单个part内部是否有多种element，并且作为跳出循环的标志
                cntE=cntE+1;
            else
                break
            end  
        end

        nElemAll=sum(nElem);
        %---------------*Nset之后*Solid Section之前的内容--------------
        fprintf(fout1,['***************************************************************\n']);

        cmat = 1;
        while ~contains(a, '** Section') % 处理*Nset之后，** Section之前的部分
            while isempty(strfind(a, '*Elset,'))
                a = fgets(fid);
            end
            a = fgets(fid);

            % 预分配内存
            b{cmat} = cell(1, 5); % 假设每个 section 最多有 1000 行
            cline = 1;

            while isempty(strfind(a, '** Section:')) && isempty(strfind(a, '*Elset,'))
                b{cmat}{cline} = str2num(a);

                if contains(a, '*Nset,') || contains(a, '** Section') % 遇到*Nset或** Section停止循环
                    break
                end

                cline = cline + 1;
                a = fgets(fid);
            end

            if contains(a, '** Section') % 遇到*Nset或** Section停止循环
                break
            end

            cmat = cmat + 1;
        end

       if contains(a,'** Section') %遇到*Solid Section跳出循环
            break
       end
    end   
    AllnElem = sum(nElemAll);
    ElMat = {}; % 创建一个空的 0x0 cell 数组
    % 将文件指针设置回文件开头
    fid=fopen(inputName,'rt'); %%读入原inp文件
    fseek(fid, 0, 'bof');  % 'bof' 表示文件的开头
    % 接着读之后的内容，遇到特定标志（*System）停止读取，跳出循环
    while(ischar(a))%对指定部分进行操作，
        while(ischar(a))%对指定部分进行操作，以element终止
            while(ischar(a))% Element之前的部分都跳过
                if strfind(a,'*Element,')~=0 %遇到*Element停止循环
                    break
                end
                a=fgets(fid);
            end
            a=fgets(fid); %对*Element之后的部分进行操作
            cnt = 0; % 给element后的单元计数

            % 遇到*Nset跳出循环，也就是说对*Element与*Nset之间的内容进行操作
            while ~contains(a, '*Nset,') && ~contains(a, '*Element,')
                cnt = cnt + 1; % 每个单元类型内部的单元数

                % 一次性读取所有数据
                data = textscan(a, '%d', 'Delimiter', ',');
                ElMat{cntE}(cnt, :) = data{1}';

                a = fgets(fid);
            end

            % 批量写入到文件
            fprintf(fout1, '****************************** U1 *******************************\n');
            fprintf(fout1, '*User element, nodes=4, type=U1, properties=4, coordinates=2, VARIABLES=8\n');
            fprintf(fout1, '4\n');
            fprintf(fout1, '*Element, type=U1,, ELSET=SOLID1\n');

            % 避免有不连续的编号
            MX_ele_no = max(ElMat{1, 1}(:, 1)); % 第一层中最大的单元号
            c1 = cell2mat(b{1});
            matching_indices = ismember(ElMat{1, 1}(:, 1), c1);
            % 查找包含目标值的行的索引
            for i = 1:numel(c1)
                target_value = c1(i);
                % 获取匹配的索引
                matching_indices = find(ElMat{1, 1}(:, 1) == target_value);

                % 对每个包含目标值的行进行操作
                for j = 1:numel(matching_indices)
                    index = matching_indices(j);
                    % 获取当前行的数据
                    row = ElMat{1}(index, :);
                    % 对每行的第一个数加上 AllnElem
                    row(1) = row(1) + MX_ele_no;
                    fprintf(fout1, '%d, %d, %d, %d, %d\n', row);
                end
            end
            fprintf(fout1,['*UEL PROPERTY, ELSET=SOLID1\n']);
            fprintf(fout1,['<Plc>,<PGc>,0,0\n']);
            fprintf(fout1,['****************************** U2 *******************************\n']);
            fprintf(fout1,['*User element, nodes=4, type=U2, properties=4, coordinates=2, VARIABLES=12\n']);
            fprintf(fout1,['4\n']);
            fprintf(fout1,['*Element, type=U2,ELSET=SOLID2\n']); 

            c2 = cell2mat(b{2});
            matching_indices = ismember(ElMat{1, 1}(:, 1), c2);
            % 查找包含目标值的行的索引
            for i = 1:numel(c2)
                target_value = c2(i);
                % 获取匹配的索引
                matching_indices = find(ElMat{1, 1}(:, 1) == target_value);

                % 对每个包含目标值的行进行操作
                for j = 1:numel(matching_indices)
                    index = matching_indices(j);
                    % 获取当前行的数据
                    row = ElMat{1}(index, :);
                    % 对每行的第一个数加上 AllnElem
                    row(1) = row(1) + MX_ele_no;
                    fprintf(fout1, '%d, %d, %d, %d, %d\n', row);
                end
            end

            fprintf(fout1,['*UEL PROPERTY, ELSET=SOLID2\n']);
            fprintf(fout1,['<MDlc>,<MDGc>,0,0\n']);
            
            fprintf(fout1,['****************************** U3 *******************************\n']);
            fprintf(fout1,['*User element, nodes=4, type=U3, properties=4, coordinates=2, VARIABLES=12\n']);
            fprintf(fout1,['4\n']);
            fprintf(fout1,['*Element, type=U3,ELSET=SOLID3\n']); 

            c3 = cell2mat(b{3});
            matching_indices = ismember(ElMat{1, 1}(:, 1), c3);
            % 查找包含目标值的行的索引
            for i = 1:numel(c3)
                target_value = c3(i);
                % 获取匹配的索引
                matching_indices = find(ElMat{1, 1}(:, 1) == target_value);

                % 对每个包含目标值的行进行操作
                for j = 1:numel(matching_indices)
                    index = matching_indices(j);
                    % 获取当前行的数据
                    row = ElMat{1}(index, :);
                    % 对每行的第一个数加上 AllnElem
                    row(1) = row(1) + MX_ele_no;
                    fprintf(fout1, '%d, %d, %d, %d, %d\n', row);
                end
            end

            fprintf(fout1,['*UEL PROPERTY, ELSET=SOLID3\n']);
            fprintf(fout1,['<Mlc>,<MGc>,0,0\n']);            

            fprintf(fout1,['****************************** U4 *******************************\n']);
            fprintf(fout1,['*User element, nodes=4, type=U4, properties=4, coordinates=2, VARIABLES=12\n']);
            fprintf(fout1,['4\n']);
            fprintf(fout1,['*Element, type=U4,ELSET=SOLID4\n']); 

            c4 = cell2mat(b{4});
            matching_indices = ismember(ElMat{1, 1}(:, 1), c4);
            % 查找包含目标值的行的索引
            for i = 1:numel(c4)
                target_value = c4(i);
                % 获取匹配的索引
                matching_indices = find(ElMat{1, 1}(:, 1) == target_value);

                % 对每个包含目标值的行进行操作
                for j = 1:numel(matching_indices)
                    index = matching_indices(j);
                    % 获取当前行的数据
                    row = ElMat{1}(index, :);
                    % 对每行的第一个数加上 AllnElem
                    row(1) = row(1) + MX_ele_no;
                    fprintf(fout1, '%d, %d, %d, %d, %d\n', row);
                end
            end

            fprintf(fout1,['*UEL PROPERTY, ELSET=SOLID4\n']);
            fprintf(fout1,['<Mlc>,<MGc>,0,0\n']); 
            
            % 遍历每个元素
            for i = 1:cmat
                % 遍历每一行
                fprintf(fout1,['*Elset, elset=SOLID' num2str(i) '\n']);
                for j = 1:numel(b{i})
                    % 将每一行的数据以逗号隔开打印
                    cmatrix = numel(b{i}{j});
                    for k = 1:cmatrix
                        b{i}{j}(k) = b{i}{j}(k)+MX_ele_no;  
                    end
                    fprintf(fout1, '%g, ', b{i}{j}(1:end-1));
                    fprintf(fout1, '%g\n', b{i}{j}(end));
                end
                fprintf(fout1,['*************************************************************\n']);
            end
            fprintf(fout1,['**********************************************************************************\n']);

            if ~contains(a,'*Element,')==0    %判断单个part内部是否有多种element，并且作为跳出循环的标志
                cntE=cntE+1;
            else
                break
            end  
        end

        while(ischar(a))
            if contains(a,'*System') %遇到*Solid Section跳出循环
                break
            end
        fprintf(fout1,a);
        a=fgets(fid);
        end    
        if contains(a,'*System') %遇到*System跳出循环
            break
        end
    end
    while~contains(a,'** BOUNDARY CONDITIONS')
        if strfind(a,'*User Material')~=0
            fprintf(fout1,['1, S11, S11\n']);
            fprintf(fout1,['2, S22, S22\n']);
            fprintf(fout1,['3, S33, S33\n']);
            fprintf(fout1,['4, S12, S12\n']);
            fprintf(fout1,['5, PHI, PHI\n']);
            fprintf(fout1,['6, PSI, PSI\n']);
        end
        fprintf(fout1,a);    
        a=fgets(fid);
    end

    while(ischar(a))
        if strfind(a,'** STEP: Step-1')~=0
            fprintf(fout1,a);
            a=fgets(fid);
            fprintf(fout1,['*Step, name=Step-1, nlgeom=NO, inc=1000000\n']);
            fprintf(fout1,['*Static, direct\n']);
            fprintf(fout1,['<step_length>, 1., \n']);
            fprintf(fout1,['*Solution Technique, type=QUASI-NEWTON, reform kernel=25\n']);
            fprintf(fout1,['**\n']);
            fprintf(fout1,['** CONTROLS\n']);
            fprintf(fout1,['*Controls, reset\n']);
            fprintf(fout1,['*Controls, parameters=time incrementation\n']);
            fprintf(fout1,['25000, 25000, 25000, 25000, 25000, , , , , , \n']);
            break
        end
        fprintf(fout1,a);    
        a=fgets(fid);
    end
    while(ischar(a))
        if strfind(a,'** BOUNDARY CONDITIONS')~=0
            fprintf(fout1,a);
            a=fgets(fid);
            break
        end    
        a=fgets(fid);
    end

    while(ischar(a))
        if strfind(a,'** OUTPUT REQUESTS')~=0
            fprintf(fout1,a);
            a=fgets(fid);
            fprintf(fout1,['*Restart, write, frequency=0\n']);
            fprintf(fout1,['** FIELD OUTPUT: F-Output-1\n']);
            fprintf(fout1,['*Output, field, frequency=1000\n']);
            fprintf(fout1,['*Element Output, directions=YES\n']);
            fprintf(fout1,['SDV\n']);
            fprintf(fout1,['**\n']);
            fprintf(fout1,['** HISTORY OUTPUT: H-Output-1\n']);
            fprintf(fout1,['**\n']);
            fprintf(fout1,['*Output, history\n']);
            fprintf(fout1,['*Node Output, nset=LOAD\n']);
            fprintf(fout1,['RF2, U2\n']);
            break
        end
        fprintf(fout1,a);    
        a=fgets(fid);
    end
    while(ischar(a))
        if strfind(a,'*End Step')~=0
            fprintf(fout1,a);
            a=fgets(fid);
            break
        end    
        a=fgets(fid);
    end
    while(ischar(a)) % 这里可以将所有的step都打印出来，并且当遍历完最后一句时，a = -1,自动结束while循环
        while(ischar(a))
            a=fgets(fid);
            fprintf(fout1,a);
            if strfind(a,'*End Step')~=0
                break
            end
        end    
        a=fgets(fid);
    end
    fclose('all');
end
