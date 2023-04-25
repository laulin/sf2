import unittest

from sf2.openinram import OpenInRAM

class TestCore(unittest.TestCase):
    def test_interpole_command(self):
        oir = OpenInRAM(None, "")
        result = oir.interpole_command("cat {filename}")
        expected = "cat {filename}"

        self.assertEqual(result, expected)

    def test_interpole_command_bracket(self):
        oir = OpenInRAM(None, "")
        result = oir.interpole_command("cat [ filename ]")
        expected = "cat {filename}"

        self.assertEqual(result, expected)

    def test_interpole_command_default(self):
        oir = OpenInRAM(None, "")
        result = oir.interpole_command("cat")
        expected = "cat {filename}"

        self.assertEqual(result, expected)
