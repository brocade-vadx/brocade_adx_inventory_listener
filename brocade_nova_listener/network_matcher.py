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

import SubnetTree
import logging
import threading
import os

from config import CONFIG

LOG = logging.getLogger(__name__)

class SubnetLocator(object):
    def __init__(self):

        self.subnet_rlock=threading.RLock()
        self.init_subnet_tree()
        
    def init_subnet_tree(self):
        try:
            self.subnet_rlock.acquire(True)
            LOG.debug("Lock acquired by "+str(os.getpid()))
            self.subnet_tree=SubnetTree.SubnetTree()
            self.add_subnet("0.0.0.0/0")
            mgmt_network_str=CONFIG.get("DEFAULT", "vadx_mgmt_network")
            subnet_list=mgmt_network_str.split(",")
            if(subnet_list==None or len(subnet_list)==0):
                LOG.debug("No subnets in the db..subnet tree initialized")
            else :
                for subnet in subnet_list:
                    self.add_subnet(subnet)

        finally:
            self.subnet_rlock.release()


    def add_subnet(self,subnet_str):

        LOG.debug("Adding subnet to tree "+subnet_str)
        try:
            self.subnet_rlock.acquire(True)
            LOG.debug("Lock acquired by "+str(os.getpid()))
            self.subnet_tree.insert(subnet_str,subnet_str)
        finally:
            self.subnet_rlock.release()
    
    def delete_subnet(self,subnet_str):

        LOG.debug("Deleting subnet from tree "+subnet_str)
        try:
            self.subnet_rlock.acquire(True)
            LOG.debug("Lock acquired by "+str(os.getpid()))
            self.subnet_tree.remove(subnet_str)
        finally:
            self.subnet_rlock.release()
        
    
    def get_subnet(self,ip):
        ipaddress=str(ip)
        subnetstr=None
        try:
            self.subnet_rlock.acquire(False)
            LOG.debug("Lock acquired by "+str(os.getpid()))
            if(ipaddress in self.subnet_tree):
                subnetstr = self.subnet_tree[ipaddress]
                LOG.debug(" The ip "+ipaddress+" is in subnet "+subnetstr)
        finally:
            self.subnet_rlock.release()
            return subnetstr
