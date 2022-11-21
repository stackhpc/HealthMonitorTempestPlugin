from health_monitor_tempest_plugin.common.utils import gen_json_report,gen_runs_file

from tempest.scenario import manager

from tempest.lib import exceptions as lib_exc

from tempest.common import waiters

from tempest import exceptions

import sys

import testtools
import logging

import traceback

from tempest import config

import time
import datetime
CONF = config.CONF

import re 

#setup logging to output to console
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
handler.setFormatter(formatter)
LOG.addHandler(handler)

class BasicTest(manager.ScenarioTest):

    credentials=['primary']

    def setUp(self):
        super(BasicTest, self).setUp()
        gen_runs_file(CONF)

    
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
        LOG.info('trying to ssh')
        self.ssh_client = self.get_remote_client(
            ip_address=self.ip,
            username=self.ssh_user,
            private_key=keypair['private_key'],
            server=self.instance)

    def create_server_and_check_connectivity(self,f,i,ssh_user,network):
        success=True
        self.ssh_user = ssh_user

        details = ""
        try: 
            time_ssh = time.perf_counter()
            time_start = time.perf_counter()
            keypair = self.create_keypair()
            security_group = self.create_security_group()
            try:
                LOG.info('creating server')
                self.instance = self.create_server(image_id=i, flavor=f, key_name=keypair['name'],security_groups=[{'name':security_group['name']}],networks=[{'uuid': network}])
                time_start_end = time.perf_counter()
                LOG.info('server up')
                self.verify_ssh(keypair)
                time_ssh_end = time.perf_counter()
                self.servers_client.delete_server(self.instance['id'])
                try:
                    waiters.wait_for_server_termination(
                    self.servers_client, self.instance['id'], ignore_error=False)
                except lib_exc.DeleteErrorException as e:
                    LOG.warning("Failed to delete server : %s",str(e))
                    details += str(e)
                    success = False
                    time_ssh_end = time_ssh
                    time_start_end = time_start
            except lib_exc.SSHTimeout:
                LOG.error("Server SSH timed out")
                details += str(e)
                success = False
                time_ssh_end = time_ssh
                time_start_end = time_start
            except Exception as e: 
                LOG.error('Server build failed with message: %s',str(e))
                details += str(e)
                success = False
                time_ssh_end = time_ssh
                time_start_end = time_start
                print(traceback.format_exc())
        except Exception as e:
            LOG.error('Resource creation failed with message: %s',str(e))
            details += str(e)
            success = False
            time_ssh_end = time_ssh
            time_start_end = time_start
        
        return (self.compute_images_client.show_image(i)['image']['name'],
                self.flavors_client.show_flavor(f)['flavor']['name'],
                success,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),time_start_end-time_start,time_ssh_end-time_ssh, details)

    @testtools.testcase.attr('positive')
    def test_all_flavors_and_images(self):

        regex = re.compile(r'#\S+')

        runs = []

        LOG.info('im here')

        with open('tests') as f:
            with open('tests.pos','r+') as id_f:
                id_x = int(id_f.readline())
                total = 0
                for i,line in enumerate(f):
                    total += 1
                    if i == id_x:
                        data = json.loads(line)
                        runs.append(self.create_server_and_check_connectivity(data['flavor'],data['image'],data['ssh_user'],CONF.network.public_network_id))
                if id_x == total - 1:
                    with open('tests.pos','w') as id_fx:
                        id_fx.write(str(0))
                else:
                    with open('tests.pos','w') as id_fx:
                        id_fx.write(str(id_x+1))

        gen_json_report(runs)
        
        
