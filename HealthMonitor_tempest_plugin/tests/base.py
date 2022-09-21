import tempest.test
import logging
from tempest import config

from HealthMonitor_tempest_plugin.common.manager import Manager 

CONF = config.CONF

class BaseHealthCheck(tempest.test.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(BaseHealthCheck, self).__init__(*args, **kwargs)
        self.manager = Manager()
        self.LOG = logging.getLogger(__name__)

    @classmethod
    def skip_checks(cls):
        super(BaseHealthCheck,cls).skip_checks()

        if not CONF.service_available.nova:
            raise cls.skipException("Nova is not available, cannot perform Health Check")
        else:
            print('yaaa is good bro')

    @classmethod
    def resource_setup(cls):
        super(BaseHealthCheck, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(BaseHealthCheck, cls).resource_cleanup()
