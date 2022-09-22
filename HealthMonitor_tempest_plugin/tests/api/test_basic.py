from HealthMonitor_tempest_plugin.tests.base import BaseHealthCheck

import time

import testtools

from tempest import config

CONF = config.CONF


class BasicTest(BaseHealthCheck):

    def __init__(self, *args, **kwargs):
        super(BasicTest,self).__init__(*args,**kwargs)

    @testtools.testcase.attr('positive')
    def test_basic(self):
        resp1 = self.manager.keypairs_client.create_keypair(name='yeet')
        pk = resp1['keypair']['private_key']
        pubk = resp1['keypair']['public_key']
        print("INFO: Generated SSH keypair...")
        print("INFO : pub_key:",pubk )

        server_create_time_b = time.perf_counter()
        resp = self.manager.servers_client.create_server(name='test-server', imageRef=CONF.compute.image_ref, flavorRef=CONF.compute.flavor_ref, key_name='yeet', networks=[{'uuid': CONF.network.public_network_id}]);
        server_create_time_a = time.perf_counter()

        #temp - DELETE
        self.manager.keypairs_client.delete_keypair('yeet')

        id = resp['server']['id']

        print('INFO: server_id :',id)
        print('---------------------------')
        #print(resp)
        print('INFO: Time to create server : {:3.4f}'.format(server_create_time_a-server_create_time_b))
        
        print('INFO: Waiting for server to become active...')

        while True:
            r = self.manager.servers_client.show_server(resp['server']['id'])
            print("INFO: Polling...")
            print('INFO : SERVER_STATUS',r['server']['status'])
            if r['server']['status'] == "ACTIVE":
                print(r)
                break
            else:
                time.sleep(CONF.compute.ready_wait)
            
        print("INFO : Got server status ready")
        print('---------------------------')
        
        print("INFO: Attempting to ssh into server...")
        if (CONF.network_feature_enabled.floating_ips and 
            CONF.network.floating_network_name):
            print("INFO: Getting ports for server with id: ",)

        #resp2 = self.manager.servers_client.delete_server(resp['server']['id'])

        
        self.manager.keypairs_client.delete_keypair('yeet')
        self.assertEqual('yes','yes');
        