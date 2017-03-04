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


class TrailCam():

  def __init__(self, camera, motion_sensor, output_dir,
               record_secs=30, annotate_text='Trailcam'):
    self.camera = camera
    self.motion_sensor = motion_sensor
    self.output_dir = output_dir
    self.record_secs = record_secs
    self.annotate_text = annotate_text
    self.shutdown_requested = False

  def run(self):
    output_file = os.path.join(self.output_dir, 'video.h264')
    while not self.shutdown_requested:
      self.motion_sensor.wait_for_motion(5.0)
      while self.motion_sensor.motion_detected:
        LOG.info('Recording video')
        self.camera.start_recording(output_file)
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < self.record_secs:
          self.camera.annotate_text = '%s %s' % (
              self.annotate_text, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
          self.camera.wait_recording(0.2)
        self.camera.stop_recording()
        LOG.info('Recording stopped')
        sleep(0.5)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        encoded_file = os.path.join(self.output_dir, '%s.mp4' % timestamp)
        LOG.info('Encoding file ' + encoded_file)
        encode_mp4(output_file, encoded_file)

  def request_shutdown(self):
    self.shutdown_requested = True


def encode_mp4(input_file, output_file):
  call(['MP4Box', '-add', input_file, output_file])


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


def init_logging(log_dir=None):
  root_logger = logging.getLogger('')
  root_logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(formatter)
  root_logger.addHandler(console_handler)
  if log_dir:
    log_file = os.path.join(log_dir, 'trailcam.log')
    file_handler = TimedRotatingFileHandler(log_file, when='D', backupCount=7)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


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
  parser.add_argument('--record-secs', type=int, default=30)
  parser.add_argument('--annotate-text', dest='annotate_text', default='Trailcam')
  return parser.parse_args()


def main():
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
  LOG.info('Starting trailcam')
  trailcam = TrailCam(
      camera,
      motion_sensor,
      args.output_dir,
      record_secs=args.record_secs,
      annotate_text=args.annotate_text)

  def shutdown_handler(signum, frame):
    LOG.info('Signaling shutdown')
    trailcam.request_shutdown()

  signal.signal(signal.SIGTERM, shutdown_handler)
  signal.signal(signal.SIGHUP, shutdown_handler)

  try:
    trailcam.run()
  except KeyboardInterrupt:
    pass
  finally:
    camera.close()

  LOG.info('Exiting')


if __name__ == '__main__':
  main()
