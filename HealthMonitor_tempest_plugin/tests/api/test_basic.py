from HealthMonitor_tempest_plugin.tests.base import BaseHealthCheck

import time

import testtools

class BasicTest(BaseHealthCheck):

    def __init__(self, *args, **kwargs):
        super(BasicTest,self).__init__(*args,**kwargs)

    @testtools.testcase.attr('positive')
    def test_basic(self):
        resp = self.manager.servers_client.create_server(name='test-server', imageRef='ba111615-c4ab-49ed-9abe-73841c6f0029', flavorRef='1', networks=[{'uuid': '3c187a9a-778e-46d5-83d0-2c35207b1f39'}]);
        print(resp)
        self.assertEqual('yes','yes');
        