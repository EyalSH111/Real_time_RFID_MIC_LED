import numpy as np
import scipy.io
import os
import random
import matplotlib.pyplot as plt
import serial
import time
import sys  # Import sys to use sys.exit()
from collections import deque
import threading
import tkinter as tk
from tkinter import ttk

# File paths
base_folder = r'C:\Users\Eyal\.spyder-py3\mic_project'
data2_path = os.path.join(base_folder, 'Data_1.mat')
data1_path = os.path.join(base_folder, 'Data_2.mat')

# RFID parameters
known_uid = "69 DC FC D5"  # Replace with the actual UID of your target card
duration = 30  # Duration of recording in seconds
sampling_rate = 10  # Samples per second
num_samples = sampling_rate * duration
data = deque(maxlen=num_samples)
time_vector = deque(maxlen=num_samples)

# Initialize serial port function
def initialize_serial():
    try:
        arduino = serial.Serial(port='COM7', baudrate=9600, timeout=1)
        time.sleep(2)  # Allow time for the Arduino to initialize
        return arduino
    except serial.SerialException as e:
        print(f"Failed to open serial port: {e}")
        sys.exit()

# Function to read RFID
def read_rfid(arduino):
    if arduino.in_waiting > 0:
        uid = arduino.readline().decode().strip()
        return uid
    return None

# Function to turn LED on/off
def turn_on_led(arduino):
    arduino.write(b'H')
    time.sleep(2)
    arduino.write(b'L')

# Function to read and store data
def read_data(arduino, stop_event, data, time_vector, start_time):
    print("Starting data reading...")
    while not stop_event.is_set():
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8', errors='ignore').strip()
            if line.isdigit():
                sensor_value = int(line)
                elapsed_time = time.time() - start_time
                data.append(sensor_value)
                time_vector.append(elapsed_time)
        time.sleep(0.1)
    print("Data reading stopped.")

# Timer and progress bar
def start_timer(root, progress, label, duration, stop_event):
    progress["maximum"] = duration
    elapsed_time = 0
    while elapsed_time <= duration:
        if stop_event.is_set():
            break
        time_remaining = duration - elapsed_time
        label.config(text=f"Time remaining: {time_remaining} seconds")
        progress["value"] = elapsed_time
        root.update_idletasks()
        time.sleep(1)
        elapsed_time += 1
    stop_event.set()

# Extract outliers
def extract_outliers(data):
    data = np.array(data)
    Q1, Q3 = np.percentile(data, [25, 75])
    IQR = Q3 - Q1
    lower_bound, upper_bound = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    outlier_indices = np.where((data < lower_bound) | (data > upper_bound))[0]
    outliers = data[outlier_indices]
    return outlier_indices, outliers

# Plot data with outliers
def plot_outliers(time_vector, data, outlier_indices, outliers):
    plt.figure(figsize=(12, 6))
    plt.plot(time_vector, data, label='Recorded Data', color='blue', marker='o', markersize=5)
    if len(outlier_indices) > 0:
        plt.plot(np.array(time_vector)[outlier_indices], outliers, 'ro', label='Outliers')
    plt.title('Data with Outliers Highlighted')
    plt.xlabel('Time (s)')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.show()

# Main function
def main(arduino):
    print("Waiting for RFID card...")
    # Wait until the correct RFID card is detected
    while True:
        uid = read_rfid(arduino)
        if uid:
            print(f"RFID Tag UID: {uid}")
            if uid == known_uid:
                print("Known RFID Tag detected!")
                turn_on_led(arduino)  # Turn on LED if the correct card is detected
                break
            else:
                print("Wrong card.")
                return  # Exit if the card is not recognized

    # Initialize Tkinter progress bar
    root = tk.Tk()
    root.title("Recording Progress")
    root.geometry("300x100")
    
    progress = ttk.Progressbar(root, orient="horizontal", length=280, mode="determinate")
    progress.pack(pady=20)
    label = tk.Label(root, text="Starting...")
    label.pack()

    stop_event = threading.Event()
    start_time = time.time()

    # Data collection and timer threads
    timer_thread = threading.Thread(target=start_timer, args=(root, progress, label, duration, stop_event))
    data_thread = threading.Thread(target=read_data, args=(arduino, stop_event, data, time_vector, start_time))
    timer_thread.start()
    data_thread.start()
    root.mainloop()
    stop_event.set()
    data_thread.join()

    # Save recorded data
    data_list, time_list = list(data), list(time_vector)
    scipy.io.savemat(data2_path, {"data1": data_list, "time_vector": time_list})
    print("Recording complete. Data saved as Data_2.mat")

    # Plot outliers
    outlier_indices, outliers = extract_outliers(data_list)
    plot_outliers(time_list, data_list, outlier_indices, outliers)

    # Load and compare with Data_1
    data1 = scipy.io.loadmat(data1_path)['data1'].flatten()
    time_vector_data1 = scipy.io.loadmat(data1_path)['time_vector'].flatten()

    # Comparison parameters
    window_size = int(5 * sampling_rate)
    tolerance = 3
    match_found = False

    # Perform match analysis with random windows
    for i in range(5):
        start_index = random.randint(0, len(data_list) - window_size)
        data2_window = data_list[start_index:start_index + window_size]
        data1_window = data1[start_index:start_index + window_size]
        time_window = time_list[start_index:start_index + window_size]

        # Find common points, excluding values 279-283
        common_points = (np.abs(np.array(data2_window) - np.array(data1_window)) <= tolerance) & \
                        ~((np.array(data2_window) >= 279) & (np.array(data2_window) <= 283)) & \
                        ~((np.array(data1_window) >= 279) & (np.array(data1_window) <= 283))
        
        if np.sum(common_points) >= 4:
            match_found = True
            print(f"Match found in 5-second window {i+1} with at least 4 common points.")
            turn_on_led(arduino)  # Turn on LED if match is found
            break

    # Final result
    if match_found:
        print("The recordings likely represent the same sound based on common points.")
    else:
        print("No matching windows with enough common points were found.")

if __name__ == "__main__":
    arduino = initialize_serial()  # Initialize serial port
    try:
        main(arduino)
    finally:
        if arduino and arduino.is_open:
            arduino.close()  # Ensure serial port is closed
