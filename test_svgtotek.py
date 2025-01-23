import unittest
from svgtotek import TekPath


class TestTekPath(unittest.TestCase):

    BORDER = TekPath([(0, 0), (0, 779), (1023, 779), (1023, 0)])

    def test_vector_mode_checkout_coordinates(self):
        self.assertEqual(
            str(self.BORDER),
            ' ` @8k @8k?_ `?_'
        )
