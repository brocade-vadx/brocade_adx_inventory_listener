import inventory_conf as admin_config

__author__ = 'Gayathri Venkataraman'

import logging
import threading
import logging.handlers as handlers
from datetime import datetime
from novaclient.v1_1 import client as novaclient
from neutronclient.v2_0 import client as neutronclient

from utils.brocade_adx_network_matcher import BrocadeAdxSubnetLocator
from brocade_neutron_lbaas.db.db_base import configure_db
from brocade_neutron_lbaas.db.adx_lb_db_plugin import AdxLoadBalancerDbPlugin
from brocade_neutron_lbaas.db.context import Context
import utils.adx_inventory_constants as constants

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename=admin_config.log_dir+'adx_inventory.log', filemode='w', level=logging.DEBUG,format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = handlers.RotatingFileHandler(
       "adx_inventory.log", maxBytes=500000000, backupCount=10)
log.addHandler(handler)


def logWrapper(method):
    def wrapper(*args, **kwargs):

        log.debug('BrocadeAdxDeviceManager %s called with arguments %s %s'
                  % (method.__name__, args, kwargs))
        return method(*args, **kwargs)
    return wrapper

class BrocadeADXDeviceManager():
    def __init__(self):
        # add checks and validation
      self.dm_rlock=threading.RLock()
      self.context=Context()
      self.plugin=AdxLoadBalancerDbPlugin()
      configure_db(admin_config.database)
      self._nova_client=self._get_nova_client()
      self._neutron_client=self._get_neutron_client()
      self._mgmt_network_locator= BrocadeAdxSubnetLocator()

    def _get_nova_client(self):
        return novaclient.Client(
               admin_config.admin_username,
               admin_config.admin_password,
               auth_url=admin_config.auth_url,
               tenant_id=admin_config.admin_tenant_id)

    def _format_date(self, date_str):
        fmt = '%Y-%m-%d %H:%M:%S'
        try:
            formated_date = datetime.strptime(date_str, fmt)
            return formated_date
        except ValueError, v:
            ulr = len(v.args[0].partition('unconverted data remains: ')[2])
            if ulr:
                date_str = datetime.strptime(date_str[:-ulr], fmt)
                return date_str
            else:
                raise v


    def build_instance_dict(self,ins_dict,notification):

        ins_dict['tenant_id']=notification['tenant_id']
        ins_dict['nova_instance_id']=notification[constants.nova_instance_id]
        ins_dict['name']=notification['hostname']
        ins_dict['user']=admin_config.vadx_username
        ins_dict['password']=admin_config.vadx_password
        ins_dict['status']=notification['state']
        ins_dict['communication_type']=admin_config.vadx_communication_type
        #ins_dict['created_time']=datetime.strptime(notification['created_at'],'%Y-%m-%d %H:%M:%S')
        ins_dict['created_time']=self._format_date(notification['created_at'])
        ins_dict['status_description']=notification['state_description']
        return ins_dict

    @logWrapper
    def process_notification(self, event_type,notification):
        self.dm_rlock.acquire(True)
        try:
            log.info("Processing vadx notification for Host "+ str(notification[constants.nova_instance_host_name])+" tenant "+str(notification[constants.nova_instance_tenant_id]))
            filters={'nova_instance_id':notification[constants.nova_instance_id]}
            insList=self.plugin.get_adxloadbalancer(self.context,filters)
            ins=None
            if len(insList)!=0:
                ins=insList[0]
            # check in database if the entry exists, add as applicable
            if event_type in constants.nova_create_start_event:
                #ins=self._nova_client.servers.get(notification[constants.nova_instance_id])
                log.info("got instance")
                if ins==None:
                    ins_dict={}
                    ins_dict=self.build_instance_dict(ins_dict,notification)
                    log.debug("Creating adx instance in database %r" %(ins_dict,))
                    self.plugin.create_adxloadbalancer(ins_dict,self.context)

            elif event_type in constants.nova_delete_end_event:
                if ins!=None:
                    log.debug("Deleting adx from the database %r" %(ins,))
                    self.plugin.delete_adxloadbalancer(ins['id'],self.context)

            elif event_type in constants.TRANSITION_EVENTS:

                if ins!=None:
                    log.debug("Device will be put in transition state and cannot be used for configuration %r" %(ins,))
                    ins_dict={'id':ins['id'],'status':"IN-TRANSITION",'status_description':notification['state_description']}
                    self.plugin.update_adxloadbalancer(ins_dict,self.context)
            elif event_type in constants.RESTORE_EVENTS or event_type in constants.SHUTOFF_EVENTS:
                 if ins!=None:
                    log.debug("Device state will be updated %r"%(ins,))
                    ins_dict={'id':ins['id'],'status':notification['state'],'status_description':notification['state_description']}
                    self.plugin.update_adxloadbalancer(ins_dict,self.context)


            elif event_type in constants.nova_update_event:
                # check if device exists, if not create and update status
                if ins==None:
                    ins_dict={}
                    try:
                        nova_ins=self._nova_client.servers.get(notification[constants.nova_instance_id])
                    except Exception as e:
                        log.exception(e.message,e.args)
                        log.error("Nova instance and db instance does not exist stale notification ...ignoring")
                        return

                    ins_dict=self.build_instance_dict(ins_dict,notification)
                    log.debug("Creating adx instance in database %r" %(ins_dict,))
                    ins_dict=self.plugin.create_adxloadbalancer(ins_dict,self.context)
                    ins=ins_dict

                if ins!=None :
                    ins_dict={'id':ins['id'],'status_description':notification['state_description']}
                    if (ins['status']=="IN-TRANSITION" and notification['new_task_state']==None):
                        ins_dict['status']=notification['state']
                        ins['status']=notification['state']
                    elif ins['status']!="IN-TRANSITION":
                         ins_dict['status']=notification['state']
                         ins['status']=notification['state']
                    log.debug("Updating status for device %r" %(ins_dict,))
                    self.plugin.update_adxloadbalancer(ins_dict, self.context)

                if ins['ports']==None or len(ins['ports'])==0:
                    ports=[]
                    if notification[constants.nova_instance_terminated_at]=="":
                        nova_ins=None
                        try:
                            nova_ins=self._nova_client.servers.get(notification[constants.nova_instance_id])
                        except Exception as e:
                            log.exception(e.message,e.args)
                            log.error("Nova instance and db instance does not exist stale notification ...ignoring")
                            return
                        log.info("got instance")
                        networks =nova_ins.addresses
                        macs=[]
                        if networks:
                            for network in networks.iterkeys():
                                ips = networks[network]
                                for mac in ips:
                                    macs.append(mac['OS-EXT-IPS-MAC:mac_addr'])
                            networks=self._get_networks_for_device(macs)
                            if len(networks)!=0:
                                self._create_ips_and_ports(ins,networks)

            elif event_type in constants.nova_create_end_event:
                ins['status']=notification['state']
                if (ins['ports']==None or len(ins['ports'])==0):
                    fixed_ips=notification[constants.nova_instance_fixed_ips]
                    instance_macs=[]
                    ports=[]
                    for fixed_ip in fixed_ips:
                        mac=fixed_ip[constants.nova_port_mac]
                        instance_macs.append(mac)
                    networks=self._get_networks_for_device(instance_macs)
                    if len(networks)!=0:
                        # add the networks to instance and commit to database
                        self._create_ips_and_ports(ins,networks)
                else:
                    ins_up_dict={'id':ins['id'],'status':ins['status']}
                    ins=self.plugin.update_adxloadbalancer(ins_up_dict,self.context)
        except Exception as e:
            log.exception(e.message,e.args)
        finally:
            self.dm_rlock.release()



    def _get_networks_for_device(self,macs):
        portlist=self._neutron_client.list_ports()
        networks=[]
        if portlist!=None:
            ports=portlist[constants.neutron_ports]
            if ports!=None:
                for port in ports:
                    if port[constants.nova_mac_address] in macs:
                        networkList=port[constants.nova_instance_fixed_ips]
                        network=networkList[0]
                        network['status']=port[constants.status]
                        network['network_id']=port[constants.neutron_network_id]
                        network['mac']=port[constants.nova_mac_address]
                        networks.append(network)

        return networks



    def _create_ips_and_ports(self,ins,networks):
        ports=[]
        for network in networks:
                log.info("Network: %r" % (network, ))
                log.info("Network: %r" % (network, ))
                port={'subnet_id':network['subnet_id'],
                      'status':network['status'],
                      'mac':network['mac'],
                      'ip_address':network['ip_address'],
                      'network_id':network['network_id'],
                      'adx_lb_id':ins['id']}
                port=self.plugin.create_port(port,self.context)
                ports.append(port)
                subnet = self._mgmt_network_locator.get_subnet(network['ip_address'])
                if subnet!="0.0.0.0/0":
                    log.info("Management _ip :"+ network['ip_address'])
                    ins['management_ip']=network['ip_address']
                    ins_up_dict={'id':ins['id'],'management_ip':ins['management_ip']}
                    self.plugin.update_adxloadbalancer(ins_up_dict, self.context)
        ins['ports']=ports



    def _get_neutron_client(self):
        return neutronclient.Client(
                username=admin_config.admin_username,
                password=admin_config.admin_password,
                tenant_id=admin_config.admin_tenant_id,
                auth_url=admin_config.auth_url)


    def get_adx_loadbalancer(self,subnet_id):
        filters={'Port.subnet_id':subnet_id}
        adx= self.plugin.get_adxloadbalancer(self.context,filters)
        if len(adx)==0:
            filters={'Port.subnet_id':'ALL'}
            adx=self.plugin.get_adxloadbalancer(self.context,filters)

        return adx