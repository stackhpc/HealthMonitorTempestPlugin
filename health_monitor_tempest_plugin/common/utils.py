import logging
import sys
import os
import json

from os.path import exists

#from tabulate import tabulate

LOG_FILE = os.environ.get('LOG_FILE', './healthmon.log')

#setup logging to output to console
LOG = logging.getLogger(__name__)

"""
def gen_report(runs,runs_alt):

    report="\n"

    report += tabulate([[r[0],r[1],r[2],'{:3.4f}s'.format(r[3])] for r in runs],headers=['Image', 'Flavor','Success?','Time'],tablefmt='grid')
    report += '\n'
    if runs_alt:
        report += 'ALTERNATIVE RUNS \n'
        report += tabulate([[r[0],r[1],r[2],'{:3.4f}s'.format(r[3])] for r in runs_alt],headers=['Image', 'Flavor','Success?','Time'],tablefmt='grid')
    else:
        report += "No alternative runs performed"

    return report
           runs.append((self.compute_images_client.show_image(i)['image']['name'],
                                 self.flavors_client.show_flavor(f)['flavor']['name'],
                                 success,time2-time1, details))
"""

def gen_runs_file(CONF):
    with open('tests', 'w+') as file:
        if(CONF.healthmon.image and CONF.healthmon.ssh_user):     
            if(CONF.healthmon.flavor):       
                for i,ssh_user in zip(CONF.healthmon.image,CONF.healthmon.ssh_user):
                    for f in CONF.healthmon.flavor:
                        data = {}
                        data['image'] = i
                        data['ssh_user'] = ssh_user
                        data['flavor'] = f
                        json.dump(data, file, ensure_ascii=False)


        if(CONF.healthmon.flavor_alt and CONF.healthmon.image_alt and CONF.healthmon.ssh_user_alt):            
            for i,ssh_user in zip(CONF.healthmon.image_alt,CONF.healthmon.ssh_user_alt):
                if(CONF.healthmon.flavor_alt):
                    for f in CONF.healthmon.flavor_alt:
                        data = {}
                        data['image'] = i
                        data['ssh_user'] = ssh_user
                        data['flavor'] = f
                        json.dumps(data, f, ensure_ascii=False, indent=4)

    if not exists('tests.pos'):
        with open('tests.pos', 'w+') as f:
            f.write(str(0))

def gen_json_report(runs):
    
    report = []

    for i,r in enumerate(runs):
        run = {}
        run['image'] = r[0]
        run['flavor'] = r[1]
        run['success'] = r[2]
        run['time'] = r[3]
        run['time_to_start'] = r[4]
        run['time_to_ssh'] = r[5]
        run['error'] = r[6]
        report.append(run)

    
    with open(LOG_FILE,'a') as f:
        for r in report: 
            f.write(json.dumps(r))
            f.write('\n')
    

