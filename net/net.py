import logging
import re
import sys

import netifaces
import yaml

PUB = 'PUB'
INN = 'INN'

logger = logging.getLogger(__name__)


class NetworkError(Exception):
    pass


class IPUnreachable(NetworkError):
    pass


def is_ip4(ip):

    if type(ip) not in (type(''), type(u'')):
        return False

    ip = ip.split('.')

    for s in ip:

        if not s.isdigit():
            return False

        i = int(s)
        if i < 0 or i > 255:
            return False

    return len(ip) == 4


def ip_class(ip):

    if ip.startswith('127.0.0.'):
        return INN

    intraPatterns = ['172\..*',
                     '10\..*',
                     '192\.168\..*',
                     ]

    for ptn in intraPatterns:

        if re.match(ptn, ip):
            return INN

    else:
        return PUB


def ips_prefer(ips, preference):

    eips = choose_pub(ips)
    iips = choose_inn(ips)

    if preference == PUB:
        return eips + iips
    else:
        return iips + eips


def is_pub(ip):
    return ip_class(ip) == PUB


def is_inn(ip):
    return ip_class(ip) == INN


def choose_pub(ips):
    return [x for x in ips if ip_class(x) == PUB]


def choose_inn(ips):
    return [x for x in ips if ip_class(x) == INN]


def get_host_ip4(iface_prefix=None):

    if iface_prefix is None:
        iface_prefix = ['']

    if type(iface_prefix) in (type(''), type(u'')):
        iface_prefix = [iface_prefix]

    ips = []

    for ifaceName in netifaces.interfaces():

        for t in iface_prefix:
            if ifaceName.startswith(t):
                matched = True
                break

        if not matched:
            continue

        ifo = netifaces.ifaddresses(ifaceName)

        if ifo.has_key(netifaces.AF_INET) and ifo.has_key(netifaces.AF_LINK):

            ip = ifo[netifaces.AF_INET][0]['addr']
            if ip != '127.0.0.1':
                ips += [ip]

    return ips


def choose_by_idc(dest_idc, local_idc, ips):

    if dest_idc == local_idc:
        pref_ips = ips_prefer(ips, INN)
    else:
        pref_ips = ips_prefer(ips, PUB)

    return pref_ips


def get_host_devices(iface_prefix=''):

    rst = {}

    names = netifaces.interfaces()
    names = [x for x in names if x.startswith(iface_prefix)]

    for name in names:

        ifo = netifaces.ifaddresses(name)

        if ifo.has_key(netifaces.AF_INET) and ifo.has_key(netifaces.AF_LINK):

            ip = ifo[netifaces.AF_INET][0]['addr']

            if ip == '127.0.0.1':
                continue

            rst[name] = {'INET': ifo[netifaces.AF_INET],
                         'LINK': ifo[netifaces.AF_LINK]}

    return rst


def parse_ip_regex_str(ip_regexs_str):

    ip_regexs_str = ip_regexs_str.strip()

    rst = ip_regexs_str.split(',')
    for r in rst:
        if r == '':
            raise ValueError('invalid regular expression: ' + repr(r))

    return rst


def choose_by_regex(ips, ip_regexs):

    rst = []

    for ip in ips:

        for ip_regex in ip_regexs:
            if re.match(ip_regex, ip):
                rst.append(ip)
                break

    return rst


if __name__ == "__main__":

    args = sys.argv[1:]

    if args[0] == 'ip':
        print yaml.dump(get_host_ip4(), default_flow_style=False)

    elif args[0] == 'device':
        print yaml.dump(get_host_devices(), default_flow_style=False)

    else:
        raise ValueError('invalid command line arguments', args)
