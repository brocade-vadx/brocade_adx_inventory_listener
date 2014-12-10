'''
 Copyright 2013 by Brocade Communication Systems
 All rights reserved.

 This software is the confidential and proprietary information
 of Brocade Communication Systems, ("Confidential Information").
 You shall not disclose such Confidential Information and shall
 use it only in accordance with the terms of the license agreement
 you entered into with Brocade Communication Systems.
'''
import inventory_conf as conf

'''
Created on Oct 14, 2013

@author: gayathri
'''
import SubnetTree
import logging
import threading
import os

LOG = logging.getLogger(__name__)

class BrocadeAdxSubnetLocator(object):
    def __init__(self):

        self.subnet_rlock=threading.RLock()
        self.init_subnet_tree()
        
    def init_subnet_tree(self):
        try:
            self.subnet_rlock.acquire(True)
            LOG.debug("Lock acquired by "+str(os.getpid()))
            self.subnet_tree=SubnetTree.SubnetTree()
            self.add_subnet("0.0.0.0/0")
            mgmt_network_str=conf.vadx_mgmt_network
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