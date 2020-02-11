# Copyright 2020 Olivier Fisette

import numpy as np

cell_order = [(0,0), (1,1), (2,2), (1,0), (2,0), (0,1), (2,1), (0,2), (1,2)]

class GROAtom:
    """An atom record in a Gromos87 structure"""

    def __init__(self, resid, resname, name, id, x, y, z):
        self.chain = ""
        self.resid = resid
        self.resname = resname
        self.name = name
        self.id = id
        self.x = x
        self.y = y
        self.z = z

def read(infile):
    """Read a Gromos87 structure from a filename or stream, returning an (atoms, 
    cell, title) tuple"""
    if isinstance(infile, str):
        infile = open(infile)

    lines = infile.readlines()
    title = lines[0]

    cell = np.zeros((3,3))
    for (n, val) in enumerate([float(token) for token in lines[-1].split()]):
        i, j = cell_order[n]
        cell[i,j] = val * 10

    atoms = []
    for line in lines[2:-1]:
        resid = int(line[0:5])
        resname = line[5:9].strip()
        name = line[11:15].strip()
        id = int(line[15:20])
        x = float(line[20:28]) * 10
        y = float(line[28:36]) * 10
        z = float(line[36:44]) * 10
        atoms.append(GROAtom(resid, resname, name, id, x, y, z))

    delta = 0
    for atom in atoms:
        if atom.id == 0:
            delta += 100000
        atom.id += delta
    delta = 0
    for atom in atoms:
        if atom.resid == 0:
            delta += 100000
        atom.resid += delta

    return atoms, cell, title

def write(outfile, atoms, cell = np.zeros((3,3)), title = ""):
    """Write a Gromos87 structure to a filename or stream, from the given atoms
    and, optionally, cell (3x3 matrix) and title"""
    if isinstance(outfile, str):
        outfile = open(outfile, "w")

    outfile.write(title + "\n")
    outfile.write("{:d}\n".format(len(atoms)))

    atomfmt = "{:5d}{:5s}{:>5s}{:5d}{:8.3f}{:8.3f}{:8.3f}\n"
    for atom in atoms:
        id = atom.id
        while id > 99999:
            id -= 100000
        resid = atom.resid
        while resid > 99999:
            resid -= 100000
        outfile.write(atomfmt.format(resid, atom.resname, atom.name, id, \
                atom.x / 10, atom.y / 10, atom.z / 10))

    for (i,j) in cell_order:
        outfile.write("{:10.5f}".format(cell[i,j] / 10))
    outfile.write("\n")
