from math import frexp
from re import S
from HealthMonitor_tempest_plugin.tests.base import BaseHealthCheck
import sys
import time

import testtools
import logging

from tempest import config

CONF = config.CONF
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
handler.setFormatter(formatter)

LOG.addHandler(handler)


class BasicTest(BaseHealthCheck):

    def __init__(self, *args, **kwargs):
        super(BasicTest,self).__init__(*args,**kwargs)

    @testtools.testcase.attr('positive')
    def test_basic(self):
        resp1 = self.manager.keypairs_client.create_keypair(name='yeet')
        pk = resp1['keypair']['private_key']
        pubk = resp1['keypair']['public_key']
        LOG.info("Generated SSH keypair...")
        LOG.info("pub_key: %s",pubk )
        

        server_create_time_b = time.perf_counter()
        resp = self.manager.servers_client.create_server(name='test-server', imageRef=CONF.compute.image_ref, flavorRef=CONF.compute.flavor_ref, key_name='yeet', networks=[{'uuid': CONF.network.public_network_id}]);
        server_create_time_a = time.perf_counter()

        id = resp['server']['id']

        LOG.info('server_id : %s',id)
        LOG.info('---------------------------')
        #print(resp)
        LOG.info('Time to create server : {:3.4f}'.format(server_create_time_a-server_create_time_b))
        
        LOG.info('Waiting for server to become active...')

        while True:
            r = self.manager.servers_client.show_server(id)
            LOG.info("Polling...")
            LOG.info('SERVER_STATUS: %s',r['server']['status'])
            if r['server']['status'] == "ACTIVE":
                tenant_id = r['server']['tenant_id']
                break
            else:
                time.sleep(CONF.compute.ready_wait)
            
        LOG.info("Got server status ready")
        LOG.info('---------------------------')
        
        LOG.info("Attempting to ssh into server...")
        if (CONF.network_feature_enabled.floating_ips and 
            CONF.network.floating_network_name):
            LOG.info("Getting ports for server with id: %s",id)
            port_id,ipv4 = self.get_port(id)
            LOG.info("Got port_id %s for server_ip %s",port_id,ipv4)
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
            fxp = r['floatingip']['fixed_ip_address']

            net_name = self.manager.networks_client.show_network(r['floatingip']['floating_network_id'])['network']['name']

            if CONF.identity.auth_version == 'v3':
                project_name = self.manager.projects_client.show_project(r['floatingip']['tenant_id'])['project']['name']
            else:
                project_name = self.manager.tenants_client.show_tenant(r['floatingip']['tenant_id'])['tenant']['name']
            
            LOG.info('Created new floating ip %s on network "%s" bound to server "%s" with ip %s in project "%s"',fip,net_name,name,fxp,project_name)


        # resp2 = self.manager.servers_client.delete_server(resp['server']['id'])

        #wait for float ip to come up 
        self.manager.keypairs_client.delete_keypair('yeet')
        self.assertEqual('yes','yes');
        