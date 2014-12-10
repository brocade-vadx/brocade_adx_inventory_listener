This repository contains the code for the Brocade Device inventory listener. The listener listens to nova events to manage
Brocade adx device inventory


1. Download the code

2. run "python setup.py install

3. pip install configparser

4. copy the device_inventory.ini to /etc/neutron/services/loadbalancer/brocade

5. Modify the ini file to point to the database to which the device driver will connect to

6. Modify the nova.conf to have the following changes

    [DEFAULT]
    notification_topics=brcd
    notify_on_state_change=vm_state
    notification_driver=nova.openstack.common.notifier.rpc_notifier

 7. Modify the inventory.conf as applicable

 8. The brocade adx device driver python libraries need to be installed . Please refer to instructions under
    github.com/brocade-vadx/adx-device-driver

 9. Restart nova-conductor, nova-scheduler,nova-api, nova-compute

 10. 

 11. If you want to run the nova_listener as a background service follow the following

            a. edit the brocade_adx_listener.sh to the correct install path
            b. copy the sh file into /etc/init.d/<servicename>
            c. service <servicename> start

     or if you do not want it as a service run it as python nova_listener.py &









