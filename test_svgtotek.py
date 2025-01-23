import unittest
from svgtotek import TekPath, TekShape
from svgpathtools import Path, Line


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

    def test_deduplicate(self):
        self.assertEqual(
            str(TekPath([(0, 0), (0, 779), (0, 779), (1023, 779), (1023, 0), (1023, 0)])),
            ' ` @8k @8k?_ `?_'
        )


class TestTekShape(unittest.TestCase):

    SVG_SEG_1 = Line(200+300j, 250+350j)
    SVG_SEG_2 = Line(250+350j, 250+400j)
    SVG_SEG_3 = Line(250+400j, 250+450j)
    SVG_SEG_4 = Line(250+450j, 250+500j)

    def test_closed_paths(self):
        tekShape = TekShape([
            Path(self.SVG_SEG_1, self.SVG_SEG_2),
            Path(self.SVG_SEG_3, self.SVG_SEG_4)
        ])
        self.assertEqual(
            len(tekShape.paths),
            2
        )
        self.assertEqual(
            len(tekShape.paths[0].coordinates),
            3
        )
        self.assertEqual(
            len(tekShape.paths[1].coordinates),
            2
        )

    def test_open_paths(self):
        tekShape = TekShape([
            Path(self.SVG_SEG_1),
            Path(self.SVG_SEG_3, self.SVG_SEG_4)
        ])
        self.assertEqual(
            len(tekShape.paths),
            2
        )
        self.assertEqual(
            len(tekShape.paths[0].coordinates),
            2
        )
        self.assertEqual(
            len(tekShape.paths[1].coordinates),
            3
        )
