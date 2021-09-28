import colorama
import qrcode
import os
import subprocess
import datetime
from shutil import which
import sys

__version__ = "0.1"


class utils:
    def __init__(self):
        print("utils ..... ")
        #self.__wifi__payload="WIFI:T:WPA;S:{ssid};P:{password};;"


    def run_os_command(self, command=None):
        """
        Runs a given command using subprocess module
        """
        print(command)
        if command:
            env = os.environ.copy()
            env["LANG"] = "C"
            output, _ = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True,
                                     env=env).communicate()
            return output.decode("utf-8").rstrip("\r\n")
        else:
            raise ValueError("Command can not be empty")

    def generate_QR_code(self, qr_link_handler=None,show_qr=False):
        text = "https://github.com/muhammedabdelkader"
        if qr_link_handler:
            text = qr_link_handler
        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_L,
                           box_size=10,
                           border=4)
        qr.add_data(text)
        file_name = f"{datetime.datetime.today().time().microsecond}_qr_code_{text.split(':')[0]}.png"
        try:
            img = qr.make_image()
            img.save(file_name)
            if show_qr:
                self.run_os_command(command=f"open {file_name}")
        except FileNotFoundError:
            raise ValueError(f"No such file/directory: '{file_name}'")
        return f"QR code has been saved to {file_name}"




