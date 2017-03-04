import logging
import os
import signal
import sys

from datetime import datetime
from gpiozero import MotionSensor
from picamera import Color, PiCamera
from subprocess import call
from time import sleep


MOTION_SENSOR_PIN = 17

LOG = logging.getLogger('Trailcam')


def init_logging():
  log_file = os.path.join('trailcam_log')
  logging.basicConfig(
      level=logging.DEBUG,
      datefmt='%Y-%m-%d %H:%M:%S')


def exit_handler(signum, frame):
  LOG.info('Exiting')
  sys.exit()


if __name__ == '__main__':
  init_logging()
  signal.signal(signal.SIGHUP, exit_handler)
  motion_sensor = MotionSensor(MOTION_SENSOR_PIN)
  while True:
    motion_sensor.wait_for_motion()
    LOG.info('Motion detected')
    while motion_sensor.motion_detected:
      LOG.info('Recording video')
      with PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.vflip = True
        camera.annotate_background = Color('black')
        camera.start_recording('/home/pi/video.h264')
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < 30:
          camera.annotate_text = 'Trailcam %s' % (
              datetime.now().strftime('%d-%m-%y %H:%M:%S'))
          camera.wait_recording(0.2)
        camera.stop_recording()
      sleep(0.5)
      timestamp = datetime.now().strftime('%d-%m-%y_%H-%M-%S')
      input_file = '/home/pi/video.h264'
      output_file = '/home/pi/%s.mp4' % timestamp
      call(['MP4Box', '-add', input_file, output_file])
    LOG.info('Motion ended')

