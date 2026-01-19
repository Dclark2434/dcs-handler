import socket
import logging

BIOS_IP = '127.0.0.1'
BIOS_PORT = 7778

class DcsBiosSender:
    def __init__(self, ip=BIOS_IP, port=BIOS_PORT):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.info(f"DCS-BIOS Sender initialized on {self.ip}:{self.port}")

    def send_command(self, command_string):
        """
        Sends a command string to DCS-BIOS.
        Appends a newline if not present.
        """
        if not command_string.endswith('\n'):
            command_string += '\n'
        
        try:
            self.sock.sendto(command_string.encode('utf-8'), (self.ip, self.port))
            logging.debug(f"Sent to DCS-BIOS: {command_string.strip()}")
        except Exception as e:
            logging.error(f"Error sending to DCS-BIOS: {e}")

    def close(self):
        self.sock.close()
