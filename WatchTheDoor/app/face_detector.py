from logging import Logger
from urllib.request import urlopen
from uuid import uuid4

import cv2
import numpy as np
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.interval import IntervalTrigger
from injector import inject, singleton

from app.configurator import AppConfig
from app.send_message import MessageSender


@singleton
class Detector(object):
    JOB_NAME = 'DETECT_JOB'

    @inject
    def __init__(self, ac: AppConfig, sender: MessageSender, scheduler: BaseScheduler, logger: Logger):
        self.config = ac
        self.sender = sender
        self.scheduler = scheduler
        self.trigger = IntervalTrigger(seconds=self.config.interval)
        self.post_find_trigger = IntervalTrigger(seconds=self.config.post_find_interval)
        self.logger = logger

    def launch_detect_job(self):
        self.logger.info("launching teh job")
        return self.scheduler.add_job(
            func=self._take_pic,
            trigger=self.trigger,
            id=Detector.JOB_NAME,
            name="Detect faces at the door",
            replace_existing=True
        )

    def _fetch_image_bytes(self):
        """
        Fetch a snapshot from the uv4L server and return it as a numpy byte array
        """
        resp = urlopen("http://{}:8080/stream/snapshot.jpeg".format(self.config.host)).read()
        return np.asarray(bytearray(resp), dtype=np.uint8)

    def _detect_faces(self):
        return self._detect(self._fetch_image_bytes())

    def _take_pic(self):
        tupl = self._detect_faces()
        num, name = tupl
        job = self.scheduler.get_job(Detector.JOB_NAME)
        if num <= 0:
            self.logger.info("No faces found")
        if num > 0:
            self.logger.info("We found {:d} faces!!!!".format(num))
            self.sender.send(name)
            self.logger.info("Rescheduling teh job for two minutes from now")
            job.reschedule(self.post_find_trigger)
        elif job.trigger != self.trigger:
            self.logger.info("Rescheduling the job as normal!")
            job.reschedule(self.trigger)

    def _detect(self, img_bytes):
        casc_path = "/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml"
        face_casc = cv2.CascadeClassifier(casc_path)
        img = cv2.imdecode(img_bytes, -1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_casc.detectMultiScale(
            # here's where the tweaking happens
            gray,
            scaleFactor=1.01,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CV_FEATURE_PARAMS_HAAR
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            self.logger.info("Found face with width=%d height=%d" % (w, h))
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        numfaces = len(faces)
        if numfaces == 0:
            return 0, None

        name = '/tmp/' + str(uuid4()) + '.png'
        cv2.imwrite(name, img)
        return numfaces, name
