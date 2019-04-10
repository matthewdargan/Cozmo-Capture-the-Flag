import socket
import errno
from socket import error as socket_error

def start_connection():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket_error as msg:
        print("Connection failed.")

    # set ip address and port of the network here
    ip = "10.0.1.10"
    port = 5000
    
    try:
        s.connect((ip, port))
    except socket_error as msg:
        robot.say_text("socket failed to bind").wait_for_completed()

    return s

def recieve_message(message: str, connection: socket.socket):
    cont = True

    while cont:
        bytedata = connection.recv(4048)
        data = bytedata.decode('utf-8')
        
        if not data:
            cont = False
            s.close()
            quit()
        else: