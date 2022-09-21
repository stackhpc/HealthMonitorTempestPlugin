from HealthMonitor_tempest_plugin.tests.base import BaseHealthCheck
from HealthMonitor_tempest_plugin.common.manager import Manager 
import testtools

class BasicTest(BaseHealthCheck):

    def __init__(self, *args, **kwargs):
        super(BasicTest,self).__init__(*args,**kwargs)

    @testtools.testcase.attr('positive')
    def test_basic(self):
        self.manager = Manager()
        print("I authenticated!")
        self.assertEqual('yes','yes');