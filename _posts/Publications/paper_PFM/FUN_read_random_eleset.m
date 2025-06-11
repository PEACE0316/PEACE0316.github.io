function [remainingElements,selectedElements] = FUN_read_random_eleset(filename, setName, crack_ratio,shape)
    % Read abaqus inp file to get nodes, elements, element type, element areas,
    % and randomly select elements based on Weibull distribution
    %% Output arguments:
    % node : nodes of the model
    % element : elements of the model
    % eType : the element type
    % elementAreas : areas of the elements in the specified set
    % selectedElements: the randomly selected elements based on Weibull distribution
    %% Matlab 2016b or later (due to the use of 'split' function)
% filename = 'BM_m_5_2.inp';
% setName = 'ASS-1_vertical_M';
%输出的是random_set的单元以及剩余的单元

%  Read the entire file content as a string
s = fileread(filename);
s = lower(s);  % Convert file content to lowercase for easier handling
q = split(s, '*'); % Split content by '*'

% Read nodes
np = arrayfun(@(i)strncmp(q{i},'node',4), 1:numel(q), 'uniform', 1);
ns = q{find(np,1)}; % Get the node block
nsp = strfind(ns, newline);
ns = ns(nsp(1)+1:nsp(end)-1); % Extract node data
node = str2num(ns); % Convert string to numerical array

% Read elements
ep = arrayfun(@(i)strncmp(q{i},'element',7), 1:numel(q), 'uniform', 1);
es = q{find(ep,1)}; % Get the element block
esp = strfind(es, newline);
et = es(1:esp(1)-1); % Extract element type
n1 = strfind(et,'type=');
eType = et(n1(1)+5:end-1); % Extract element type
es = es(esp(1)+1:esp(end)-1); % Extract element data
es = strrep(es, char([44,13,10]), char(44)); % Remove newline and carriage return
element = str2num(es);  % Convert element data to numerical array

% Read element set (ELSET)
setPattern = strcat('elset, elset=', lower(setName));
setIdx = find(arrayfun(@(i)strncmp(q{i}, setPattern, length(setPattern)), 1:numel(q), 'uniform', 1), 1);
if isempty(setIdx)
    error('Element set not found.');
end
elsetBlock = q{setIdx};
elsetLines = strfind(elsetBlock, newline);
elset = elsetBlock(elsetLines(1)+1:elsetLines(end)-1); % Extract element set data
elset = str2num(elset); % Convert element set to numerical array，这里面包含的都是指定set对应的单元号

% Calculate element areas (assuming 4-node quadrilateral elements)
elementAreas = zeros(size(elset)); %按列存储
for i = 1:numel(elset)
    elNodes = element(element(:,1) == elset(i), 2:5); % Get the nodes of the element
    coords = node(elNodes, 2:3); % Get the coordinates of the nodes
    % Calculate the area of the quadrilateral element by dividing into two triangles
    A1 = polyarea(coords([1,2,3], 1), coords([1,2,3], 2)); % First triangle (nodes 1, 2, 3)
    A2 = polyarea(coords([1,3,4], 1), coords([1,3,4], 2)); % Second triangle (nodes 1, 3, 4)
    elementAreas(i) = A1 + A2; % Total area of the quadrilateral
end

% Calculate the total area
totalArea = sum(elementAreas(:));

%% Randomly select elements such that their combined area is 20% of the total area

% Define Weibull distribution parameters
% shape = 2; % Weibull shape parameter
scale = 1; % Weibull scale parameter

% Generate Weibull random weights for each element
weibullWeights = wblrnd(scale, shape, numel(elset), 1);

% Calculate how much area to select (20% of total area)
targetArea = crack_ratio * totalArea;

% Sort elements by their weighted random values (to prioritize selection)
[~, sortedIdx] = sort(weibullWeights, 'descend');

% Initialize variables for selecting elements
selectedElements = [];
currentArea = 0;

for i = 1:numel(sortedIdx)
    elID = elset(sortedIdx(i));  % Current element ID
    elArea = elementAreas(sortedIdx(i));  % Corresponding area

    if currentArea + elArea <= targetArea
        selectedElements = [selectedElements; elID];  % Add element to selection
        currentArea = currentArea + elArea;  % Accumulate area
    else
        break;  % Stop if adding the current element exceeds 20% area
    end
end

% Output: selectedElements contains the selected element IDs based on area
%disp(['Selected ', num2str(numel(selectedElements)), ' elements covering 20% of the total area.']);
remainingElements = setdiff(elset, selectedElements);
end
