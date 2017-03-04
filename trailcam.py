import argparse
import logging
import os
import signal
import sys

from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from gpiozero import MotionSensor
from picamera import Color, PiCamera
from subprocess import call
from time import sleep


MOTION_SENSOR_PIN = 17

LOG = logging.getLogger('Trailcam')


def init_logging(log_dir=None):
  root_logger = logging.getLogger('')
  root_logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(formatter)
  root_logger.addHandler(console_handler)
  if log_dir:
    log_file = os.path.join(log_dir, 'trailcam.log')
    file_handler = TimedRotatingFileHandler(log_file, when='M', backupCount=7)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def exit_handler(signum, frame):
  LOG.info('Exiting')
  sys.exit()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--log-dir', '-l', dest='log_dir', default=os.path.dirname(os.path.realpath(__file__)))
  args = parser.parse_args()
  init_logging(log_dir=args.log_dir)
  signal.signal(signal.SIGHUP, exit_handler)
  LOG.info('Starting up')
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

