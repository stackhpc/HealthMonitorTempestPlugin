import logging
import sys
import os
import json

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
    

