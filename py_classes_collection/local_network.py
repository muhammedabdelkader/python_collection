"""Local Network operations """
import socket
import subprocess

__version__ = "0.1"


class local_network:
    def __init__(self):
        print("Class Called ")

    def get_wifi_profiles_passwords(self):
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
        for i in profiles:
            results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode(
                'utf-8').split('\n')
            results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
            try:
                print("{:<30}|  {:<}".format(i, results[0]))
            except IndexError:
                print("{:<30}|  {:<}".format(i, ""))

    def get_ip_address(self, hostname):
        return socket.gethostbyname(hostname)


R = local_network()
print(R.get_wifi_profiles_passwords())  # R.get_ip_address("google.com"))
