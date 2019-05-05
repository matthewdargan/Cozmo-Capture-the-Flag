import socket
from socket import error as socket_error
from typing import List


def start_connection(ip: str, port: int) -> socket.socket:
    """
    Start a connection to a TCP network.

    :param ip ip address of the network
    :param port port number to forward messages over
    :return: socket opened with the ip address and port number
    """

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket_error:
        print("Connection failed.")

    try:
        s.connect((ip, port))
    except socket_error:
        print('Socket failed to bind')

    s.setblocking(False)
    return s


def receive_message(connection: socket.socket) -> List[str]:
    """
    Receive a cube message from the network and parse it into sections so we can
    check the coordinates of a robot's cubes against a base.

    :param connection the network connection used to receive data
    :return: parameterized coordinate data
    """

    try:
        bytedata = connection.recv(4048)
        data = bytedata.decode('utf-8')

        if not data:
            print('No message to receive')
        else:
            return data.split(' ')
    except socket.error:
        return []
