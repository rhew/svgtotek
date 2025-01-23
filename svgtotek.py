"""
Converts SVG paths to Tektronix 4010-compatible instructions.
This was helpful: https://vt100.net/docs/vt3xx-gp/chapter13.html
"""
import svgpathtools

MARGIN = 10

GS = chr(0x1d)  # Group Select character
MAX_X_COORDINATE = 1023
MAX_Y_COORDINATE = 779


class TekPath:
    def __init__(self, coordinates):
        self.coordinates = [
            (coordinate[0], coordinate[1]) for coordinate in coordinates
        ]

    def bbox(self):
        return (
            min([coordinate[0] for coordinate in self.coordinates]),
            min([coordinate[1] for coordinate in self.coordinates]),
            max([coordinate[0] for coordinate in self.coordinates]),
            max([coordinate[1] for coordinate in self.coordinates])
        )

    def scale(self, factor):
        return TekPath([
            (coordinate[0] * factor, coordinate[1] * factor)
            for coordinate in self.coordinates
        ])

    def offset(self, offset):
        return TekPath([
            (coordinate[0] + offset[0], coordinate[1] + offset[1])
            for coordinate in self.coordinates
        ])

    def __str__(self):
        tek_string = ""
        for (x, y) in self.coordinates:
            tek_string += (
                (chr((0b00100000) | ((int(y) >> 5) & 0b00011111))) +  # encode high y
                (chr((0b01100000) | (int(y) & 0b00011111))) +         # encode low y
                (chr((0b00100000) | ((int(x) >> 5) & 0b00011111))) +  # encode high x
                (chr((0b01000000) | (int(x) & 0b00011111)))           # encode low x
            )
        return tek_string


class TekShape:
    def __init__(self, svg_file):

        def flip_y(coordinates):
            return [(coordinate[0], MAX_Y_COORDINATE - coordinate[1]) for coordinate in coordinates]

        def bezier_to_svg_points(bezier, num_samples=6):
            return [bezier.start] + [
                bezier.point(t / (float(num_samples)-1)) for t in range(num_samples)
            ]

        def svg_points_to_coordinates(points):
            return [(point.real, point.imag) for point in points]

        def bezier_to_coordinates(bezier, num_samples=6):
            return svg_points_to_coordinates(bezier_to_svg_points(bezier, num_samples))

        self.paths = []
        svg_paths, attributes = svgpathtools.svg2paths(svg_file)
        for svg_path in svg_paths:
            for segment in svg_path:
                if isinstance(segment, svgpathtools.path.Line):
                    self.paths.append(TekPath(flip_y([
                         (segment.start.real, segment.start.imag),
                         (segment.end.real, segment.end.imag)
                    ])))
                elif isinstance(segment, svgpathtools.path.CubicBezier):
                    self.paths.append(TekPath(flip_y(bezier_to_coordinates(segment))))
                else:
                    raise ValueError(f"Unsupported path type: {type(segment)}")

    def fit(self):
        def offset_to_center(bbox):
            return (
                MAX_X_COORDINATE / 2 - (bbox[2] + bbox[0]) / 2,
                MAX_Y_COORDINATE / 2 - (bbox[3] + bbox[1]) / 2
            )
        scale_factor = min(
            (MAX_X_COORDINATE - (MARGIN * 2)) / (self.bbox()[2] - self.bbox()[0]),
            (MAX_Y_COORDINATE - (MARGIN * 2)) / (self.bbox()[3] - self.bbox()[1]),
        )
        self.paths = [path.scale(scale_factor) for path in self.paths]
        offset = offset_to_center(self.bbox())
        self.paths = [path.offset(offset) for path in self.paths]
        return self

    def __str__(self):
        tek_string = ""
        for path in self.paths:
            tek_string += GS + str(path)
        return tek_string

    def bbox(self):
        def max_bounding(tuples):
            return (
                min([t[0] for t in tuples]),
                min([t[1] for t in tuples]),
                max([t[2] for t in tuples]),
                max([t[3] for t in tuples]),
            )
        return max_bounding([path.bbox() for path in self.paths])


if __name__ == "__main__":
    input_svg = 'input.svg'
    shape = TekShape(input_svg)
    shape.fit()
    with open('input.tek', 'w') as f:
        f.write(str(shape))
