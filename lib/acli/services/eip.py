# -*- coding: utf-8 -*-
from __future__ import (absolute_import, print_function, unicode_literals)
from acli.output.eip import (output_eip_list, output_eip_info)
from acli.connections import get_client
from botocore.exceptions import ClientError


def eip_list(aws_config=None):
    """
    @type aws_config: Config
    """
    ec2_client = get_client(client_type='ec2', config=aws_config)
    addresses_response = ec2_client.describe_addresses()
    addresses = addresses_response.get('Addresses', None)
    if len(list(addresses)):
        output_eip_list(output_media='console', addresses=addresses)
    exit('No elastic IPs found.')


def eip_info(aws_config=None, eip=None):
    """
    @type aws_config: Config
    """
    ec2_client = get_client(client_type='ec2', config=aws_config)
    try:
        addresses_response = ec2_client.describe_addresses(PublicIps=[eip])
        address = addresses_response.get('Addresses', None)[0]
        if len(list(address)):
            output_eip_info(output_media='console', address=address)
    except ClientError:
        exit('EIP {0} not found.'.format(eip))