from __future__ import (absolute_import, print_function)
from acli.output import output_ascii_table
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def output_ec2_stats(output_media=None, instance=None, cpu_stats=None, network_stats=None):
    if output_media == 'console':
        td = list()
        td.append(['id', instance.id])
        td.append(['name', instance.tags.get('Name', '-')])
        td.append(['cpu 15mins / 30mins / 1hour',
                   "{0} / {1} / {2}".format(cpu_stats.get('fifteen_mins'),
                                            cpu_stats.get('thirty_mins'),
                                            cpu_stats.get('one_hour'))])
        td.append(['network in 1hr / 6hrs / 12hrs',
                   "{0} / {1} / {2}".format(network_stats.get('one_hour_in'),
                                            network_stats.get('six_hours_in'),
                                            network_stats.get('twelve_hours_in'))]),
        td.append(['network out 1hr / 6hrs / 12hrs',
                   "{0} / {1} / {2}".format(network_stats.get('one_hour_out'),
                                            network_stats.get('six_hours_out'),
                                            network_stats.get('twelve_hours_out'))])
        output_ascii_table(table_title="EC2 Stats",
                           table_data=td)
    exit(0)


def output_ec2_cpu(dates=None, values=None, instance_id=None, output_type='table'):
    print(output_type)
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax = plt.gca()
    xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(dates, values)
    plt.gcf().autofmt_xdate()
    plt.title('CPU statistics for: {0}'.format(instance_id))
    plt.xlabel('Time (UTC)')
    plt.ylabel('CPU %')
    plt.grid(True)
    plt.show()
    exit(0)


def output_ec2_net(in_dates=None, in_values=None, out_dates=None,
                   out_values=None, instance_id=None, output_type=None):
    if not output_type or output_type == 'graph':
        plt.subplots_adjust(bottom=0.2)
        plt.xticks(rotation=25)
        ax = plt.gca()
        xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        in_line = plt.plot(in_dates, in_values)
        out_line = plt.plot(out_dates, out_values)
        plt.setp(in_line, color='g', linewidth=2.0, label='inbound')
        plt.setp(out_line, color='b', linewidth=2.0, label='outbound')
        plt.gcf().autofmt_xdate()
        plt.title('Network statistics for: {0}'.format(instance_id))
        plt.xlabel('Time (UTC)')
        plt.ylabel('Network (Bytes/s)')
        plt.grid(True)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        plt.show()
        exit(0)


def output_asg_cpu(dates=None, values=None,
                   asg_name=None, output_type=None):
    if not output_type or output_type == 'graph':
        plt.subplots_adjust(bottom=0.2)
        plt.xticks(rotation=25)
        ax = plt.gca()
        xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        plt.plot(dates, values)
        plt.gcf().autofmt_xdate()
        plt.title('CPU statistics for: {0}'.format(asg_name))
        plt.xlabel('Time (UTC)')
        plt.ylabel('CPU %')
        plt.grid(True)
        plt.show()
        exit(0)
