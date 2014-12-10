__author__ = 'root'
from brocade_neutron_lbaas.adx_device_inventory import BrocadeAdxDeviceInventoryManager
if __name__ == '__main__':
    dm=BrocadeAdxDeviceInventoryManager(object)
    subnet_id='575e5549-2574-4b28-918d-b0ecc9a3d925'
    lb=dm.get_device(subnet_id)
    print("%r"%(lb,))
