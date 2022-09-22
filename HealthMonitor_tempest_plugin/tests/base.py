import tempest.test
import logging
from tempest import config

import ipaddress

from HealthMonitor_tempest_plugin.common.manager import Manager 

CONF = config.CONF
LOG = logging.getLogger(__name__)

class BaseHealthCheck(tempest.test.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(BaseHealthCheck, self).__init__(*args, **kwargs)
        self.manager = Manager()

    @classmethod
    def skip_checks(cls):
        super(BaseHealthCheck,cls).skip_checks()

        if not CONF.service_available.nova:
            raise cls.skipException("Nova is not available, cannot perform Health Check")

    @classmethod
    def resource_setup(cls):
        super(BaseHealthCheck, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(BaseHealthCheck, cls).resource_cleanup()

    def get_port(self, id):
        ports = self.manager.ports_client.list_ports(device_id=id)['ports']

        def _is_active(port):
            return (port['status'] == 'ACTIVE' or
                port.get('binding:vnic_type') == 'baremetal')

        try:
            port_map = [(p["id"], fxip["ip_address"])
                    for p in ports
                    for fxip in p["fixed_ips"]
                    if (ipaddress.ip_address(fxip["ip_address"]) and
                        _is_active(p))]
        except:
            LOG.warning('INVALID IP FOUND IN CONFIG')

        inactive = [p for p in ports if p['status'] != 'ACTIVE']

        if inactive:
            LOG.warning("Instance has ports that are not ACTIVE: %s", inactive)

        self.assertNotEmpty(port_map,
                            "No IPv4 addresses found in: %s" % ports)
        self.assertEqual(len(port_map), 1,
                        "Found multiple IPv4 addresses: %s. "
                        "Unable to determine which port to target."
                        % port_map)

        return port_map[0]