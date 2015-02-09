This repository contains the code for the Brocade Device Inventory Listener.

The listener listens to nova events and updates the vADX instances in 
the Brocade ADX Device Inventory Database


-  Download the Brocade ADX Inventory Listener Code

-  Install pysubnettree python module

    a. wget https://pypi.python.org/packages/source/p/pysubnettree/pysubnettree-0.23.tar.gz

    b. gunzip pysubnettree-0.23.tar.gz, untar the tar file, cd to the directory
   
    c. Run "python setup.py install" to install pysubnettree 
			
-  Modify the nova.conf to have the following changes

    [DEFAULT]

    notification_topics=brcd

    notify_on_state_change=vm_state

    notification_driver=nova.openstack.common.notifier.rpc_notifier

-  Copy inventory_listener.ini to /etc/neutron/services/loadbalancer/brocade directory
   Modify the inventory_listener.ini as applicable

-  Install Brocade ADX Device Driver Python Module. Please refer to install instructions under
   github.com/brocade-vadx/adx-device-driver

-  Restart nova-conductor, nova-scheduler,nova-api, nova-compute

-  To run the nova_listener as a background service do the following

            a. edit the brocade_adx_listener.sh to the correct install path
            b. copy the sh file into /etc/init.d/<servicename>
            c. service <servicename> start

   (or)

    Run "python nova_listener.py &" from the command prompt
