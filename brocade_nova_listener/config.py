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

import ConfigParser
from oslo.config import cfg

brocade_device_inventory_listener_opts = [
    cfg.StrOpt('device_inventory_listener_file_name',
               default='/etc/neutron/services/loadbalancer/'
                       'brocade/brocade_nova_listener.ini',
               help="file containing the brocade nova listener properties")]
cfg.CONF.register_opts(brocade_device_inventory_listener_opts, "brocade")

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(cfg.CONF.brocade.device_inventory_listener_file_name)
