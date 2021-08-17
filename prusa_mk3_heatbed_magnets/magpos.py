#!/usr/bin/python

import os
import sys
import getopt
import csv

class Rect:
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    def offset(self, xoffset, yoffset):
        return Rect(self.x + float(xoffset), self.y + float(yoffset), self.width, self.height)

    def inflate(self, xinflate, yinflate):
        return Rect(self.x - float(xinflate)/2, self.y - float(yinflate)/2, self.width + xinflate, self.height + yinflate)


def parse_magnet_file(magnet_input_file, xorigin, yorigin, xinflate, yinflate):
    magnets = []
    with open(magnet_input_file, newline = '') as csvfile:
        magnetreader = csv.reader(csvfile, delimiter=',')
        headerrow = True
        for row in magnetreader:
            if headerrow:
                headerrow = False
            else:
                magnet = Rect(row[0], row[1], row[2], row[3]).offset(-xorigin, -yorigin).inflate(xinflate, yinflate)
                magnets.append(magnet)
    return magnets


def process_svg_file(magnets, svg_output_file):
    with open(os.path.join(sys.path[0], "steel-sheet.svg"), mode = 'r', newline = '') as svginpf :
        with open(svg_output_file, mode = 'w') as svgoutf:
            for line in svginpf:
                if "{{MAGNET_RECTANGLES}}" in line:
                    for magnet in magnets:
                        rectline = '<rect x="{x:.3f}" y="{y:.3f}" width="{width:.3f}" height="{height:.3f}"/>'.format(x = magnet.x, y = magnet.y, width = magnet.width, height = magnet.height)
                        svgoutf.write(rectline)
                        svgoutf.write('\n')
                else:
                    svgoutf.write(line)


def process_klipper_file(magnets, klipper_output_file):
    with open(klipper_output_file, mode = 'w') as outf:
        num = 1
        for magnet in magnets:
            outf.write("faulty_region_{num}_min: {minx:.3f}, {miny:.3f}\n".format(num = num, minx = magnet.x, miny = magnet.y))
            outf.write("faulty_region_{num}_max: {maxx:.3f}, {maxy:.3f}\n".format(num = num, maxx = magnet.x + magnet.width, maxy = magnet.y + magnet.height))
            num = num + 1

def print_usage():
    print("Usage: ", sys.argv[0], " -m magnet_input_file [-k klipper_output_file] [-s svg_output_file] [-o x_origin,y_origin] [-i x_inflate,y_inflate")

def main(argv):
    magnet_input_file = ''
    klipper_output_file = ''
    svg_output_file = ''
    xorigin = 0
    yorigin = 0
    xinflate = 0
    yinflate = 0

    try:
        opts, args = getopt.getopt(argv, "m:k:s:g:o:i:")
    except:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-m':
            magnet_input_file = arg
        elif opt == '-k':
            klipper_output_file = arg
        elif opt == '-s':
            svg_output_file = arg
        elif opt == '-o':
            (xorigin, yorigin) = arg.split(",")
        elif opt == '-i':
            (xinflate, yinflate) = arg.split(",")

    if magnet_input_file == '':
        print("magnet_input_file is required")
        print_usage()
        sys.exit(2)

    magnets = parse_magnet_file(magnet_input_file, float(xorigin), float(yorigin), float(xinflate), float(yinflate))

    if svg_output_file != '':
        process_svg_file(magnets, svg_output_file)

    if klipper_output_file != '':
        process_klipper_file(magnets, klipper_output_file)

if __name__ == "__main__":
   main(sys.argv[1:])