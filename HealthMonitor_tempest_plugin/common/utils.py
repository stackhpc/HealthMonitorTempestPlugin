import logging
import sys

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

    report += tabulate([[r[0],r[1],r[2],'{:3.4f}s'.format(r[3])] for r in runs],headers=['Image', 'Flavor','Success?','Time'],tablefmt='grid')
    report += '\n'
    if runs_alt:
        report += 'ALTERNATIVE RUNS \n'
        report += tabulate([[r[0],r[1],r[2],'{:3.4f}s'.format(r[3])] for r in runs_alt],headers=['Image', 'Flavor','Success?','Time'],tablefmt='grid')
    else:
        report += "No alternative runs performed"

    return report
