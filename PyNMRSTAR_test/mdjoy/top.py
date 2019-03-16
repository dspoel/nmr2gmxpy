import re

class GmxTopGlobalError(Exception):

    def __init__(self, line, section, msg):
        self.line = line
        self.section = section
        self.msg = msg

    def __str__(self):
        if self.section:
            return "line %d, section '%s': %s" % \
                    (self.line, self.section, self.msg)
        else:
            return 'line %d, outside a section: %s' % (self.line, self.msg)

class GmxTopInstError(Exception):

    def __init__(self, msg, expected = None, read = None, found = None):
        self.msg = msg
        self.expected = expected
        self.read = read
        self.found = found

    def __str__(self):
        if self.expected:
            if self.read:
                return "%s; expected %s, read '%s'" % (self.msg, \
                                                       str(self.expected), \
                                                       str(self.read))
            elif self.found:
                return '%s; expected %s, found %s' % (self.msg, \
                                                      str(self.expected), \
                                                      str(self.found))
            else:
                raise Exception('unhandled internal parser error')
        else:
            return self.msg

class GmxTopInst:

    def __init__(self, line):
        if line.endswith('\n'):
            line = line[:-1]
        match = re.search('\s*;', line)
        if match:
            self.comment = line[match.start():].rstrip()
            self.parse(line[:match.start()])
        else:
            self.comment = ''
            self.parse(line)

    def parse(self, inst):
        raise NotImplementedError()

    def format(self, aflen=5):
        return '%s%s\n' % (self.format_internal(aflen), self.comment)

    def format_internal(self, aflen):
        raise NotImplementedError()

    def get_atom_nrs(self):
        return []

    def set_atom_nrs(self, atoms):
        pass

class GmxTopComment(GmxTopInst):

    def parse(self, inst):
        pass

    def format_internal(self, aflen):
        return ""

class GmxTopHeader(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        if not len(tokens) == 3:
            raise GmxGmxTopInstError('invalid section header')
        if not tokens[0] == '[' and tokens [2] == ']':
            raise GmxGmxTopInstError('invalid section header')
        self.title = tokens[1]

    def format_internal(self, aflen):
        return '[ %s ]' % self.title

class GmxTopDefaults(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if count != 5:
            raise GmxGmxTopInstError('invalid column count', 5, count)
        try:
            self.nbfunc = int(tokens[0])
        except ValueError:
            raise GmxGmxTopInstError('invalid nbfunc', 'integer', tokens[0])
        try:
            self.func_rule = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid func_rule', 'integer', tokens[1])
        self.gen_pairs = tokens[2]
        try:
            self.fudgeLJ = float(tokens[3])
        except ValueError:
            raise GmxTopInstError('invalid fudgeLJ', 'float', tokens[3])
        try:
            self.fudgeQQ = float(tokens[4])
        except ValueError:
            raise GmxTopInstError('invalid fudgeQQ', 'float', tokens[4])

    def format_internal(self, aflen):
        return "%-15d %-15d %-15s %-7.1f %-6.4f" % (self.nbfunc, \
                                                    self.func_rule, \
                                                    self.gen_pairs, \
                                                    self.fudgeLJ, \
                                                    self.fudgeQQ)

class GmxTopAtomType(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if count != 7:
            raise GmxTopInstError('invalid column count', 5, count)
        self.name = tokens[0]
        self.atype = tokens[1]
        try:
            self.mass = float(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid mass', 'float', tokens[2])
        try:
            self.charge = float(tokens[3])
        except ValueError:
            raise GmxTopInstError('invalid charge', 'float', tokens[3])
        self.ptype = tokens[4]
        try:
            self.sigma = float(tokens[5])
        except ValueError:
            raise GmxTopInstError('invalid sigma', 'float', tokens[5])
        try:
            self.epsilon = float(tokens[6])
        except ValueError:
            raise GmxTopInstError('invalid epsilon', 'float', tokens[6])

    def format_internal(self, aflen):
        return '%-6s  %6s    %8.3f   %6.4f  %-3s %.5e  %.5e' % \
               (self.name, self.atype, self.mass, self.charge, self.ptype, \
                self.sigma, self.epsilon)

class GmxTopMoleculeType(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not count == 2:
            raise GmxTopInstError('invalid column count', 2, found = count)
        self.name = tokens[0]
        try:
            self.nrexcl = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid nrexcl', 'integer', tokens[1])

    def format_internal(self, aflen):
        return '%-16s %2d' % (self.name, self.nrexcl)

class GmxTopAtom(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if count != 8 and count != 11:
            raise GmxTopInstError('invalid column count', '8 or 11', \
                                     found = count)
        try:
            self.nr = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid nr', 'integer', tokens[0])
        self.atype = tokens[1]
        try:
            self.resnr = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid resnr', 'integer', tokens[2])
        self.residue = tokens[3]
        self.atom = tokens[4]
        try:
            self.cgnr = int(tokens[5])
        except ValueError:
            raise GmxTopInstError('invalid cgnr', 'integer', tokens[5])
        try:
            self.charge = float(tokens[6])
        except ValueError:
            raise GmxTopInstError('invalid charge', 'float', tokens[6])
        try:
            self.mass = float(tokens[7])
        except ValueError:
            raise GmxTopInstError('invalid mass', 'float', tokens[7])
        if count == 11:
            self.atypeB = tokens[8]
            try:
                self.chargeB = float(tokens[9])
            except ValueError:
                raise GmxTopInstError('invalid chargeB', 'float', tokens[9])
            try:
                self.massB = float(tokens[10])
            except ValueError:
                raise GmxTopInstError('invalid massB', 'float', tokens[10])
        else:
            self.atypeB, self.chargeB, self.massB = None, None, None

    def format_internal(self, aflen):
        if abs(self.charge) < 10e-6:
            charge = "         0"
        else:
            charge = "%10.4f" % self.charge
        if abs(self.mass) < 10e-6:
            mass = "         0"
        else:
            mass = "%10.3f" % self.mass
        if self.atypeB is not None:
            if abs(self.chargeB) < 10e-6:
                chargeB = "         0"
            else:
                chargeB = "%10.4f" % self.chargeB
            if abs(self.massB) < 10e-6:
                massB = "         0"
            else:
                massB = "%10.3f" % self.massB
            return '%6d %10s %6d %6s %6s %6d %s %s %10s %s %s' \
                   % (self.nr, self.atype, self.resnr, self.residue, \
                      self.atom, self.cgnr, charge, mass, \
                      self.typeB, chargeB, massB)
        else:
            return '%6d %10s %6d %6s %6s %6d %s %s' % \
                   (self.nr, self.atype, self.resnr, self.residue, \
                    self.atom, self.cgnr, charge, mass)

    def get_atom_nrs(self):
        return [self.nr]

    def set_atom_nrs(self, new_values):
        self.nr = new_values[0]

class GmxTopBond(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not (count >= 3 and count <= 7):
            raise GmxTopInstError('invalid column count', '3 to 7', \
                                     found = count)
        try:
            self.ai = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid ai', 'integer', tokens[0])
        try:
            self.aj = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid aj', 'integer', tokens[1])
        try:
            self.funct = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid funct', 'integer', tokens[2])
        if count > 3:
            try:
                self.c0 = float(tokens[3])
            except ValueError:
                raise GmxTopInstError('invalid c0', 'float', tokens[3])
        else:
            self.c0 = None
        if count > 4:
            try:
                self.c1 = float(tokens[4])
            except ValueError:
                raise GmxTopInstError('invalid c1', 'float', tokens[4])
        else:
            self.c1 = None
        if count > 5:
            try:
                self.c2 = float(tokens[5])
            except ValueError:
                raise GmxTopInstError('invalid c2', 'float', tokens[5])
        else:
            self.c2 = None
        if count > 6:
            try:
                self.c3 = float(tokens[6])
            except ValueError:
                raise GmxTopInstError('invalid c3', 'float', tokens[6])
        else:
            self.c3 = None

    def format_internal(self, aflen):
        format_str = '%' + str(aflen) + 'd %' + str(aflen) + 'd %5d'
        output = format_str % (self.ai, self.aj, self.funct)
        if self.c0 is not None:
            output += '  %e' % self.c0
        if self.c1 is not None:
            output += '  %e' % self.c1
        if self.c2 is not None:
            output += '  %e' % self.c2
        if self.c3 is not None:
            output += '  %e' % self.c3
        return output

    def get_atom_nrs(self):
        return [self.ai, self.aj]

    def set_atom_nrs(self, new_values):
        self.ai, self.aj = new_values

class GmxTopConstraint(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not (count >= 3 and count <= 5):
            raise GmxTopInstError('invalid column count', '3 to 5', \
                                     found = count)
        try:
            self.ai = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid ai', 'integer', tokens[0])
        try:
            self.aj = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid aj', 'integer', tokens[1])
        try:
            self.funct = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid funct', 'integer', tokens[2])
        if count > 3:
            try:
                self.c0 = float(tokens[3])
            except ValueError:
                raise GmxTopInstError('invalid c0', 'float', tokens[3])
        else:
            self.c0 = None
        if count > 4:
            try:
                self.c1 = float(tokens[4])
            except ValueError:
                raise GmxTopInstError('invalid c1', 'float', tokens[4])
        else:
            self.c1 = None

    def format_internal(self, aflen):
        format_str = '%' + str(aflen) + 'd %' + str(aflen) + 'd %5d'
        output = format_str % (self.ai, self.aj, self.funct)
        if self.c0 is not None:
            output += ' %e' % self.c0
        if self.c1 is not None:
            output += ' %e' % self.c1
        return output

    def get_atom_nrs(self):
        return [self.ai, self.aj]

    def set_atom_nrs(self, new_values):
        self.ai, self.aj = new_values

class GmxTopPair(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not (count >= 3 and count <= 8):
            raise GmxTopInstError('invalid column count', '3 to 8', \
                                     found = count)
        try:
            self.ai = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid ai', 'integer', tokens[0])
        try:
            self.aj = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid aj', 'integer', tokens[1])
        try:
            self.funct = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid funct', 'integer', tokens[2])
        if count > 3:
            try:
                self.c0 = float(tokens[3])
            except ValueError:
                raise GmxTopInstError('invalid c0', 'float', tokens[3])
        else:
            self.c0 = None
        if count > 4:
            try:
                self.c1 = float(tokens[4])
            except ValueError:
                raise GmxTopInstError('invalid c1', 'float', tokens[4])
        else:
            self.c1 = None
        if count > 5:
            try:
                self.c2 = float(tokens[5])
            except ValueError:
                raise GmxTopInstError('invalid c2', 'float', tokens[5])
        else:
            self.c2 = None
        if count > 6:
            try:
                self.c3 = float(tokens[6])
            except ValueError:
                raise GmxTopInstError('invalid c3', 'float', tokens[6])
        else:
            self.c3 = None
        if count > 7:
            try:
                self.c4 = float(tokens[7])
            except ValueError:
                raise GmxTopInstError('invalid c4', 'float', tokens[7])
        else:
            self.c4 = None

    def format_internal(self, aflen):
        format_str = '%' + str(aflen) + 'd %' + str(aflen) + 'd %5d'
        output = format_str % (self.ai, self.aj, self.funct)
        if self.c0 is not None:
            output += ' %e' % self.c0
        if self.c1 is not None:
            output += ' %e' % self.c1
        if self.c2 is not None:
            output += ' %e' % self.c2
        if self.c3 is not None:
            output += ' %e' % self.c3
        if self.c4 is not None:
            output += ' %e' % self.c4
        return output

    def get_atom_nrs(self):
        return [self.ai, self.aj]

    def set_atom_nrs(self, new_values):
        self.ai, self.aj = new_values

class GmxTopAngle(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not (count >= 4 and count <= 8):
            raise GmxTopInstError('invalid column count', '4 to 8', \
                                     found = count)
        try:
            self.ai = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid ai', 'integer', tokens[0])
        try:
            self.aj = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid aj', 'integer', tokens[1])
        try:
            self.ak = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid ak', 'integer', tokens[2])
        try:
            self.funct = int(tokens[3])
        except ValueError:
            raise GmxTopInstError('invalid funct', 'integer', tokens[3])
        if count > 4:
            try:
                self.c0 = float(tokens[4])
            except ValueError:
                raise GmxTopInstError('invalid c0', 'float', tokens[4])
        else:
            self.c0 = None
        if count > 5:
            try:
                self.c1 = float(tokens[5])
            except ValueError:
                raise GmxTopInstError('invalid c1', 'float', tokens[5])
        else:
            self.c1 = None
        if count > 6:
            try:
                self.c2 = float(tokens[6])
            except ValueError:
                raise GmxTopInstError('invalid c2', 'float', tokens[6])
        else:
            self.c2 = None
        if count > 7:
            try:
                self.c3 = float(tokens[7])
            except ValueError:
                raise GmxTopInstError('invalid c3', 'float', tokens[7])
        else:
            self.c3 = None

    def format_internal(self, aflen):
        format_str = '%' + str(aflen) + 'd %' + str(aflen) + 'd %' + \
                     str(aflen) + 'd %5d'
        output = format_str % (self.ai, self.aj, self.ak, self.funct)
        if self.c0 is not None:
            output += '  %e' % self.c0
        if self.c1 is not None:
            output += '  %e' % self.c1
        if self.c2 is not None:
            output += '  %e' % self.c2
        if self.c3 is not None:
            output += '  %e' % self.c3
        return output

    def get_atom_nrs(self):
        return [self.ai, self.aj, self.ak]

    def set_atom_nrs(self, new_values):
        self.ai, self.aj, self.ak = new_values

class GmxTopDihedral(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not (count >= 5 and count <= 11):
            raise GmxTopInstError('invalid column count', '5 to 11', \
                                     found = count)
        try:
            self.ai = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid ai', 'integer', tokens[0])
        try:
            self.aj = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid aj', 'integer', tokens[1])
        try:
            self.ak = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid ak', 'integer', tokens[2])
        try:
            self.al = int(tokens[3])
        except ValueError:
            raise GmxTopInstError('invalid al', 'integer', tokens[3])
        try:
            self.funct = int(tokens[4])
        except ValueError:
            raise GmxTopInstError('invalid funct', 'integer', tokens[4])
        if self.funct == 9:
            self.c0 = None
            self.c1 = None
            self.c2 = None
            self.c3 = None
            if count == 6:
                self.multi = tokens[5]
            elif count == 5:
                self.multi = None
            else:
                raise GmxTopInstError('invalid column count', '5 to 6', \
                                         count)
        else:
            self.multi = None
            if count > 5:
                try:
                    self.c0 = float(tokens[5])
                except ValueError:
                    raise GmxTopInstError('invalid c0', 'float', tokens[5])
            else:
                self.c0 = None
            if count > 6:
                try:
                    self.c1 = float(tokens[6])
                except ValueError:
                    raise GmxTopInstError('invalid c1', 'float', tokens[6])
            else:
                self.c1 = None
            if count > 7:
                try:
                    self.c2 = float(tokens[7])
                except ValueError:
                    raise GmxTopInstError('invalid c2', 'float', tokens[7])
            else:
                self.c2 = None
            if count > 8:
                try:
                    self.c3 = float(tokens[8])
                except ValueError:
                    raise GmxTopInstError('invalid c3', 'float', tokens[8])
            else:
                self.c3 = None
            if count > 9:
                try:
                    self.c4 = float(tokens[9])
                except ValueError:
                    raise GmxTopInstError('invalid c4', 'float', tokens[9])
            else:
                self.c4 = None
            if count > 10:
                try:
                    self.c5 = float(tokens[10])
                except ValueError:
                    raise GmxTopInstError('invalid c5', 'float', tokens[10])
            else:
                self.c5 = None

    def format_internal(self, aflen):
        format_str = '%' + str(aflen) + 'd %' + str(aflen) + 'd %' + \
                     str(aflen) + 'd %' + str(aflen) + 'd %5d'
        output = format_str % (self.ai, self.aj, self.ak, self.al, self.funct)
        if self.funct == 9:
            if self.multi is not None:
                output += '    ' + self.multi
        else:
            if self.c0 is not None:
                output += '  %e' % self.c0
            if self.c1 is not None:
                output += '  %e' % self.c1
            if self.c2 is not None:
                output += '  %e' % self.c2
            if self.c3 is not None:
                output += '  %e' % self.c3
            if self.c4 is not None:
                output += '  %e' % self.c4
            if self.c5 is not None:
                output += '  %e' % self.c5
        return output

    def get_atom_nrs(self):
        return [self.ai, self.aj, self.ak, self.al]

    def set_atom_nrs(self, new_values):
        self.ai, self.aj, self.ak, self.al = new_values

class GmxTopVirtualSite3(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not (count >= 5 and count <= 8):
            raise GmxTopInstError('invalid number of columns', '5 to 8', \
                                     found = count)
        try:
            self.ai = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid ai', 'integer', tokens[0])
        try:
            self.aj = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid aj', 'integer', tokens[1])
        try:
            self.ak = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid ak', 'integer', tokens[2])
        try:
            self.al = int(tokens[3])
        except ValueError:
            raise GmxTopInstError('invalid al', 'integer', tokens[3])
        try:
            self.funct = int(tokens[4])
        except ValueError:
            raise GmxTopInstError('invalid funct', 'integer', tokens[4])
        self.c0 = None
        self.c1 = None
        self.c2 = None
        if count > 5:
            try:
                self.c0 = float(tokens[5])
            except ValueError:
                raise GmxTopInstError('invalid c0', 'float', tokens[5])
        if count > 6:
            try:
                self.c1 = float(tokens[6])
            except ValueError:
                raise GmxTopInstError('invalid c1', 'float', tokens[6])
        if count > 7:
            try:
                self.c2 = float(tokens[7])
            except ValueError:
                raise GmxTopInstError('invalid c2', 'float', tokens[7])

    def format_internal(self, aflen):
        format_str = '%' + str(aflen) + 'd %' + str(aflen) + 'd %' \
                     + str(aflen) + 'd %' + str(aflen) + 'd %5d'
        output = format_str % (self.ai, self.aj, self.ak, self.al, self.funct)
        if self.c0 is not None:
            output += ' %e' % self.c0
        if self.c1 is not None:
            output += ' %e' % self.c1
        if self.c2 is not None:
            output += ' %e' % self.c2
        return output

    def get_atom_nrs(self):
        return [self.ai, self.aj, self.ak, self.al]

    def set_atom_nrs(self, new_values):
        self.ai, self.aj, self.ak, self.al = new_values

class GmxTopVirtualSite4(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not (count >= 6 and count <= 9):
            raise GmxTopInstError('invalid number of columns', '6 to 9', \
                                     found = count)
        try:
            self.ai = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid ai', 'integer', tokens[0])
        try:
            self.aj = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid aj', 'integer', tokens[1])
        try:
            self.ak = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid ak', 'integer', tokens[2])
        try:
            self.al = int(tokens[3])
        except ValueError:
            raise GmxTopInstError('invalid al', 'integer', tokens[3])
        try:
            self.am = int(tokens[4])
        except ValueError:
            raise GmxTopInstError('invalid am', 'integer', tokens[4])
        try:
            self.funct = int(tokens[5])
        except ValueError:
            raise GmxTopInstError('invalid funct', 'integer', tokens[5])
        self.c0 = None
        self.c1 = None
        self.c2 = None
        if count > 6:
            try:
                self.c0 = float(tokens[6])
            except ValueError:
                raise GmxTopInstError('invalid c0', 'float', tokens[6])
        if count > 7:
            try:
                self.c1 = float(tokens[7])
            except ValueError:
                raise GmxTopInstError('invalid c1', 'float', tokens[7])
        if count > 8:
            try:
                self.c2 = float(tokens[7])
            except ValueError:
                raise GmxTopInstError('invalid c2', 'float', tokens[8])

    def format_internal(self, aflen):
        format_str = '%' + str(aflen) + 'd %' + str(aflen) + 'd %' \
                     + str(aflen) + 'd %' + str(aflen) + 'd %' + str(aflen) + \
                     'd %5d'
        output = format_str % (self.ai, self.aj, self.ak, self.al, self.am, \
                               self.funct)
        if self.c0 is not None:
            output += ' %e' % self.c0
        if self.c1 is not None:
            output += ' %e' % self.c1
        if self.c2 is not None:
            output += ' %e' % self.c2
        return output

    def get_atom_nrs(self):
        return [self.ai, self.aj, self.ak, self.al, self.am]

    def set_atom_nrs(self, new_values):
        self.ai, self.aj, self.ak, self.al, self.am = new_values

class GmxTopPositionRestraint(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if count != 5:
            raise GmxTopInstError('invalid number of columns', 5, \
                                     found = count)
        try:
            self.i = int(tokens[0])
        except ValueError:
            raise GmxTopInstError('invalid i', 'integer', tokens[0])
        try:
            self.funct = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid funct', 'integer', tokens[1])
        try:
            self.fcx = int(tokens[2])
        except ValueError:
            raise GmxTopInstError('invalid fcx', 'integer', tokens[2])
        try:
            self.fcy = int(tokens[3])
        except ValueError:
            raise GmxTopInstError('invalid fcy', 'integer', tokens[3])
        try:
            self.fcz = int(tokens[4])
        except ValueError:
            raise GmxTopInstError('invalid fcz', 'integer', tokens[4])

    def format_internal(self, aflen):
        return '%4d %4d %10d %10d %10d' % (self.i, self.funct, self.fcx, \
                                           self.fcy, self.fcz)

    def get_atom_nrs(self):
        return [self.i]

    def set_atom_nrs(self, new_values):
        self.i = new_values[0]

class GmxTopSystem(GmxTopInst):

    def parse(self, inst):
        self.inst = inst

    def format_internal(self, aflen):
        return self.inst

class GmxTopMolecule(GmxTopInst):

    def parse(self, inst):
        tokens = inst.split()
        count = len(tokens)
        if not count == 2:
            raise GmxTopInstError('invalid column count', 2, found = count)
        self.name = tokens[0]
        try:
            self.nmols = int(tokens[1])
        except ValueError:
            raise GmxTopInstError('invalid nmols', 'integer', tokens[1])

    def format_internal(self, aflen):
        return '%-17s %d' % (self.name, self.nmols)

header_strings = {'defaults': GmxTopDefaults, \
                  'atomtypes': GmxTopAtomType, \
                  'moleculetype': GmxTopMoleculeType, \
                  'atoms': GmxTopAtom, \
                  'bonds': GmxTopBond, \
                  'constraints': GmxTopConstraint, \
                  'pairs': GmxTopPair, \
                  'angles': GmxTopAngle, \
                  'dihedrals': GmxTopDihedral, \
                  'virtual_sites3': GmxTopVirtualSite3, \
                  'virtual_sites4': GmxTopVirtualSite4, \
                  'position_restraints': GmxTopPositionRestraint, \
                  'system': GmxTopSystem, \
                  'molecules': GmxTopMolecule}

def read(infile):

    if isinstance(infile, str):
        infile = open(infile)

    topology = []
    section = None
    inst_type = None

    for i, line in enumerate(infile):
        sline = line.strip()
        if len(sline) == 0 or sline[0] in '#;':
            inst = GmxTopComment(line)
        elif sline.startswith('['):
            try:
                inst = GmxTopHeader(line)
            except GmxTopInstError as e:
                raise GmxTopGlobalError(i+1, 'header', str(e))
            section = inst.title
            try:
                inst_type = header_strings[section]
            except KeyError:
                raise GmxTopGlobalError(i+1, None, \
                        'unexpected header "%s"' % section)
        else:
            if section:
                try:
                    inst = inst_type(line)
                except GmxGmxTopInstError as e:
                    raise GmxTopGlobalError(i+1, section, str(e))
            else:
                raise GmxTopGlobalError(i+1, None, 'unexpected instruction')
        topology.append(inst)

    return topology

def write(topology, outfile):

    if isinstance(outfile, str):
        outfile = open(outfile, 'w')

    natoms = len([inst for inst in topology if isinstance(inst, GmxTopAtom)])
    aflen = len(str(natoms))
    if aflen < 5:
        aflen = 5

    for inst in topology:
        outfile.write(inst.format(aflen))
