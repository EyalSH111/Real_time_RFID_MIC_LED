close all;  % Close all open figures
clc;

% Change directory to where the data is located
cd('C:\Users\Eyal\.spyder-py3\mic_project');  % Adjust to your directory

% Load Data_3 and Data_5
load('Data_3.mat');  % Load Data_3.mat, assuming it contains 'data1'
rec2 = double(data1);  % Convert data1 to double and assign to rec2
load('Data_4.mat');  % Load Data_5.mat, assuming it also contains 'data1'
rec3 = double(data1);  % Convert data1 to double and assign to rec3

% Sampling rate (samples per second) - adjust if different
sampling_rate = length(time_vector) / (time_vector(end) - time_vector(1));

% Define window size for 5 seconds
window_size = round(5 * sampling_rate);

% Define tolerance for finding common points
tolerance = 3;

% Set up serial communication with Arduino
arduinoSerial = serialport("COM7", 9600);  % Replace 'COM7' with your Arduino's port
pause(2);  % Wait for 2 seconds to ensure the serial connection is ready

% First figure: Plot the original data
figure(1);
plot(time_vector, rec2, '-bo', 'MarkerFaceColor', 'b', 'DisplayName', 'Original Data 3');  % Plot rec2 with blue circles
hold on;
plot(time_vector, rec3, '-go', 'MarkerFaceColor', 'g', 'DisplayName', 'Original Data 5');  % Plot rec3 with green circles
xlabel('Time (s)');
ylabel('Amplitude');
title('Original Data Comparison');
legend('show');
grid on;

% Second figure: Plotting common points in random windows
figure(2);
plot(time_vector, rec2, '-bo', 'MarkerFaceColor', 'b', 'DisplayName', 'Original Data 3');  % Plot rec2 with blue circles
hold on;
plot(time_vector, rec3, '-go', 'MarkerFaceColor', 'g', 'DisplayName', 'Original Data 5');  % Plot rec3 with green circles
hold on;

% Initialize a flag to check if we have a matching window
match_found = false;

% Loop through 5 random 5-second windows
for i = 1:5
    % Select a random start point for a 5-second window
    start_index = randi([1, length(time_vector) - window_size + 1]);

    % Extract the 5-second window from rec2 and rec3
    rec2_window = rec2(start_index:start_index + window_size - 1);
    rec3_window = rec3(start_index:start_index + window_size - 1);
    time_window = time_vector(start_index:start_index + window_size - 1);

    % Identify common points within the 5-second window, excluding values between 279 and 285
    common_points_window = abs(rec2_window - rec3_window) <= tolerance & ...
                           ~(rec2_window >= 279 & rec2_window <= 283) & ...
                           ~(rec3_window >= 279 & rec3_window <= 283);

    % Total number of common points in the comparison, excluding data points with values between 279 and 282
    num_common_points = sum(common_points_window);

    % Plot common points in the 5-second window on the second figure
    plot(time_window(common_points_window), rec2_window(common_points_window), 'ks', 'MarkerFaceColor', 'k');  % Common points in black squares

    % Check if we have at least 3 common points
    if num_common_points >= 4
        match_found = true;
        fprintf('Match found in 5-second window %d with %d common points.\n', i, num_common_points);

        % Send signal to Arduino to turn on the LED
        write(arduinoSerial, '1', "char");  % Send '1' character to Arduino over serial
        pause(5);  % Keep MATLAB paused for 5 seconds to allow LED to stay on
        break;
    end

    % Display information about the selected window
    disp(['Random 5-second window ', num2str(i), ' starts at time: ', num2str(time_vector(start_index)), ' seconds']);
    disp(['Number of common points in window (excluding values between 279 and 282): ', num2str(num_common_points)]);
end

% Add a dotted horizontal line at zero on the second figure
yline(0, ':k', 'LineWidth', 1.5, 'DisplayName', 'Zero Line');  % Dotted black line at y=0

% Label the second plot
xlabel('Time (s)');
ylabel('Amplitude');
title('Data with Random 5-Second Windows Highlighted');
legend('show');  % Show legend for clarity
grid on;

% Display final result
if match_found
    disp('The recordings likely represent the same sound based on common points.');
else
    disp('No matching windows with enough common points were found. The recordings may not represent the same sound.');
end

% Clean up: Close the serial connection
clear arduinoSerial;
