# Copyright 2015
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.config import cfg

service_available_group = cfg.OptGroup(name="service_available",
                                       title="Available OpenStack Services")

ServiceAvailableGroup = [
    cfg.BoolOpt("nova",
                default=True,
                help="Whether nova is expected to be available"),
]

health_mon_group = cfg.OptGroup(name="healthmon",
                                title="Health Monitor Options")

HealthMonitorGroup =  [

    cfg.MultiStrOpt("flavor",
                help='A list of flavors compatible with the images provided'),
    cfg.MultiStrOpt("bm_flavor",
                help='A list of flavors compatible with the images provided'),
    #temp - move this somewhere better
    cfg.StrOpt("bm_net_id",
                help='A list of flavors compatible with the images provided'),

    cfg.MultiStrOpt("image",
                help='A list of images compatible with the flavors provided'),

    cfg.MultiStrOpt("flavor_alt",
                help='A list of flavors compatible with the alternative images provided'),

    cfg.MultiStrOpt("image_alt",
                help='A list of images compatible with the alternative flavors provided'),
    
    cfg.MultiStrOpt("ssh_user",
                help='corresponding ssh users for images - must be in order'),
    cfg.MultiStrOpt("ssh_user_alt",
                help='corresponding ssh users for images - must be in order')

]
