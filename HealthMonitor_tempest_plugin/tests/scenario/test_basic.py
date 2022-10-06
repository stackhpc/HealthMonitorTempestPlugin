from HealthMonitor_tempest_plugin.common.utils import gen_report,gen_json_report

from tempest.scenario import manager

from tempest.lib import exceptions as lib_exc

from tempest.common import waiters

from tempest import exceptions

import sys

import testtools
import logging

from tempest import config

import time
CONF = config.CONF

import re 

#setup logging to output to console
LOG = logging.getLogger(__name__)


class BasicTest(manager.ScenarioTest):

    credentials=['primary']

    def setUp(self):
        super(BasicTest, self).setUp()
    
    @classmethod
    def skip_checks(cls):
        super(BasicTest,cls).skip_checks()

    def verify_ssh(self, keypair):
        # Obtain a floating IP if floating_ips is enabled
        if (CONF.network_feature_enabled.floating_ips and
            CONF.network.floating_network_name):
            fip = self.create_floating_ip(self.instance, external_network_id=CONF.network.floating_network_name)
            self.ip = self.associate_floating_ip(
                fip, self.instance)['floating_ip_address']
        else:
            server = self.servers_client.show_server(
                self.instance['id'])['server']
            self.ip = self.get_server_ip(server)
        # Check ssh
        self.ssh_client = self.get_remote_client(
            ip_address=self.ip,
            username=self.ssh_user,
            private_key=keypair['private_key'],
            server=self.instance)


    @testtools.testcase.attr('positive')
    def test_all_flavors_and_images(self):

        regex = re.compile(r'#\S+')

        runs = []
        runs_alt = []

        if(CONF.healthmon.flavors and CONF.healthmon.images and CONF.healthmon.ssh_users):
            for f in [f for f in list(filter(None,CONF.healthmon.flavors.split('\n'))) if not regex.match(f)]:

                for i,ssh_user in zip([i for i in list(filter(None,CONF.healthmon.images.split('\n'))) if not regex.match(i)],
                                      [s for s in list(filter(None,CONF.healthmon.ssh_users.split('\n'))) if not regex.match(s)]):

                    success=True
                    time1 = time.perf_counter()
                    keypair = self.create_keypair()
                    security_group = self.create_security_group()
                    self.ssh_user = ssh_user
                    details = ""

                    try:
                        self.instance = self.create_server(image_id=i, flavor=f, key_name=keypair['name'],security_groups=[{'name':security_group['name']}],networks=[{'uuid': CONF.network.public_network_id}])
                        self.verify_ssh(keypair)
                        time2 = time.perf_counter()
                        self.servers_client.delete_server(self.instance['id'])
                        try:
                            waiters.wait_for_server_termination(
                            self.servers_client, self.instance['id'], ignore_error=False)
                        except lib_exc.DeleteErrorException as e:
                            LOG.warning("Failed to delete server : %s",str(e))
                            details += str(e)
                            success = False
                    except exceptions.BuildErrorException as e: 
                        LOG.error('Server build failed with message: %s',str(e))
                        details += str(e)
                        success = False
                        time2 = time1

                    

                    runs.append((self.compute_images_client.show_image(i)['image']['name'],
                                 self.flavors_client.show_flavor(f)['flavor']['name'],
                                 success,time2-time1, details))
                    
        if(CONF.healthmon.flavors_alt and CONF.healthmon.images_alt):
            for f in list(filter(None,CONF.healthmon.flavors_alt.split('\n'))):

                for i,ssh_user in zip(list(filter(None,CONF.healthmon.images_alt.split('\n'))),
                                      list(filter(None,CONF.healthmon.ssh_users_alt.split('\n')))):

                    pass
        
        gen_json_report(runs,runs_alt)
        
        