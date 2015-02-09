import ConfigParser
from oslo.config import cfg

brocade_device_inventory_listener_opts = [
    cfg.StrOpt('device_inventory_listener_file_name',
               default='/etc/neutron/services/loadbalancer/'
                       'brocade/inventory_listener.ini',
               help=_('file containing the brocade device inventroy listener properties'))]
cfg.CONF.register_opts(brocade_device_inventory_listener_opts, "brocade")

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(cfg.CONF.brocade.device_inventory_listener_file_name)
