#! /usr/bin/env python3
import logging

from flask_injector import FlaskInjector

from app import app
from app.dep_inject import WatchTheDoorModule
from app.face_detector import Detector
from os.path import abspath, dirname
from os import chdir

abs_path = abspath(__file__)
dir = dirname(abs_path)
chdir(dir)

logging.basicConfig(format='%(asctime)s %(message)s')
logging.root.setLevel(logging.WARN)
inj = FlaskInjector(app=app, modules=[WatchTheDoorModule])
det = inj.injector.get(Detector)
det.launch_detect_job()

app.run(host='0.0.0.0', threaded=True)
