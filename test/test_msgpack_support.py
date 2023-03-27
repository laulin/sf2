import unittest
from pprint import pprint
import os
from contextlib import suppress

from sf2.msgpack_support import MsgpackSupport


WORKING_FILE = "/tmp/test.x"
class TestJsonSupport(unittest.TestCase):

   
    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)


    def test_write_and_read(self):
        c = MsgpackSupport(WORKING_FILE)

        container = {
            "x" : 1,
            "y" : b"bytes",
            "z" : {
                "a": "a",
                "b" : ["b", b"b"]
            }
        }

        c.dump(container)
        result = c.load()

        self.assertDictEqual(result, container)