#!/usr/bin/env python

import pynmrstar, argparse

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mrfile", help="NMR star file",   type=str,
        default=None)
    parser.add_argument("-p", "--pdbfile", help="PDB file with correct GROMACS atom numbering.", type=str,
        default=None)
    parser.add_argument("-o", "--itpfile", help="ITP file", type=str,
        default="mr.itp")

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args  = parseArguments()

    if args.mrfile:
        entry = pynmrstar.Entry.from_file(args.mrfile)
        entry.print_tree()
