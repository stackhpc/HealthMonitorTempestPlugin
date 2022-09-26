from math import frexp
from re import S
from termios import TAB2
from HealthMonitor_tempest_plugin.tests.base import BaseHealthCheck
from HealthMonitor_tempest_plugin.common.utils import gen_report

import sys

import testtools
import logging

from tempest import config

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


class BasicTest(BaseHealthCheck):

    def __init__(self, *args, **kwargs):
        super(BasicTest,self).__init__(*args,**kwargs)

    @testtools.testcase.attr('positive')
    def test_all_flavors_and_images(self):

        regex = re.compile(r'#\S+')

        runs = []
        runs_alt = []

        if(CONF.healthmon.flavors and CONF.healthmon.images and CONF.healthmon.ssh_users):
            for f in [f for f in list(filter(None,CONF.healthmon.flavors.split('\n'))) if not regex.match(f)]:

                for i,ssh_user in zip([i for i in list(filter(None,CONF.healthmon.images.split('\n'))) if not regex.match(i)],
                                      [s for s in list(filter(None,CONF.healthmon.ssh_users.split('\n'))) if not regex.match(s)]):

                    success,time = self.create_server_and_get_ssh(ssh_user,i,f)
                    runs.append((i,f,success,time))
        if(CONF.healthmon.flavors_alt and CONF.healthmon.images_alt):
            for f in list(filter(None,CONF.healthmon.flavors_alt.split('\n'))):

                for i,ssh_user in zip(list(filter(None,CONF.healthmon.images_alt.split('\n'))),
                                      list(filter(None,CONF.healthmon.ssh_users_alt.split('\n')))):

                    success,time = self.create_server_and_get_ssh(ssh_user,i,f)
                    runs_alt.append((i,f,success,time))
        
        LOG.info(gen_report(runs,runs_alt))
        
        