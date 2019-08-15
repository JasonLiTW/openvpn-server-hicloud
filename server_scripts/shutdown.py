import os
import time
import json
import requests


if __name__ == '__main__':
    no_user_count_path = "/home/jason/logs/no-user-count.log"
    os.system('sudo systemctl stop openvpn@server')
    os.system("sudo rm -f {0}".format(no_user_count_path))
    time.sleep(5)  # waiting for OpenVPN disconnect script
    url = "https://api.server.com/stop"
    # headers = {'Content-Type': 'application/json'}
    # data = {"who": "server"}
    # res = requests.post(url=url, headers=headers, data=json.dumps(data))
    res = requests.get(url=url)
    if res.status_code != requests.codes.ok:
        # local shutdown.
        os.system('sudo shutdown -h now')
