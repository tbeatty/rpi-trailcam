import argparse
import logging
import os
import picamera
import signal
import sys

from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from gpiozero import MotionSensor
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


def init_camera(sharpness=0, contrast=0, brightness=0, saturation=0, iso=0,
                stabilize=False, hflip=False, vflip=False):
  camera = picamera.PiCamera()
  camera.sharpness = sharpness
  camera.contrast = contrast
  camera.brightness = brightness
  camera.saturation = saturation
  camera.ISO = iso
  camera.video_stabilization = stabilize
  camera.hflip = hflip
  camera.vflip = vflip
  camera.resolution = (1024, 768)
  camera.annotate_background = picamera.Color('black')
  return camera


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--output-dir', '-o', dest='output_dir', default='/home/pi')
  parser.add_argument('--log-dir', '-l', dest='log_dir', default='/home/pi')
  parser.add_argument('--sharpness', type=int, default=0)
  parser.add_argument('--contrast', type=int, default=0)
  parser.add_argument('--brightness', type=int, default=50)
  parser.add_argument('--saturation', type=int, default=0)
  parser.add_argument('--iso', type=int, default=0)
  parser.add_argument('--stabilize', action='store_true')
  parser.add_argument('--hflip', action='store_true')
  parser.add_argument('--vflip', action='store_true')
  return parser.parse_args()


if __name__ == '__main__':
  args = parse_args()
  init_logging(log_dir=args.log_dir)
  LOG.info('Initializing')
  camera = init_camera(
      sharpness=args.sharpness,
      contrast=args.contrast,
      brightness=args.brightness,
      saturation=args.saturation,
      iso=args.iso,
      stabilize=args.stabilize,
      hflip=args.hflip,
      vflip=args.vflip)
  motion_sensor = MotionSensor(MOTION_SENSOR_PIN)
  output_file = os.path.join(args.output_dir, 'video.h264')
  shutdown_requested = False

  def shutdown_handler():
    LOG.info('Signaling shutdown')
    shutdown_requested = True

  while not shutdown_requested:
    LOG.info('Waiting for motion')
    motion_sensor.wait_for_motion()
    LOG.info('Motion detected')
    while motion_sensor.motion_detected:
      LOG.info('Recording video')
      camera.start_recording(output_file)
      start_time = datetime.now()
      while (datetime.now() - start_time).seconds < 30:
        camera.annotate_text = 'Trailcam %s' % (
            datetime.now().strftime('%d-%m-%y %H:%M:%S'))
        camera.wait_recording(0.2)
      camera.stop_recording()
      sleep(0.5)
      timestamp = datetime.now().strftime('%d-%m-%y_%H-%M-%S')
      encoded_file = os.path.join(args.output_dir, '%s.mp4' % timestamp)
      call(['MP4Box', '-add', output_file, encoded_file])
    LOG.info('Motion ended')

  camera.close()
  LOG.info('Exiting')

