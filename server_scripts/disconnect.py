#!/usr/bin/env python3
import datetime
import os

if __name__ == '__main__':
    client_name = os.environ.get('common_name', "n/a")
    client_ip = os.environ.get('ifconfig_pool_remote_ip', "n/a")
    byte_in = os.environ.get('bytes_received', "n/a")
    byte_out = os.environ.get('bytes_sent', "n/a")
    flow_log_path = "/home/jason/logs/flow.log"

    with open(flow_log_path, "a") as f:
        f.write("{}=={:^13}=={:^10}=={:^12}=={:^12}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                              client_name, client_ip, byte_in, byte_out))
