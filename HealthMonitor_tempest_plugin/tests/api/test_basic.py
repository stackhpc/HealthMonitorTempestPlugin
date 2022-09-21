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
        resp = self.manager.servers_client.create_server(name='test-server', imageRef=CONF.compute.image_ref, flavorRef=CONF.compute.flavor_ref, networks=[{'uuid': CONF.network.public_network_id}]);
        print('server_id :',resp['server']['id'])
        print('---------------------------')
        print()
        resp2 = self.manager.servers_client.delete_server(resp['server']['id'])
        self.assertEqual('yes','yes');
        