# Raspberry Pi Trailcam

## Setup instructions

1. Install dependencies

  - `sudo apt-get update && sudo apt-get upgrade -y`
  - `sudo apt-get install -y python-dev python-gpiozero gpac`

2. Install Picamera

  - `wget https://bootstrap.pypa.io/get-pip.py && sudo python get-pip.py`
  - `sudo pip install picamera`

3. Clone the repository

  - `git clone https://github.com/tbeatty/rpi-trailcam`

4. Start the program

  - `python trailcam.py`

## Usage

```
usage: trailcam.py [-h] [--output-dir OUTPUT_DIR] [--log-dir LOG_DIR]
                   [--sharpness SHARPNESS] [--contrast CONTRAST]
                   [--brightness BRIGHTNESS] [--saturation SATURATION]
                   [--iso ISO] [--stabilize] [--hflip] [--vflip]
                   [--record-secs RECORD_SECS] [--annotate-text ANNOTATE_TEXT]

optional arguments:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
  --log-dir LOG_DIR, -l LOG_DIR
  --sharpness SHARPNESS
  --contrast CONTRAST
  --brightness BRIGHTNESS
  --saturation SATURATION
  --iso ISO
  --stabilize
  --hflip
  --vflip
  --record-secs RECORD_SECS
  --annotate-text ANNOTATE_TEXT
```

## Program output

```
2017-03-04 19:09:50,115 [INFO] Trailcam: Initializing
2017-03-04 19:09:50,573 [INFO] Trailcam: Starting trailcam
2017-03-04 19:09:58,510 [INFO] Trailcam: Recording video
AVC-H264 import - frame size 1024 x 768 at 25.000 FPS
AVC Import results: 900 samples - Slices: 15 I 885 P 0 B - 0 SEI - 15 IDR
2017-03-04 19:11:14,715 [INFO] Trailcam: Exiting
```
