#!/usr/bin/env python
# coding: utf-8

import logging

from oslo.config import cfg
from oslo import messaging
import eventlet

import inventory_conf as admin_config
from adx_device_manager import BrocadeADXDeviceManager
eventlet.monkey_patch()

logging.basicConfig()
log = logging.getLogger()

log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

import os
pid = os.getpid()
op = open("/var/brocade_nova_listener.pid","w")
op.write("%s" % pid)
op.close()

class NotificationHandler(object):

    def __init__(self):
        self.adx_inv_manager= BrocadeADXDeviceManager()

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        log.info(event_type)
        if str(event_type).startswith("compute.instance"):
            log.info("RECEIVED MESSAGE: %r" % (payload, ))
            image_url=str(payload['image_ref_url'])

            if str(admin_config.vadx_image_id) in image_url:
                log.info("Vadx instance notification received ")
                self.adx_inv_manager.process_notification(event_type,payload)
            else:
                log.info("Notification is not for vadx")




    def warn(self, ctxt, publisher_id, event_type, payload, metadata):
        pass

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        pass

    def debug(self, ctx, publisher_id, event_type, payload, metadata):
        log.debug(event_type)
        log.debug("RECEIVED MESSAGE: %s" % (payload['instance_id'], ))

log.info('Configuring connection')
transport_url = admin_config.transport_url
transport = messaging.get_transport(cfg.CONF, transport_url)
targets = [messaging.Target(topic='brcd',exchange='nova')]
endpoints = [NotificationHandler()]
server = messaging.get_notification_listener(transport, targets, endpoints, allow_requeue=True, executor='eventlet')
log.info('Starting up server')
server.start()
log.info('Waiting for something')
server.wait()

