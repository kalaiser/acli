from __future__ import (absolute_import, print_function, unicode_literals)
from acli.services.asg import (asg_list, lc_list)
from acli.config import Config
from moto import mock_ec2, mock_autoscaling

import pytest
from boto3.session import Session
session = Session(region_name="eu-west-1")


@pytest.yield_fixture(scope='function')
def fake_lc():
    """ASG mock service"""
    mock = mock_autoscaling()
    mock.start()
    client = session.client('autoscaling')
    client.create_launch_configuration(
        LaunchConfigurationName='test_lc',
        ImageId='ami-abcd1234',
        InstanceType='t2.medium'
    )
    yield client.describe_launch_configurations()
    mock.stop()


@mock_autoscaling
@pytest.yield_fixture(scope='function')
def test_create_autoscaling_group():
    conn = session.client('autoscaling')

    conn.create_launch_configuration(LaunchConfigurationName='test_lc',
                                     ImageId='ami-abcd1234',
                                     InstanceType='t2.medium')


@pytest.yield_fixture(scope='function')
def fake_asg():
    """ASG mock service"""
    mock = mock_autoscaling()
    mock.start()
    client = session.client('autoscaling')
    client.create_launch_configuration(
        LaunchConfigurationName='test_lc',
        ImageId='ami-abcd1234',
        InstanceType='t2.medium'
    )

    client.create_auto_scaling_group(
        AutoScalingGroupName='test_asg',
        LaunchConfigurationName='test_lc',
        InstanceId='string',
        MinSize=123,
        MaxSize=123,
        DesiredCapacity=123,
        DefaultCooldown=123,
        AvailabilityZones=[
            'string',
        ],
        LoadBalancerNames=[
            'string',
        ],
        HealthCheckType='string',
        HealthCheckGracePeriod=123,
        PlacementGroup='string',
        VPCZoneIdentifier='string',
        TerminationPolicies=[
            'string',
        ],
        Tags=[
            {
                'ResourceId': 'string',
                'ResourceType': 'string',
                'Key': 'string',
                'Value': 'string',
                'PropagateAtLaunch': True
            },
        ]
    )
    yield client.describe_auto_scaling_groups()
    mock.stop()


config = Config(cli_args={'--region': 'eu-west-1',
                          '--access_key_id': 'AKIAIOSFODNN7EXAMPLE',
                          '--secret_access_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'})


def test_lc_list_service(fake_lc):
    with pytest.raises(SystemExit):
        lc_list(aws_config=config)
        assert 0
        assert lc_list(aws_config=config)


def test_lc_list_asgs(fake_asg):
    with pytest.raises(SystemExit):
        assert asg_list(aws_config=config)
