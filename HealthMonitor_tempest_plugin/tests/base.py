import tempest.test
import logging
from tempest import config

import ipaddress

from tempest.lib.common.utils import data_utils

from tempest.lib.common.utils.linux import remote_client 

import sys 
import time

from HealthMonitor_tempest_plugin.common.manager import Manager 

CONF = config.CONF

#setup logging to output to console
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
handler.setFormatter(formatter)
LOG.addHandler(handler)

class BaseHealthCheck(tempest.test.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(BaseHealthCheck, self).__init__(*args, **kwargs)  
        self.manager = Manager()

    @classmethod
    def skip_checks(cls):
        super(BaseHealthCheck,cls).skip_checks()

        if not CONF.service_available.nova:
            raise cls.skipException("Nova is not available, cannot perform Health Check")

    @classmethod
    def resource_setup(cls):
        super(BaseHealthCheck, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(BaseHealthCheck, cls).resource_cleanup()

    def get_port(self, id):
        ports = self.manager.ports_client.list_ports(device_id=id)['ports']

        def _is_active(port):
            return (port['status'] == 'ACTIVE' or
                port.get('binding:vnic_type') == 'baremetal')

        try:
            port_map = [(p["id"], fxip["ip_address"])
                    for p in ports
                    for fxip in p["fixed_ips"]
                    if (ipaddress.ip_address(fxip["ip_address"]) and
                        _is_active(p))]
        except:
            LOG.warning('INVALID IP FOUND IN CONFIG')

        inactive = [p for p in ports if p['status'] != 'ACTIVE']

        if inactive:
            LOG.warning("Instance has ports that are not ACTIVE: %s", inactive)

        self.assertNotEmpty(port_map,
                            "No IPv4 addresses found in: %s" % ports)
        self.assertEqual(len(port_map), 1,
                        "Found multiple IPv4 addresses: %s. "
                        "Unable to determine which port to target."
                        % port_map)

        return port_map[0]

    def get_image(self,id):
        return self.manager.image_client_v2.show_image(id)['name']

    def get_flavor(self,id):

        return self.manager.flavors_client.show_flavor(id)['flavor']['name']

    def clean_up_server(self,server_id,SERVER_NAME,KEYPAIR_NAME, fip_id=None, fip=None):

        LOG.info('Test finished, cleaning up...')

        self.manager.servers_client.delete_server(server_id)
        LOG.info('Deleted server "%s"',SERVER_NAME)

        self.manager.keypairs_client.delete_keypair(KEYPAIR_NAME)
        LOG.info('Deleted keypair "%s"',KEYPAIR_NAME)

        if fip_id:
            self.manager.floating_ips_client.delete_floatingip(fip_id)
            LOG.info('Deleted floating ip %s',fip)


    def create_server_and_get_ssh(self,ssh_user,image,flavor):

        SERVER_NAME = data_utils.rand_name(name='server',prefix='healthmon')
        KEYPAIR_NAME = data_utils.rand_name(name='keypair',prefix='healthmon')

        IMG_NAME = self.get_image(image)
        FLV_NAME = self.get_flavor(flavor)

        LOG.info('PERFORMING BASIC SSH TEST WITH IMAGE "%s" AND FLAVOR "%s"',IMG_NAME,FLV_NAME)

        r = self.manager.keypairs_client.create_keypair(name=KEYPAIR_NAME)
        pk = r['keypair']['private_key']
        pubk = r['keypair']['public_key']
        LOG.info("Generated SSH keypair '%s'",KEYPAIR_NAME)
        LOG.info("pub_key: %s",pubk)
        
        LOG.info('Creating server...')
        t1 = time.perf_counter()
        r = self.manager.servers_client.create_server(name=SERVER_NAME, imageRef=image, flavorRef=flavor, key_name=KEYPAIR_NAME, networks=[{'uuid': CONF.network.public_network_id}]);
        t2 = time.perf_counter()

        id = r['server']['id']

        LOG.info('server_name : %s server_id : %s',SERVER_NAME,id)
        LOG.info('---------------------------')
        LOG.info('Time to create server : {:3.4f}s'.format(t2-t1))
        
        LOG.info('Waiting for server to become active...')
        t1 = time.perf_counter()
        while True:
            r = self.manager.servers_client.show_server(id)
            LOG.info("Polling...")
            LOG.info('STATUS: %s',r['server']['status'])
            if r['server']['status'] == "ACTIVE":
                t2 = time.perf_counter()
                tenant_id = r['server']['tenant_id']
                break
            elif r['server']['status'] == "ERROR":
                LOG.error("Fatal: Server Status ERROR")
                LOG.error('reason: "%s"',r['server']['fault']['message'])
                LOG.error('details: %s',r['server']['fault']['details'])
                LOG.error("test failed for image '%s' and flavor '%s'",IMG_NAME,FLV_NAME)
                self.clean_up_server(id,SERVER_NAME,KEYPAIR_NAME)
                return
            else:
                time.sleep(CONF.compute.ready_wait)
        LOG.info("Got server status ready")
        LOG.info('Time to complete (note: this time may be affected by the polling period "ready_wait" configured in tempest (/etc/tempest.conf)): {:3.4f}s'.format(t2-t1))
        LOG.info('---------------------------')
        
        LOG.info("Attempting to ssh into server...")
        LOG.info("Getting ports for server with id: %s",id)
        port_id,ipv4 = self.get_port(id)
        LOG.info("Got port_id %s for server_ip %s",port_id,ipv4)
        #only need floating ip assignment if networking setup requires it - manually configure this in /etc/tempest.conf
        if (CONF.network_feature_enabled.floating_ips and 
            CONF.network.floating_network_name):    
            LOG.info("Creating a new floating ip...")
            kwargs = {
                'floating_network_id' : CONF.network.floating_network_name,
                'port_id' : port_id, 
                'tenant_id' : tenant_id, 
                'fixed_ip_address' : ipv4
            }

            if CONF.network.subnet_id:
                kwargs['subnet_id'] = CONF.network.subnet_id

            r = self.manager.floating_ips_client.create_floatingip(**kwargs)
            name = self.manager.servers_client.show_server(id)['server']['name']

            fip = r['floatingip']['floating_ip_address']
            fip_id = r['floatingip']['id']
            fxp = r['floatingip']['fixed_ip_address']

            #just stuff for logging
            net_name = self.manager.networks_client.show_network(r['floatingip']['floating_network_id'])['network']['name']

            if CONF.identity.auth_version == 'v3':
                project_name = self.manager.projects_client.show_project(r['floatingip']['tenant_id'])['project']['name']
            else:
                project_name = self.manager.tenants_client.show_tenant(r['floatingip']['tenant_id'])['tenant']['name']
            
            LOG.info('Created new floating ip %s on network "%s" bound to server "%s" with ip %s in project "%s"',fip,net_name,name,fxp,project_name)

            ipv4 = fip

        #establish ssh connection
        LOG.info('Starting SSH connection ...')
        LOG.info('Using ip %s, username "%s"',ipv4, ssh_user)
        #password is temporary measure for cirros issue, need to remove this when possible
        client = remote_client.RemoteClient(ipv4, ssh_user, pkey=pk, password='gocubsgo',ssh_key_type='ecdsa')
        client.validate_authentication()
        LOG.info('SSH test for image "%s" and flavor "%s" succeeded!',IMG_NAME,FLV_NAME)
        LOG.info('---------------------------')
        self.clean_up_server(id,SERVER_NAME,KEYPAIR_NAME,fip_id,fip)