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
    def test_basic(self):
        self.create_server_and_get_ssh(CONF.compute.image_ref,CONF.compute.flavor_ref)
        
        