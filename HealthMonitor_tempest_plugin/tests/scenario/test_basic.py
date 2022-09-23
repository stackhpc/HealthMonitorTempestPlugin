from math import frexp
from re import S
from termios import TAB2
from HealthMonitor_tempest_plugin.tests.base import BaseHealthCheck

import sys

import testtools
import logging

from tempest import config

CONF = config.CONF


class BasicTest(BaseHealthCheck):

    def __init__(self, *args, **kwargs):
        super(BasicTest,self).__init__(*args,**kwargs)

    @testtools.testcase.attr('positive')
    def test_all_flavors_and_images(self):

        if(CONF.healthmon.flavors and CONF.healthmon.images and CONF.healthmon.ssh_users):

            for f in list(filter(None,CONF.healthmon.flavors.split('\n'))):
                for i,ssh_user in zip(list(filter(None,CONF.healthmon.images.split('\n'))),
                                      list(filter(None,CONF.healthmon.ssh_users.split('\n')))):
                    self.create_server_and_get_ssh(ssh_user,i,f)
        if(CONF.healthmon.flavors_alt and CONF.healthmon.images_alt):
            for f in CONF.healthmon.flavors_alt.split('\n'):
                for i in CONF.healthmon.images_alt.split('\n'):
                    self.create_server_and_get_ssh(i,f)
        
        