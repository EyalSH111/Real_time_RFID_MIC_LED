This project is a prototype of a security system built on a breadboard, combining an RFID reader, a microphone, and an 8x8 LED matrix, with real-time logic running in Python.

 How It Works:

The system continuously runs a Python script that waits for a specific RFID tag.

Once the correct RFID is scanned, a 30-second timer starts.

Within that time, the user must input a specific sound.

If the sound is recognized correctly:

✅ A green smiling face is displayed on the LED matrix.

If the sound is incorrect:

❌ A red face is shown.

 Tech Stack:

Hardware: Breadboard, RFID Module, Microphone, 8x8 LED Matrix, Arduino

Software:

Python for real-time control and logic

MATLAB for audio signal analysis and tone recognition

Arduino for hardware interfacing

 Highlights:

Custom logic for reliable sound recognition.

Improved Arduino-Python integration for smooth hardware-software communication.

Simple and effective demonstration of multi-factor authentication (RFID + audio).
