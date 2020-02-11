# Copyright 2020 Olivier Fisette

from textwrap import wrap
from mdjoy import *

class PDBAtom:
    """An atom record in a PDB structure"""

    def __init__(self, hetatom, id, name, alternate, resname, chain, resid, \
            insertion, x, y, z, occupancy, temperature, \
            segment, element, charge):
        self.hetatom = hetatom
        self.id = id
        self.name = name
        self.alternate = alternate
        self.resname = resname
        self.chain = chain
        self.resid = resid
        self.insertion = insertion
        self.x = x
        self.y = y
        self.z = z
        self.occupancy = occupancy
        self.temperature = temperature
        self.segment = segment
        self.element = element
        self.charge = charge

def read(infile):
    """Read a PDB structure from a filename or stream, returning an (atoms,
    cell, title) tuple"""
    if isinstance(infile, str):
        infile = open(infile)

    title = ""
    cell = None
    atoms = []

    for line in infile:
        if line.startswith("END"):
            break
        elif line.startswith("TITLE"):
            if not title == "":
                title += " "
            title += line[10:].strip()
        elif line.startswith("CRYST1"):
            tokens = line.split()
            lengths = [float(token) for token in tokens[1:4]]
            angles = [float(token) for token in tokens[4:7]]
            cell = box2cell(lengths, angles)
        elif line.startswith("ATOM") or line.startswith("HETATM"):
            hetatom = line.startswith("HETATM")
            id = int(line[6:11])
            name = line[12:16].strip()
            if len(name) > 0 and name[0] in '0123456789':
                name = name[1:] + name[0]
            alternate = line[16]
            resname = line[17:21].strip()
            chain = line[21]
            resid = int(line[22:26])
            insertion = line[26]
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            occupancy = float(line[54:60])
            temperature = float(line[60:66])
            segment = line[72:76].strip()
            element = line[76:78].strip()
            charge = line[78:80].strip()
            atoms.append(PDBAtom(hetatom, id, name, alternate, resname, chain, \
                                 resid, insertion, x, y, z, occupancy, \
                                 temperature, segment, element, charge))

    delta = 0
    for atom in atoms:
        if atom.id == 0:
            delta += 100000
        atom.id += delta
    delta = 0
    for atom in atoms:
        if atom.resid == 0:
            delta += 10000
        atom.resid += delta

    return atoms, cell, title

def write(outfile, atoms, cell = None, title = None):
    """Write a PDB structure to a filename or stream, from the given atoms and,
    optionally, cell (3x3 matrix) and title"""
    if isinstance(outfile, str):
        outfile = open(outfile, "w")

    if not title is None:
        for (n, line) in enumerate(wrap(title, 70)):
            if n > 0:
                outfile.write("TITLE {:4d} {}\n".format(n+1, line))
            else:
                outfile.write("TITLE     {}\n".format(line))
    if not cell is None:
        lengths, angles = cell2box(cell)
        boxfmt = "CRYST1{:9.3f}{:9.3f}{:9.3f}{:7.2f}{:7.2f}{:7.2f} " + \
                "P 1           1\n"
        outfile.write(boxfmt.format(*lengths, *angles))
    atomfmt = "{:6s}{:5d} {:4s}{:1s}{:4s}{:1s}{:4d}{:1s}   " + \
                  "{:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}      " + \
                  "{:4s}{:2s}{:2s}\n"
    for atom in atoms:
        if atom.hetatom:
            atomstr = "HETATM"
        else:
            atomstr = "ATOM  "
        if len(atom.name) == 4:
            name = atom.name
        else:
            name = " " + atom.name.ljust(3)
        id = atom.id
        while id > 99999:
            id -= 100000
        resid = atom.resid
        while resid > 9999:
            resid -= 10000
        outfile.write(atomfmt.format(atomstr, id, name, atom.alternate, \
                atom.resname, atom.chain, resid, atom.insertion, \
                atom.x, atom.y, atom.z, atom.occupancy, atom.temperature, \
                atom.segment, atom.element.rjust(2), atom.charge))
    outfile.write("END\n")
