#!/usr/bin/env python
# coding: utf-8

import logging
import logging
import logging.handlers as handlers
import ConfigParser

from oslo.config import cfg
from oslo import messaging
import eventlet

from adx_device_manager import BrocadeADXDeviceManager
from config import CONFIG
eventlet.monkey_patch()

import os
pid = os.getpid()
op = open("/opt/stack/status/brocade_nova_listener.pid","w")
op.write("%s" % pid)
op.close()

FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
log_dir = CONFIG.get("DEFAULT", "log_dir")
log_file_name = log_dir  + "/" + "adx_inventory.log"
log_level = CONFIG.get("DEFAULT", "log_level").upper()
logging.basicConfig(filename = log_file_name,
                    filemode='w', level=log_level,
                    format=FORMAT)
logger = logging.getLogger()
logger.setLevel(log_level)
handler = handlers.RotatingFileHandler(
       log_file_name,
       maxBytes=50000,
       backupCount=10)
formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)

LOG = logging.getLogger(__name__)


class NotificationHandler(object):
    def __init__(self):
        self.adx_inv_manager= BrocadeADXDeviceManager()

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.info(event_type)
        if str(event_type).startswith("compute.instance"):
            LOG.info("RECEIVED MESSAGE: %r" % (payload, ))
            image_url=str(payload['image_ref_url'])

            vadx_image_ids = CONFIG.get("DEFAULT", "vadx_image_ids").split(",")
            #vadx_image_ids = admin_config.vadx_image_id.split(",")
            if vadx_image_ids == None or len(vadx_image_ids) == 0:
                LOG.error("No valid vadx image id specified in the config file")
                return

            for vadx_imag_id in vadx_image_ids:
                if vadx_image_id in image_url:
                    LOG.info("vadx instance notification received ")
                    self.adx_inv_manager.process_notification(event_type,payload)
                    return
                else:
                    LOG.info("Notification is not for vadx")

    def warn(self, ctxt, publisher_id, event_type, payload, metadata):
        pass

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        pass

    def debug(self, ctx, publisher_id, event_type, payload, metadata):
        LOG.debug(event_type)
        LOG.debug("RECEIVED MESSAGE: %s" % (payload['instance_id'], ))

LOG.info('configuring connection')
transport_url = CONFIG.get("DEFAULT", "transport_url")
transport = messaging.get_transport(cfg.CONF, transport_url)
targets = [messaging.Target(topic='brcd',exchange='nova')]
endpoints = [NotificationHandler()]
server = messaging.get_notification_listener(transport,
                                             targets,
                                             endpoints,
                                             allow_requeue=True,
                                             executor='eventlet')
LOG.info('starting up server')
server.start()
LOG.info('waiting for nova events/notifications')
server.wait()

