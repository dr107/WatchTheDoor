#! /usr/bin/env python3
import logging

from flask_injector import FlaskInjector

from app import app
from app.dep_inject import WatchTheDoorModule
from app.face_detector import Detector

logging.basicConfig()
logging.root.setLevel(logging.WARN)
inj = FlaskInjector(app=app, modules=[WatchTheDoorModule])
det = inj.injector.get(Detector)
det.launch_detect_job()

app.run(host=det.config.host, threaded=True)
