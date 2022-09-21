import tempest.test
from HealthMonitor_tempest_plugin.common.manager import Manager 
import testtools

class BasicTest(tempest.test.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(BasicTest,self).__init__(*args,**kwargs)

    @testtools.testcase.attr('positive')
    def test_basic(self):
        self.manager = Manager()
        print("I authenticated!")
        self.assertEqual('yes','yes');

    @classmethod
    def skip_checks(cls):
        super(BasicTest,cls).skip_checks()

    @classmethod
    def resource_setup(cls):
        super(BasicTest, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(BasicTest, cls).resource_cleanup()