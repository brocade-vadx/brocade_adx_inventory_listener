# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 Brocade, Inc.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import sys
import eventlet
eventlet.monkey_patch()

import logging
import logging.handlers as handlers
import ConfigParser

from oslo.config import cfg
from oslo import messaging
import eventlet

from device_manager import DeviceManager
from config import CONFIG
eventlet.monkey_patch()

FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
log_dir = CONFIG.get("DEFAULT", "log_dir")
log_file_name = log_dir  + "/" + "brocade_nova_listener.log"
log_level = CONFIG.get("DEFAULT", "log_level").upper()
logging.basicConfig(filename = log_file_name,
                    filemode='w', level=log_level,
                    format=FORMAT)
logger = logging.getLogger()
logger.setLevel(log_level)
handler = handlers.RotatingFileHandler(
       log_file_name,
       maxBytes=20000000,
       backupCount=10)
formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)

LOG = logging.getLogger(__name__)


class NotificationHandler(object):
    def __init__(self):
        self.adx_inv_manager= DeviceManager()

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.info(event_type)
        if str(event_type).startswith("compute.instance"):
            #LOG.info("RECEIVED MESSAGE: %r" % (payload, ))
            image_url=str(payload['image_ref_url'])

            vadx_image_id = CONFIG.get("DEFAULT", "vadx_image_ids")
            if vadx_image_id in image_url:
                LOG.info("vadx instance notification received ")
                LOG.info("RECEIVED MESSAGE: %r" % (payload, ))
                self.adx_inv_manager.process_notification(event_type,payload)
                return
            else:
                LOG.info("Notification is not for vadx")
        else:
            #LOG.info("RECEIVED MESSAGE: %r" % (payload, ))
            pass
            

    def warn(self, ctxt, publisher_id, event_type, payload, metadata):
        pass

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        pass

    def debug(self, ctx, publisher_id, event_type, payload, metadata):
        pass
        #LOG.debug(event_type)
        #LOG.debug("RECEIVED MESSAGE: %s" % (payload['instance_id'], ))

def main(argv=sys.argv[1:]):
    try:
        LOG.info('configuring connection')
        transport_url = CONFIG.get("DEFAULT", "transport_url")
        transport = messaging.get_transport(cfg.CONF, transport_url)
        targets = [messaging.Target(topic='brcd',exchange='nova')]
        #targets = [messaging.Target(topic='brcd']
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
    except KeyboardInterrupt:
        print("... exiting brocade nova listener")
        return 130
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":
    main()

