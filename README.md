# robotic-voice-control
Implementation of Voice Control of the Rosmaster X3 Plus Smart Robot

This project demonstrates my programming skills in Python and robotics control using ROS. It was created as a portfolio project to show navigation logic, object handling and speech interaction. 

Based on the analysis, Vosk with grammar showed the best accuracy and response time.
[View Power BI analysis](https://github.com/sofiia-samigulina/robotic-voice-control/blob/main/analysis_power_bi/analysis_report.pdf)

# Technologies 
- Python
- ROS
- Linux
- Speech recognition models: Whisper and Vosk
- Computer vision and YOLO model for object detection
- multithreading
- Power BI for models analysis

# Hardware requirements

This project requires a Rosmaster X3 Plus robotic car. Without this car the project can't be fully tested.

# How it works

1. The microphone listens to the environment
2. Whisper or Vosk models recognize the human speech
3. A ROS node processes the commands and controls robot movement
4. A camera together with YOLO object detection is used when the robot needs to locate and grip objects

# Code usage

This repository is provided for educational and demonstration purposes. 

**You may:** 

- view the code
- study the implementation
- use it as inspiration

**You may not:**
- copy the code
- reuse parts of the code in other projects
- redistribute the code

Exceptions may be granted for technical evaluation during job interviews.

# Author

Sofiia Samigulina
