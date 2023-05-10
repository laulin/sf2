import unittest
import base64

from sf2.auth_sign import AuthSign

class TestAuthSign(unittest.TestCase):

    def test_dict_to_bytes(self):
        container = {
            "a" : b"b",
            "z" : "x",
            "c" : {
                "e" : b"f",
                "a" : b"d"
            }
        }
        auth_sign = AuthSign(container)
        result = auth_sign.dict_to_bytes(container)

        expected  = b"abcadefzx"

        self.assertEqual(result, expected)

    def test_dict_to_bytes(self):
        container = {
            "a" : b"b",
            "z" : "x",
            "c" : {
                "e" : b"f",
                "a" : b"d"
            }
        }
        auth_sign = AuthSign(container)
        result = auth_sign.sha256_dict(container)

        expected  = b"\x06@\xb1dD\xa51+N\x06\xf6\x1e5\x15(\xb0\x8e\x93N\xc9E\xc0\xaf\xc0\xec2>\xaaX!:\x15"

        self.assertEqual(result, expected)

    def test_sign_and_verify(self):
        MASTER_KEY = base64.urlsafe_b64encode(b"0123456789abcdef0123456789abcdef")

        container = {
            "auth":{
                "user":{
                    "ssh":{
                        "foo@bar":"test"
                    }
                },
                "stuff": b"xyz"
            }
        }

        auth_sign = AuthSign(container)
        auth_sign.add_keys(MASTER_KEY)
        auth_sign.sign(MASTER_KEY)
        auth_sign.verify()



