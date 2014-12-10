__author__ = 'Gayathri Venkataraman'
# nova notification constants
nova_instance_host_name='hostname'
nova_instance_tenant_id='tenant_id'
nova_instance_fixed_ips='fixed_ips'
nova_port_mac='vif_mac'
nova_instance_id='instance_id'
nova_instance_terminated_at='terminated_at'
# nova client constants
neutron_ports='ports'
nova_mac_address='mac_address'
status='status'
neutron_network_id='network_id'
TRANSITION_EVENTS=['compute.instance.delete.start','compute.instance.power_off.start','compute.instance.reboot.start','compute.instance.pause.start',
                   'compute.instance.shutdown.start','compute.instance.delete_ip.start','compute.instance.rebuild.start','compute.instance.resize.prep.start',
                   'compute.instance.resize.prep.end','compute.instance.resize.start','compute.instance.resize.revert.start']
RESTORE_EVENTS=['compute.instance.power_on.end','compute.instance.reboot.end','compute.instance.unpause.end','compute.instance.resume','compute.instance.resize.end','compute.instance.finish_resize.start',
                'compute.instance.finish_resize.end','compute.instance.finish_resize.start','compute.instance.resize.revert.end','compute.instance.resize.confirm.start','compute.instance.resize.confirm.end'
]
SHUTOFF_EVENTS=['compute.instance.power_off.end','compute.instance.pause.end','compute.instance.shutdown.end','compute.instance.suspend']
nova_create_start_event='compute.instance.create.start'
nova_create_end_event='compute.instance.create.end'
nova_delete_end_event='compute.instance.delete.end'
nova_update_event='compute.instance.update'

