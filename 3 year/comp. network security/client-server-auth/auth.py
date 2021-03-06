import sys
# To import FastModularExponentiation
sys.path.insert(0, '../../computer security/')
from rsa.backend import RSA, miller_rabin_generate
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from re import fullmatch
from typing import Tuple


class Auth:
    """Class to share common functionality"""
    FAILURE = b'Failed to log on.'
    SUCCESS = b'Successfully logged in.'
    def _generate_keys(self, bits_length: int) -> Tuple:
        p = miller_rabin_generate(bits_length)
        q = miller_rabin_generate(bits_length)
        n = p * q
        euler_func = (p - 1) * (q - 1)
        rsa = RSA()
        rsa.n = n
        rsa.euler_func = euler_func
        pub_key = (rsa.generate_public_key(bits_length), n)
        priv_key = (rsa.generate_private_key(), n)
        return rsa, pub_key, priv_key

    def get_hash(self, passwd: str) -> str:
        """Get a hash of the password"""
        # TODO: Fix the issue with the hash object
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(passwd.encode('utf-8'))
        hash = digest.finalize()
        return hash

    def generate_keys(self, bits_length: int) -> None:
        """Generate keys and save them"""
        rsa, pub_key, priv_key = self._generate_keys(bits_length)
        self._rsa = rsa
        self._pub_key = pub_key
        self._priv_key = priv_key

    def _get_key(self, key: str) -> Tuple:
        """Extract e and n from the format (e, n)"""
        splited_key = key.split(', ')
        extracted_key = (int(splited_key[0][1:]), int(splited_key[1][:-1]))
        return extracted_key

    def _check_the_key(self, key: str) -> bool:
        """Check the key that it's in proper format"""
        pattern = '\(\d*, \d*\)'
        valid = fullmatch(pattern, key)
        if not valid:
            return False
        return True

    def _encrypt(self, data: str, key: Tuple=None) -> str:
        """Encrypt one time, if the key is specified, then set it to rsa obj"""
        if key:
            self._rsa.e = key[0]
            self._rsa.n = key[1]
        return self._rsa.encrypt(data)

    def encrypt_twice(self, key: Tuple, data: str) -> str:
        """Encrypt twice
        First: with your private key
        Second: with public key of another side
        """
        self._rsa.e = self._priv_key[0]
        self._rsa.n = self._priv_key[1]
        encrypted_once = self._encrypt(data).split()
        encrypted_twice = self._encrypt(encrypted_once, key)
        # print('data: ', data)
        # print()
        # print('e, n', self._priv_key[0], self._priv_key[1])
        # print('encrypted_once: ', encrypted_once)
        # print()
        # print('e, n', self._rsa.e, self._rsa.n)
        # print('encrypted_twice: ', encrypted_twice)
        # print()
        return encrypted_twice

    def _decrypt(self, data: str, key: Tuple=None) -> str:
        """Decrypt one time, if the key is specified, then set it to rsa obj"""
        if key:
            self._rsa.d = key[0]
            self._rsa.n = key[1]
        return self._rsa.decrypt(data)

    def decrypt_twice(self, key: Tuple, data: str) -> str:
        """Decrypt twice as with encrypt"""
        self._rsa.d = self._priv_key[0]
        self._rsa.n = self._priv_key[1]
        decrypted_once = self._decrypt(data.split())
        decrypted_twice = self._decrypt(decrypted_once.split(), key)
        decrypted_twice = b''.join(list(map(lambda num: chr(int(num) % self._rsa.LAST_ORD).encode(), decrypted_twice.split())))
        # print('data: ', data)
        # print()
        # print('d, n', self._priv_key[0], self._priv_key[1])
        # print('decrypted_once: ', decrypted_once)
        # print()
        # print('d, n', self._rsa.d, self._rsa.n)
        # print('decrypted_twice: ', decrypted_twice)
        # print()
        return decrypted_twice
