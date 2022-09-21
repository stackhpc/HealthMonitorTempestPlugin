import time

from oslo_log import log as logging

import tempest.test
import logging
from tempest import config

CONF = config.CONF

class BaseHealthCheck(tempest.test.BaseTestCase):

    LOG = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(BaseHealthCheck, self).__init__(*args, **kwargs)

    @classmethod
    def skip_checks(cls):
        super(BaseHealthCheck,cls).skip_checks()

        if not CONF.service_available.nova:
            raise cls.skipException("Nova is not available, cannot perform Health Check")
