#!/usr/bin/env python
"""
Converts SVG paths to Tektronix 4010-compatible instructions.
This was helpful: https://vt100.net/docs/vt3xx-gp/chapter13.html
"""
import os
from time import sleep

import click
import svgpathtools

MARGIN = 10

GS = chr(0x1d)  # Group Select character
MAX_X_COORDINATE = 1023
MAX_Y_COORDINATE = 779


class TekPath:
    def __init__(self, coordinates):
        self.coordinates = []
        previous = coordinates[0]
        self.coordinates.append(coordinates[0])
        for coordinate in coordinates[1:]:
            if coordinate != previous:
                self.coordinates.append(coordinate)
            previous = coordinate

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
    def __init__(self, svg_paths):

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
        for svg_path in svg_paths:
            for segment in svg_path:
                if isinstance(segment, svgpathtools.path.Line):
                    self.paths.append(TekPath(
                        flip_y([(segment.start.real, segment.start.imag),
                                (segment.end.real, segment.end.imag)
                                ])))
                elif isinstance(segment, svgpathtools.path.CubicBezier):
                    self.paths.append(TekPath(flip_y(bezier_to_coordinates(segment))))
                else:
                    raise ValueError(f"Unsupported path type: {type(segment)}")

    def __str__(self):
        tek_string = ""
        last_coordinate = None
        for path in self.paths:
            if path.coordinates[0] == last_coordinate:
                tek_string += str(TekPath(path.coordinates[1:]))
            else:
                tek_string += GS + str(path)
            last_coordinate = path.coordinates[-1]
        return tek_string


# svgpathtools uses (min_x, max_x, min_y, max_y)
def max_bounding(tuples):
    return (
        min([t[0] for t in tuples]),
        max([t[1] for t in tuples]),
        min([t[2] for t in tuples]),
        max([t[3] for t in tuples]),
    )


def fit(paths, svg_min, svg_max):
    shape_bbox = max_bounding([path.bbox() for path in paths])
    scale = min(
        (svg_max.real - svg_min.real) / (shape_bbox[1] - shape_bbox[0]),
        (svg_max.imag - svg_min.imag) / (shape_bbox[3] - shape_bbox[2])
    )
    scaled_paths = [path.scaled(scale) for path in paths]

    shape_bbox = max_bounding([path.bbox() for path in scaled_paths])
    offset = complex(
        (svg_min.real + svg_max.real) / 2 - (shape_bbox[0] + shape_bbox[1]) / 2,
        (svg_min.imag + svg_max.imag) / 2 - (shape_bbox[2] + shape_bbox[3]) / 2,
    )
    translated_paths = [path.translated(offset) for path in scaled_paths]

    return translated_paths


def write_tek_file(filename, svg_paths):
    with open(filename, 'w') as f:
        f.write(str(TekShape(svg_paths)))


def draw_on_terminal(svg_paths, display_time=2):
    GS = chr(0x1d)
    US = chr(0x1f)
    CAN = chr(0x18)
    # ESC = chr(0x1b)
    # FF = chr(0x0c)
    EM = chr(0x19)

    os.system('clear')
    print(GS + str(TekShape(svg_paths)), end='', flush=True)
    sleep(display_time)
    print(EM + US + CAN)
    os.system('clear')


def pretty_bounding(bounding_box):
    return (
        f"({int(bounding_box[0])}, {int(bounding_box[1])}), " +
        f"({int(bounding_box[2])}, {int(bounding_box[3])})"
    )


def display_info(svg_paths):
    print(f"This shape has {len(svg_paths)} paths.")
    print("overall bounding box: " +
          f"{pretty_bounding(max_bounding([path.bbox() for path in svg_paths]))}")
    for path in svg_paths:
        print(f"path with bounding box: {pretty_bounding(path.bbox())} has {len(path)} segments")
        print(f"  Lines: {len([s for s in path if isinstance(s, svgpathtools.Line)])}")
        print(f"  CubicBezier: {len([s for s in path if isinstance(s, svgpathtools.CubicBezier)])}")
        print(f"  Arc: {len([s for s in path if isinstance(s, svgpathtools.Arc)])}")
        print("  QuadraticBezier: " + str(len([
            s for s in path if isinstance(s, svgpathtools.QuadraticBezier)
        ])))
        print("  other: " + str(len([
            s for s in path if not isinstance(s, (
                svgpathtools.Line,
                svgpathtools.CubicBezier,
                svgpathtools.Arc,
                svgpathtools.QuadraticBezier
            ))])))


@click.command()
@click.argument('svg_file')
@click.option('--info', '-i', help='Display SVG info', is_flag=True, default=False)
@click.option('--output', '-o', help='Output to file')
@click.option('--display', '-d', help='Display to Tektronix', is_flag=True, default=False)
@click.option('--time', '-t', help='Time to display', default=2)
def main(svg_file, info, output, display, time):
    svg_paths, _attributes = svgpathtools.svg2paths(svg_file)
    fitted = fit(svg_paths, complex(0, 0), complex(MAX_X_COORDINATE, MAX_Y_COORDINATE))
    if info:
        display_info(fitted)
    if display:
        draw_on_terminal(fitted, display_time=time)
    if output:
        write_tek_file(output, fitted)


if __name__ == "__main__":
    main()
