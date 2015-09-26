from __future__ import (absolute_import, print_function)
from boto3.session import Session
import datetime
from acli.output.cloudwatch import (output_ec2_cpu, output_ec2_net,
                                    output_asg_cpu, output_ec2_vols)
from acli.services.ec2 import ec2_get_instance_vols


def get_boto3_session(aws_config):
    return Session(region_name=aws_config.region,
                   aws_access_key_id=aws_config.access_key_id,
                   aws_secret_access_key=aws_config.secret_access_key)


def ec2_cpu(aws_config=None, instance_id=None, intervals=None, period=None,
            start=None, end=datetime.datetime.utcnow(), output_type=None):
    if not intervals:
        intervals = 60
    if not period:
        period = 7200
    session = get_boto3_session(aws_config)
    cloudwatch_client = session.client('cloudwatch')
    if not start:
        start = end - datetime.timedelta(seconds=period)
    out = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                 'Name': 'InstanceId',
                 'Value': instance_id
                }
            ],
            StartTime=start,
            EndTime=datetime.datetime.utcnow(),
            Period=intervals,
            Statistics=[
                'Average',
            ],
            Unit='Percent'
        )
    datapoints = out.get('Datapoints')
    sorted_datapoints = sorted(datapoints, key=lambda v: v.get('Timestamp'))
    dates = list()
    values = list()
    for datapoint in sorted_datapoints:
        dates.append(datapoint.get('Timestamp'))
        values.append(datapoint.get('Average'))
    output_ec2_cpu(dates=dates, values=values, instance_id=instance_id)
    exit(0)


def ec2_net(aws_config=None, instance_id=None, intervals=None, period=None,
            start=None, end=datetime.datetime.utcnow(), output_type=None):
    if not intervals:
        intervals = 60
    if not period:
        period = 7200
    session = get_boto3_session(aws_config)
    cloudwatch_client = session.client('cloudwatch')
    if not start:
        start = end - datetime.timedelta(seconds=period)
    net_in = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start,
            EndTime=datetime.datetime.utcnow(),
            Period=intervals,
            Statistics=['Average'],
            Unit='Bytes'
        )
    net_out = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkOut',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start,
            EndTime=datetime.datetime.utcnow(),
            Period=intervals,
            Statistics=['Average'],
            Unit='Bytes'
        )

    net_in_datapoints, net_out_datapoints = net_in.get('Datapoints'), net_out.get('Datapoints')
    if not all((net_in_datapoints, net_out_datapoints)):
        exit("Metrics unavailable.")
    sorted_net_in_datapoints = sorted(net_in_datapoints, key=lambda v: v.get('Timestamp'))
    sorted_net_out_datapoints = sorted(net_out_datapoints, key=lambda v: v.get('Timestamp'))
    in_dates = [x1.get('Timestamp') for x1 in sorted_net_in_datapoints]
    in_values = [x2.get('Average') for x2 in sorted_net_in_datapoints]
    out_dates = [x3.get('Timestamp') for x3 in sorted_net_out_datapoints]
    out_values = [x4.get('Average') for x4 in sorted_net_out_datapoints]
    output_ec2_net(in_dates=in_dates, in_values=in_values,
                   out_dates=out_dates, out_values=out_values,
                   instance_id=instance_id)
    exit(0)


def asg_cpu(aws_config=None, asg_name=None, intervals=None, period=None,
            start=None, end=datetime.datetime.utcnow(), output_type=None):
    if not output_type or output_type == 'graph':
        if not intervals:
            intervals = 60
        if not period:
            period = 7200
        session = get_boto3_session(aws_config)
        cloudwatch_client = session.client('cloudwatch')
        if not start:
            start = end - datetime.timedelta(seconds=period)
        out = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                     'Name': 'AutoScalingGroupName',
                     'Value': asg_name
                    }
                ],
                StartTime=start,
                EndTime=datetime.datetime.utcnow(),
                Period=intervals,
                Statistics=[
                    'Average',
                ],
                Unit='Percent'
            )
        datapoints = out.get('Datapoints')
        sorted_datapoints = sorted(datapoints, key=lambda v: v.get('Timestamp'))
        dates = [y1.get('Timestamp') for y1 in sorted_datapoints]
        values = [y2.get('Average') for y2 in sorted_datapoints]

        output_asg_cpu(dates=dates, values=values, asg_name=asg_name)
        exit(0)
    elif output_type == 'table':
        print("table")
        exit(0)


def ec2_vol(aws_config=None, instance_id=None, intervals=None, period=None,
            start=None, end=datetime.datetime.utcnow(), output_type=None):
    session = get_boto3_session(aws_config)
    ebs_vols = ec2_get_instance_vols(session=session, instance_id=instance_id)
    if not intervals:
        intervals = 60
    if not period:
        period = 7200

    cloudwatch_client = session.client('cloudwatch')
    if not start:
        start = end - datetime.timedelta(seconds=period)
    vol_datapoints = list()
    for ebs_vol in ebs_vols:
        read_ops = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EBS',
                MetricName='VolumeReadOps',
                Dimensions=[{'Name': 'VolumeId', 'Value': ebs_vol['Ebs']['VolumeId']}],
                StartTime=start,
                EndTime=datetime.datetime.utcnow(),
                Period=intervals,
                Statistics=['Average'],
                Unit='Count'
        )
        write_ops = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EBS',
                MetricName='VolumeWriteOps',
                Dimensions=[{'Name': 'VolumeId', 'Value': ebs_vol['Ebs']['VolumeId']}],
                StartTime=start,
                EndTime=datetime.datetime.utcnow(),
                Period=intervals,
                Statistics=['Average'],
                Unit='Count'
            )

        vol_datapoints.append({'device_name': ebs_vol['DeviceName'],
                               'read_datapoints': sorted(read_ops['Datapoints'], key=lambda v: v.get('Timestamp')),
                               'write_datapoints': sorted(write_ops['Datapoints'], key=lambda v: v.get('Timestamp')),
                               })

    #for vol_datapoint in vol_datapoints:
    #    print(vol_datapoint.get('device_name'))
    #   print(vol_datapoint.get('read_datapoints'))
    #    print(vol_datapoint.get('write_datapoints'))


    #net_in_datapoints, net_out_datapoints = net_in.get('Datapoints'), net_out.get('Datapoints')
    #if not all((net_in_datapoints, net_out_datapoints)):
    #    exit("Metrics unavailable.")
    #sorted_net_in_datapoints = sorted(net_in_datapoints, key=lambda v: v.get('Timestamp'))
    #sorted_net_out_datapoints = sorted(net_out_datapoints, key=lambda v: v.get('Timestamp'))
    #in_dates = [x1.get('Timestamp') for x1 in sorted_net_in_datapoints]
    #in_values = [x2.get('Average') for x2 in sorted_net_in_datapoints]
    #out_dates = [x3.get('Timestamp') for x3 in sorted_net_out_datapoints]
    #out_values = [x4.get('Average') for x4 in sorted_net_out_datapoints]
    #output_ec2_vols(in_dates=in_dates, in_values=in_values,
    #               out_dates=out_dates, out_values=out_values,
    #               instance_id=instance_id)
    output_ec2_vols(vols_datapoints=vol_datapoints, instance_id=instance_id)
