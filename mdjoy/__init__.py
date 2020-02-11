# Copyright 2020 Olivier Fisette

from random import shuffle
import numpy as np
try:
    from mdjoy.taskmonitor import TaskMonitor
    DefaultMonitor = TaskMonitor
except:
    from mdjoy.nullmonitor import NullMonitor
    DefaultMonitor = NullMonitor

__all__ = ["cell2box", "box2cell", "get_R", "set_R", "extents", "is_inside",
        "renumber_atoms", "renumber_residues", "by_residue", "by_chain",
        "is_heavy_atom", "is_clashing", "find_clashes"]

def cell2box(cell):
    """Return the lengths (3-tuple) and angles (3-tuple) of the given cell."""
    A, B, C = cell.transpose()
    a, b, c = lengths = [np.linalg.norm(V) for V in [A, B, C]]
    alpha = np.arccos(np.dot(B,C) / (b*c))
    beta = np.arccos(np.dot(A,C) / (a*c))
    gamma = np.arccos(np.dot(A,B) / (a*b))
    angles = [np.rad2deg(angle) for angle in [alpha, beta, gamma]]
    return lengths, angles

def box2cell(lengths, angles):
    """Return a 3x3 cell matrix for the given box lengths and angles."""
    x, y, z = lengths
    alpha, beta, gamma = [np.deg2rad(angle) for angle in angles]
    # A lies along the positive X axis:
    Ax, Ay, Az = A = [x, 0.0, 0.0]
    # B lies in the X-Y plane:
    Bx, By, Bz = B = [y*np.cos(alpha), y*np.sin(alpha), 0.0]
    Cx = z*np.cos(beta)
    Cy = (y*z*np.cos(gamma) - Bx*Cx) / By
    Cz = np.sqrt(z**2 - Cx**2 - Cy**2)
    C = [Cx, Cy, Cz]
    return np.array([A, B, C]).transpose()

def get_R(atoms):
    """Return the (x,y,z) coordinates of the given atoms as a 3xN matrix."""
    return np.array([[atom.x, atom.y, atom.z] for atom in atoms]).transpose()

def set_R(atoms, source):
    """Set atoms (x,y,z) coordinates from the source 3xN matrix."""
    if len(source) > 0 and hasattr(source[0], "x"):
        set_R(atoms, get_R(source))
    else:
        for n in range(len(atoms)):
            atoms[n].x = source[0][n]
            atoms[n].y = source[1][n]
            atoms[n].z = source[2][n]

def extents(atoms):
    """Return the min/max coordinates of a collection of atoms.
    
    return value -- 3x2 array of (x,y,z) and min/max, respectively"""
    R = get_R(atoms)
    xmin = np.min(R[0])
    xmax = np.max(R[0])
    ymin = np.min(R[1])
    ymax = np.max(R[1])
    zmin = np.min(R[2])
    zmax = np.max(R[2])
    return np.array([[xmin, xmax], [ymin, ymax], [zmin, zmax]])

def is_inside(atom, ext):
    """Check (bool) if an atom is inside the given extents.
    
    ext -- 3x2 array of (x,y,z) and min/max, respectively"""
    return atom.x >= ext[0,0] and \
            atom.x <= ext[0,1] and \
            atom.y >= ext[1,0] and \
            atom.y <= ext[1,1] and \
            atom.z >= ext[2,0] and \
            atom.z <= ext[2,1]

def renumber_atoms(atoms):
    """Renumber the given atoms consecutively, starting at 1."""
    id = 1
    for atom in atoms:
        atom.id = id
        id += 1

def renumber_residues(atoms):
    """Renumber residues in the given atoms consecutively, starting at 1."""
    resid = 0
    last = None
    for atom in atoms:
        if atom.resid != last:
            last = atom.resid
            resid += 1
        atom.resid = resid

def by_residue(atoms):
    """Iterate over atoms by residue, returning a list of list of atoms."""
    residues = []
    current = []
    lastid = None
    lastname = None
    lastchain = None
    for atom in atoms:
        if atom.resid != lastid or atom.resname != lastname or \
                atom.chain != lastchain:
            if len(current) != 0:
                residues.append(current)
            current = [atom]
            lastid = atom.resid
            lastname = atom.resname
            lastchain = atom.chain
        else:
            current.append(atom)
    if len(current) != 0:
        residues.append(current)
    return residues

def by_chain(atoms):
    """Iterate over atoms by chain, returning a list of list of atoms."""
    chains = []
    current = []
    last = None
    for atom in atoms:
        if atom.chain != last:
            if len(current) != 0:
                chains.append(current)
            current = [atom]
            last = atom.chain
        else:
            current.append(atom)
    if len(current) != 0:
        chains.append(current)
    return chains

def is_heavy_atom(atom):
    """Check if an atom is neither a hydrogen or a virtual site."""
    return not (atom.resname.startswith("H") or atom.resname.startswith("M"))

def is_clashing(atom, others, max_dist):
    """Check if a given atom is closer than max_dist from at least one atom in
    another given set."""
    # Avoid sqrt by comparing squared distances.
    max_dist2 = max_dist**2
    for atom2 in others:
        dx = atom2.x - atom.x
        dy = atom2.y - atom.y
        dz = atom2.z - atom.z
        d2 = dx*dx + dy*dy + dz*dz
        if d2 < max_dist2:
            return True
    return False

def find_clashes(insertion, target, max_dist = 3.0, grouping = by_residue, \
        filter = is_heavy_atom, Monitor = DefaultMonitor):
    """Find clashes between the 'insertion' and 'target' sets of atoms.
    
    max_dist -- Atoms closer than this distance are clashing
    grouping -- Function used to partition the insertion set into groups
                (default: by_residue); if one atom in a group clashes with the
                target, all atoms in the group are considered clashes
    filter   -- Function to apply to the insertion set to determine which atoms
                are used in distance comparisons (default: is_heavy_atom,
                excluding virtual sites and hydrogens)
    Monitor  -- A monitor class to display a progress bar (useful for very large
                systems/insertions)"""
    groups = grouping(insertion)
    filtered_groups = []
    for group in groups:
        filtered_groups.append([atom for atom in group if filter(atom)])
    filtered_insertion = [atom for group in filtered_groups for atom in group]
    filtered_target = [atom for atom in target if filter(atom)]

    ext = extents(filtered_insertion + filtered_target)
    nx = int(np.ceil((ext[0,1] - ext[0,0]) / max_dist)) + 2
    ny = int(np.ceil((ext[1,1] - ext[1,0]) / max_dist)) + 2
    nz = int(np.ceil((ext[2,1] - ext[2,0]) / max_dist)) + 2
    grid = [[[[] for zi in range(nz)] for yi in range(ny)] for xi in range(nx)]

    for atom in filtered_target:
        xi = int(np.floor((atom.x - ext[0,0]) / max_dist)) + 1
        yi = int(np.floor((atom.y - ext[1,0]) / max_dist)) + 1
        zi = int(np.floor((atom.z - ext[2,0]) / max_dist)) + 1
        grid[xi][yi][zi].append(atom)

    clashing_group_idx = []
    allowed_group_idx = []
    group_idx = list(range(len(groups)))
    shuffle(group_idx)
    monitor = Monitor(maxval = len(group_idx)).start()
    for (n,i) in enumerate(group_idx):
        monitor.update(n+1)
        allowed = True
        for atom in filtered_groups[i]:
            xi = int(np.floor((atom.x - ext[0,0]) / max_dist)) + 1
            yi = int(np.floor((atom.y - ext[1,0]) / max_dist)) + 1
            zi = int(np.floor((atom.z - ext[2,0]) / max_dist)) + 1
            neighbours = []
            for xj in range(xi-1, xi+1 + 1):
                for yj in range(yi-1, yi+1 + 1):
                    for zj in range(zi-1, zi+1 + 1):
                        neighbours.extend(grid[xj][yj][zj])
            if is_clashing(atom, neighbours, max_dist):
                allowed = False
                clashing_group_idx.append(i)
                break
        if allowed:
            allowed_group_idx.append(i)
    monitor.finish()

    clashing_group_idx.sort()
    clashing = []
    for i in clashing_group_idx:
        for atom in groups[i]:
            clashing.append(atom)
    allowed_group_idx.sort()
    allowed = []
    for i in allowed_group_idx:
        for atom in groups[i]:
            allowed.append(atom)
    return clashing, allowed
