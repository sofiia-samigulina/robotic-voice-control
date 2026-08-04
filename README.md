# Implementation of Voice Control of the Rosmaster X3 Plus Smart Robot

This project implements a voice-controlled robotic system for the Rosmaster X3 Plus, enabling real-time navigation and object manipulation through speech commands. It integrates speech recognition (Vosk, Whisper), computer vision (YOLO), and ROS-based control into a single pipeline.

Based on the analysis, Vosk with grammar showed the best accuracy and response time.
[View Power BI analysis](https://github.com/sofiia-samigulina/robotic-voice-control/blob/main/analysis_power_bi/analysis_report.pdf)

## Technologies 
- Python
- ROS
- Linux
- Speech recognition models: Whisper and Vosk
- Computer vision and YOLO model for object detection
- multithreading
- Power BI for models analysis

## Key results
1. Improved Whisper recognition accuracy by 60% through prompt engineering
2. Achieved 90% accuracy using Vosk grammar mode
3. Evaluated trade-off between recognition quality and response speed across both models

## Hardware requirements

This project requires a Rosmaster X3 Plus robotic car. Without this car the project can't be fully tested.

## How it works

1. The microphone listens to the environment
2. Whisper or Vosk models recognize the human speech
3. A ROS node processes the commands and controls robot movement
4. A camera together with YOLO object detection is used when the robot needs to locate, follow and grip objects

## Code usage

This repository is for educational and portfolio purposes. For technical evaluation during job interviews, full access can be provided upon request.

## Author

Sofiia Samigulina
