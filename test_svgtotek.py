import unittest
from svgtotek import TekPath


class TestTekPath(unittest.TestCase):

    BORDER = TekPath([(0, 0), (0, 779), (1023, 779), (1023, 0)])

    def test_vector_mode_checkout_coordinates(self):
        self.assertEqual(
            str(self.BORDER),
            ' ` @8k @8k?_ `?_'
        )

    def test_scale(self):
        self.assertEqual(
            str(self.BORDER.scale(0.5)),
            ' ` @,e @,e/_ `/_'
        )

    def test_offset(self):
        self.assertEqual(
            str(self.BORDER.scale(0.5).offset((75, -10))),
            '?v"K+{"K+{2J?v2J'
        )
