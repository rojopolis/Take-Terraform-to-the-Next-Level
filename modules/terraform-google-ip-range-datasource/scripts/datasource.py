'''
Generate IP Whitelist for published GCP ranges
https://cloud.google.com/compute/docs/faq#find_ip_range
'''

import json
import logging
import dns.resolver

logging.basicConfig(level='ERROR')

def get_netblock(record, cidrs):
    '''
    Recurse through netblocks and append CIDRS
    '''
    includes = []
    answers = dns.resolver.query(record, 'TXT')
    logging.debug(f'answers={answers}')
    for rdata in answers:
        logging.debug(f'rdata={rdata}')
        logging.debug(f'type={type(rdata)}')
        includes = [x.split('include:')[1] for x in str(rdata).split(' ') if x.startswith('include:')]
        cidrs.extend([x for x in str(rdata).split(' ') if x.startswith('ip')])
    logging.debug(f'includes={includes}')
    logging.debug(f'cidrs={cidrs}')
    for include in includes:
        get_netblock(include, cidrs)

def stringify_cidrs(cidr_list, ip_ver='4'):
    '''
    Terraform only supports strings for external data sources,
    so flatten lists inst space separated strings
    '''
    cidr_string = ''
    for cidr in [x.split(f'ip{ip_ver}:')[1] for x in cidrs if x.startswith(f'ip{ip_ver}')]:
        cidr_string += cidr + ' '
    return cidr_string

if __name__ == '__main__':
    cidrs = []
    get_netblock('_cloud-netblocks.googleusercontent.com', cidrs)
    print(json.dumps(
            {
                'ipv4Cidrs': stringify_cidrs(cidrs, '4'),
                'ipv6Cidrs': stringify_cidrs(cidrs, '6')
            }
        )
    )