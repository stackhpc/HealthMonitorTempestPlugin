import tempest.test
from HealthMonitor_tempest_plugin.common.manager import Manager 

class BasicTest(tempest.test.BaseTestCase):

    def __init__(self):
        super().__init__()
        self.manager = Manager()
        print("I authenticated!")
        exit()

    def skip_checks(self):
        super().skip_checks()