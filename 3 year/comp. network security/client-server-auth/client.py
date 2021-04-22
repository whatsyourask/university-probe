from auth import *
from socket import *
from crypto import get_hash
import sys


class AuthClient(Auth):
    """
    Provides client functionality
    Like interface to work with socket and auth module
    """
    def __init__(self, addr: str, port: int, bits_length: int) -> None:
        self.__addr = addr
        self.__port = port
        self.__bits_length = bits_length

    def connect(self) -> None:
        """Connect to a server"""
        # Create a socket object
        self.__socket = socket(AF_INET, SOCK_STREAM)
        # Check if it is a localhost
        is_localhost = self.__addr == ''
        if is_localhost:
            # if it is then convert '' to localhost address
            self.__addr = '127.0.0.1'
        print(f'Trying to connect to {self.__addr}:{self.__port}')
        # Connect to the server
        self.__socket.connect((self.__addr, self.__port))
        print('Connection established.')

    def authenticate(self, login: str, password: str) -> None:
        """Entire authentication"""
        # Begin a stage one
        continue_auth = self._auth_stage1()
        if continue_auth:
            # If it did okay, go to stage two
            print('[+] Server\'s public key received.')
            self.__login = login
            self.__password = password
            encrypted = self._auth_stage2()
        else:
            self.__socket.close()

    def _auth_stage1(self) -> bool:
        """Keys generation and obtaining the key from the server"""
        super()._generate_keys(self.__bits_length)
        self.__socket.send(str(self._pub_key).encode(self.ENCODING))
        server_pub_key = self.__socket.recv(1024).decode(self.ENCODING)
        print(server_pub_key)
        self.__server_pub_key = server_pub_key
        return super()._check_the_key(server_pub_key)

    def _auth_stage2(self) -> str:
        """Encrypt the login:password and send it"""
        hash = get_hash(self.__password)
        account = self.__login + ' ' + hash
        self.__server_pub_key = super()._get_key(self.__server_pub_key)
        encrypted = self.encrypt_twice(self.__server_pub_key, account)
        return encrypted


def main():
    try:
        port = int(sys.argv[1])
        bits_length = int(sys.argv[2])
        a_client = AuthClient('', port, bits_length)
        a_client.connect()
        a_client.authenticate('user', 'password')
    except ValueError:
        print('Usage: python3 client.py <port> <key bits length>')


if __name__=='__main__':
    main()