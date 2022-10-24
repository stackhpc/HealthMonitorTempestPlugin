from health_monitor_tempest_plugin.common.utils import gen_json_report

from tempest.scenario import manager

from tempest.lib import exceptions as lib_exc

from tempest.common import waiters

from tempest import exceptions

import sys

import testtools
import logging

from tempest import config

import time
import datetime
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

    def create_server_and_check_connectivity(self,f,i,ssh_user):
        success=True
        time1 = time.perf_counter()
        self.ssh_user = ssh_user
        details = ""
        try: 
            keypair = self.create_keypair()
            security_group = self.create_security_group()
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
                    time2 = time1
            except Exception as e: 
                LOG.error('Server build failed with message: %s',str(e))
                details += str(e)
                success = False
                time2 = time1
        except Exception as e:
            LOG.error('Resource creation failed with message: %s',str(e))
            details += str(e)
            success = False
            time2 = time1
        
        return (self.compute_images_client.show_image(i)['image']['name'],
                self.flavors_client.show_flavor(f)['flavor']['name'],
                success,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),time2-time1, details)

    @testtools.testcase.attr('positive')
    def test_all_flavors_and_images(self):

        regex = re.compile(r'#\S+')

        runs = []

        if(CONF.healthmon.flavor and CONF.healthmon.image and CONF.healthmon.ssh_user):
            for f in CONF.healthmon.flavor:
                for i,ssh_user in zip(CONF.healthmon.image,CONF.healthmon.ssh_user):
                    runs.append(self.create_server_and_check_connectivity(f,i,ssh_user))
                    
        if(CONF.healthmon.flavor_alt and CONF.healthmon.image_alt and CONF.healthmon.ssh_user_alt):
            for f in CONF.healthmon.flavor_alt:
                for i,ssh_user in zip(CONF.healthmon.image_alt,CONF.healthmon.ssh_user_alt):
                    runs.append(self.create_server_and_check_connectivity(f,i,ssh_user))
        
        gen_json_report(runs)
        
        
