# Copyright 2020 Olivier Fisette

class XYZAtom:
    """An atom record in an XYZ structure"""

    def __init__(self, name, x, y, z):
        self.chain = ""
        self.resid = None
        self.resname = ""
        self.name = name
        self.x = x
        self.y = y
        self.z = z

def read(infile):
    """Read an XYZ structure from a filename or stream, returning a (title, 
    atoms) tuple"""
    if isinstance(infile, str):
        infile = open(infile)

    natoms = int(infile.readline().strip())
    title = infile.readline().strip()

    atoms = []
    for i in range(natoms):
        tokens = infile.readline().split()
        name = tokens[0]
        x = float(tokens[1])
        y = float(tokens[2])
        z = float(tokens[3])
        atoms.append(XYZAtom(name, x, y, z))

    return atoms, title

def write(outfile, atoms, title = ""):
    """Write a Gromos87 structure to a filename or stream, from the given atoms
    and, optionally, cell (3x3 matrix) and title"""
    if isinstance(outfile, str):
        outfile = open(outfile, "w")

    outfile.write(str(len(atoms)) + "\n")
    outfile.write(title + "\n")

    atomfmt = "{} {} {} {}\n"
    for atom in atoms:
        outfile.write(atomfmt.format(atom.name, atom.x, atom.y, atom.z))
