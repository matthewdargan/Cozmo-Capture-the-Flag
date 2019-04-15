import socket
import errno
from socket import error as socket_error
from typing import List

def start_connection(ip, port) -> socket.socket:
    """
    Start a connection to a TCP network.

    :param: ip ip address of the network
    :param: port port number to forward messages over
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

    return s


def send_message(message: str, connection: socket.socket):
    """
    Send a message of a robot's cube's coordinates over the network.

    :param: message the message that needs to be sent
    :param: connection the network connection used to send data
    """

    connection.send(b'message', message)


def recieve_cube_message(message: str, connection: socket.socket) -> List[List[str]]:
    """
    Recieve a cube message from the network and parse it into sections so we can
    check the coordinates of a robot's cubes against a base.

    :param: message the message that needs to be parsed
    :param: connection the network connection used to recieve data
    :return: parameterized coordinate data
    """

    cont = True
    messages = []

    while cont:
        bytedata = connection.recv(4048)
        data = bytedata.decode('utf-8')

        if not data:
            print('No message to recieve')
            cont = False
        else:
            words = data.split(' ')
            messages.append(words)
    
    return messages
