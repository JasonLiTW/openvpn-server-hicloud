import os
import sys

#  (root's) crontab  * * * * * python3 check.py

if __name__ == '__main__':
    openvpn_status_path = "/etc/openvpn/openvpn-status.log"
    no_user_count_path = "/home/jason/logs/no-user-count.log"
    shutdown_script_path = "/home/jason/scripts/shutdown.py"
    stop_server_after_minutes = 45

    with open(openvpn_status_path, 'r') as f:
        lines = f.readlines()
    lines = [line.rstrip('\n') for line in lines]

    if len(lines) < 3:
        sys.exit(0)

    end_line = -1
    found = False
    for line in lines:
        end_line += 1
        if line == "ROUTING TABLE":
            found = True
            break

    if not found:
        sys.exit(0)

    not_rdp_count = 0
    for i in range(3, end_line):
        if "rdp" not in lines[i]:
            not_rdp_count += 1

    value = 0
    if not_rdp_count == 0:
        os.system("sudo touch {0}".format(no_user_count_path))
        with open(no_user_count_path, 'r') as f:
            try:
                value = int(f.readline().rstrip('\n'))
            except ValueError:
                value = 0
        value += 1
    shutdown = False

    if value >= stop_server_after_minutes:
        shutdown = True
        value = 0

    with open(no_user_count_path, 'w') as f:
        f.write(str(value))

    if shutdown:
        os.system("sudo python3 {0}".format(shutdown_script_path))
