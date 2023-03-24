import unittest
from pprint import pprint
import os
from contextlib import suppress

from sf2.json_support import JsonSupport


WORKING_FILE = "/tmp/test.x"
class TestJsonSupport(unittest.TestCase):

   
    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)


    def test_encode(self):
        js = JsonSupport(WORKING_FILE)

        container = {
            "x" : 1,
            "y" : b"bytes",
            "z" : {
                "a": "a",
                "b" : ["b", b"b"]
            }
        }

        result = js.encode(container)
        expected = {'x': 1, 'y': 'Ynl0ZXM=', 'z': {'a': 'a', 'b': ['b', 'Yg==']}}

        self.assertDictEqual(result, expected)

    def test_decode(self):
        js = JsonSupport(WORKING_FILE)

        container = {'x': 1, 'y': 'Ynl0ZXM=', 'z': {'a': 'a', 'b': ['b', 'Yg==']}}

        result = js.decode(container)
        expected = {
            "x" : 1,
            "y" : b"bytes",
            "z" : {
                "a": "a",
                "b" : ["b", b"b"]
            }
        }

        self.assertDictEqual(result, expected)

    def test_write_and_read(self):
        js = JsonSupport(WORKING_FILE)

        container = {
            "x" : 1,
            "y" : b"bytes",
            "z" : {
                "a": "a",
                "b" : ["b", b"b"]
            }
        }

        js.dump(container)
        result = js.load()

        self.assertDictEqual(result, container)