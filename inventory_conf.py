
__author__ = 'Gayathri Venkataraman'

vadx_image_id='2c396205-457e-4fec-b435-b8a219fb0172'
# add multiple networks comma seperated "1.1.1.0/24","2.2.2.0/24" etc
vadx_mgmt_network='1.1.1.0/24'
vadx_username='admin'
vadx_password='brocade'
vadx_communication_type='HTTP'
admin_username='admin'
admin_password='password'
admin_tenant_id='2646ae9d9a86440a8eeefa84670c6c95'

#transport url rabbit://<rabbit_username:<rabbit_password>@controllerip:5672/
transport_url='rabbit://guest:password@10.24.140.231:5672/'

#auth_url http://<controllerip>:35357/v2.0
auth_url='http://10.24.140.231:35357/v2.0'

#database url
database='mysql://admin:default@10.24.140.230/brocade'

#logging directory
log_dir="/var/log/adx_inventory/"
#DEBUG,INFO,ERROR
log_level="DEBUG"