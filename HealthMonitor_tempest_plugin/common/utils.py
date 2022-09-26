import logging
import sys

from HealthMonitor_tempest_plugin.common.manager import Manager 

from tabulate import tabulate

#setup logging to output to console
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
handler.setFormatter(formatter)
LOG.addHandler(handler)

def gen_report(runs,runs_alt):

    report="\n"


    images = [get_image(i[0]) for i in runs]
    flavors = [get_flavor(i[1]) for i in runs]
    successes = [i[2] for i in runs]

    report += tabulate([[get_image(r[0]),get_flavor(r[1]),r[2],'{:3.4f}s'.format(r[3])] for r in runs],headers=['Image', 'Flavor','Success?','Time'],tablefmt='grid')
    report += '\n'
    if runs_alt:
        report += 'ALTERNATIVE RUNS \n'
        report += tabulate([[get_image(r[0]),get_flavor(r[1]),r[2],'{:3.4f}s'.format(r[3])] for r in runs_alt],headers=['Image', 'Flavor','Success?','Time'],tablefmt='grid')
    else:
        report += "No alternative runs performed"

    return report

def get_image(id):
    manager = Manager()
    return manager.image_client_v2.show_image(id)['name']

def get_flavor(id):
    manager = Manager()
    return manager.flavors_client.show_flavor(id)['flavor']['name']
