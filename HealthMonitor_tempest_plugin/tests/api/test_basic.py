from math import frexp
from re import S
from termios import TAB2
from HealthMonitor_tempest_plugin.tests.base import BaseHealthCheck

from tempest.lib.common.utils.linux import remote_client 
import sys
import time

import testtools
import logging

from tempest import config

CONF = config.CONF

DEFAULT_SERVER_NAME = 'test-server'
DEFAULT_KEYPAIR_NAME = 'yeet'

#setup logging to output to console
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

        r = self.manager.keypairs_client.create_keypair(name=DEFAULT_KEYPAIR_NAME)
        pk = r['keypair']['private_key']
        pubk = r['keypair']['public_key']
        LOG.info("Generated SSH keypair...")
        LOG.info("pub_key: %s",pubk)
        
        LOG.info('Creating server...')
        t1 = time.perf_counter()
        r = self.manager.servers_client.create_server(name=DEFAULT_SERVER_NAME, imageRef=CONF.compute.image_ref, flavorRef=CONF.compute.flavor_ref, key_name=DEFAULT_KEYPAIR_NAME, networks=[{'uuid': CONF.network.public_network_id}]);
        t2 = time.perf_counter()

        id = r['server']['id']

        LOG.info('server_name : %s server_id : %s',DEFAULT_SERVER_NAME,id)
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
            else:
                time.sleep(CONF.compute.ready_wait)
        LOG.info("Got server status ready")
        LOG.info('Time to complete (note: this time is affected by the polling period "ready_wait" configured in tempest (/etc/tempest.conf)): {:3.4f}s'.format(t2-t1))
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
            LOG.info('Waiting for floating ip to become active...')
            t1 = time.perf_counter()
            while True:
                r = self.manager.floating_ips_client.show_floatingip(fip_id)
                LOG.info("Polling...")
                LOG.info('STATUS: %s',r['floatingip']['status'])
                if r['floatingip']['status'] == "ACTIVE":
                    t2 = time.perf_counter()
                    break
                else:
                    time.sleep(CONF.compute.ready_wait)
            
            LOG.info("Got server status ready")
            LOG.info('Time to complete (note: this time is affected by the polling period "ready_wait" configured in tempest (/etc/tempest.conf)): {:3.4f}s'.format(t2-t1))
            LOG.info('---------------------------')

        #establish ssh connection
        LOG.info('Starting SSH connection ...')
        LOG.info('Using ip %s, username "%s"',ipv4, CONF.validation.image_ssh_user)
        #password is temporary measure for cirros issue, need to remove this when possible
        client = remote_client.RemoteClient(ipv4, CONF.validation.image_ssh_user, pkey=pk, password='gocubsgo',ssh_key_type='ecdsa')
        client.validate_authentication()
        LOG.info('SSH succeeded!')
        LOG.info('---------------------------')
        LOG.info('Test finished, cleaning up...')

        self.manager.servers_client.delete_server(id)
        LOG.info('Deleted server "%s"',DEFAULT_SERVER_NAME)
        self.manager.keypairs_client.delete_keypair('yeet')
        LOG.info('Deleted keypair "%s"',DEFAULT_KEYPAIR_NAME)
        