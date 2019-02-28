#!/usr/bin/env python3

import argparse, os, re, itertools, tempfile
def parseArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("-m", "--mrfile", help="MR file",   type=str,
		default=None)
	parser.add_argument("-p", "--pdbfile", help="PDB file with correct GROMACS atom numbering.", type=str,
		default=None)
	parser.add_argument("-o", "--itpfile", help="ITP file", type=str,
		default="mr.itp")

	args = parser.parse_args()
	return args

class AtomNomTable:
	def __init__(self):
		gmxdata = os.environ["GMXDATA"]
		if not gmxdata:
			print("Please source a suitable GROMACS installation")
			exit(1)
		# tbl = open(gmxdata + "/top/atom_nom.tbl", "r")
		tbl = open("atom_nom.tbl", "r")
		self.table = []
		for line in tbl:
			if line.find("@") < 0:
				words = line.split()
				if len(words) == 4:
					self.table.append([words[0], words[1], words[2], words[3]])
		self.table.sort(key=lambda x: (x[0], x[1]))
		tbl.close()

	def lookup(self, resnm, atomnm):
		list_nm = []
		for t in self.table:
			if t[0] == resnm and t[1] == atomnm:
				list_nm.append(t[3])
		return list_nm


class MyAtom:
	def __init__(self, line):
		self.atomnr = int(line[7:11])
		self.atomnm = line[11:16].strip()
		self.resnm  = line[16:21].strip()
		self.resid  = int(line[22:26])

	def print(self):
		print("%d %s %s %d" % ( self.atomnr, self.atomnm, 
								self.resnm, self.resid ) )


class MyPdb:
	def __init__(self, filenm):
		fn = open(filenm, "r")
		self.pdb_atoms = []
		for line in fn:
			if line.find("ATOM") == 0 or line.find("HETATM") == 0:
				ma = MyAtom(line)
				self.pdb_atoms.append(ma)
#                ma.print()
		fn.close()
		
	def atoms(self):
		return self.pdb_atoms



def lookup_atomid(resid, atom, pdb, an_tab):
	for p in pdb.atoms():		        
		if (p.resid == resid):
			atomx = an_tab.lookup(p.resnm, atom)
			if p.atomnm == atomx[0]:
				if len(atomx) == 1:
					return [p.atomnr]
				else:      
					return list(range(p.atomnr, p.atomnr+len(atomx)))

	print("Can not find resid %d atom %s" % ( resid, atom ))
	exit(1)

def distance_restraints(line):
	junk_keywords = ["!", "*", "#"]
	atom_keywords = ['name', 'atomnm']
	restraints = []
	line = line
	line = line[0]
	line = line[-1]
#	print("line_disre:", line)
	line = line.split('|')
	for i, words in enumerate(line):
		if any(n in words for n in atom_keywords) == True:
			restraints.append(line[i+2:])
	dd = 0.1*float(restraints[0][0])
	dm = 0.1*float(restraints[0][1])
	dp = 0.1*float(restraints[0][2])
	low = dd - dm
	high1 = dd + dp
	high2 = high1 + 1
	restraints = [low, high1, high2]
	return restraints
	
class Noe:
	def __init__(self, line):
		atom_keywords = ['name', 'atomnm']
		res_keywords = ['resi', 'resid']
		replace = ["((", "))", "(", ")"]
		lresidueID = []
		latom = []
		rresidueID = []
		ratom = []
		separator = []
		final_line = []
		indices = []
		lefthand = []
		righthand = []
		final = []
		for ch in replace:
			if ch in line:
				line = line.replace(ch, '')

		test = line.split()
		for i, words in enumerate(test):
			if any(n in words for n in res_keywords) == True:
				indices.append(i)
		indices.append(len(test))
		for i,x in enumerate(indices):
			if i < (len(indices)-1): 
				part = '|'.join(test[indices[i]:indices[i+1]])
				separator.append(part)
				i+=1
		for o, elements in enumerate(separator):
			if separator[o].find('or') == -1 and o < (len(separator)-1):
				lefthand.append(separator[:o+1])
				righthand.append(separator[o+1:])
	#	print("righthand:", righthand)
		dis_res = distance_restraints(righthand)
	#	print("after_distance:", dis_res)
		lefthand = '|'.join(lefthand[0])
		lefthand = lefthand.split('|')
		for i, words in enumerate(lefthand):
			if any(r in words for r in res_keywords) == True:
				lresidueID.append(lefthand[i+1])
			if any(a in words for a in atom_keywords) == True:
				latom.append(lefthand[i+1])

		lfinal_line = map(' '.join,zip(lresidueID, latom))

		righthand = '|'.join(righthand[0])
		righthand = righthand.split('|')
		for i, words in enumerate(righthand):
			if any(r in words for r in res_keywords) == True:
				rresidueID.append(righthand[i+1])
			if any(a in words for a in atom_keywords) == True:
				ratom.append(righthand[i+1])
		rfinal_line = map(' '.join,zip(rresidueID, ratom))
		final = list(itertools.product(lfinal_line, rfinal_line))
		final.extend(dis_res)
	#	print("final:", final)
		line = final[:-3]
	#	print("line:", line)
		for ii in range(0, len(line)):
			y = list(line[ii])
			rall = y[0].split()
		#	print("rall:", rall)
			ralr = y[1].split()
		#	print("ralr:", ralr)
			ai = lookup_atomid(int(rall[0]), rall[1], pdb_atoms, an_tab)
			print("ai:", ai)
			aj = lookup_atomid(int(ralr[0]), ralr[1], pdb_atoms, an_tab) 
			print("aj:", aj)
			for i in range(0, len(ai)):
			#	print("i:", i)
			#	print("dis`-res:", dis_res)
				for j in range(0, len(aj)):
			#		print("j:", j)
					temp = {}
			#		print("ai[i]:", ai[i])
			#		print("aj[j]:", aj[j])
					aii = min(ai[i], aj[j])
					ajj = max(ai[i], aj[j])
			#		print(aii, ajj)
						
			#		print(dis_res[0], dis_res[1], dis_res[2])
					temp[aii, ajj] = [1, 1,dis_res[0], dis_res[1], dis_res[2], 1.0]
					print("temp:", temp)
					dictionary.update(temp)



atom_keywords = ['name', 'atomnm']
atomsNOE = ['H','h']
atomsDihedral = ['C', 'N', 'c', 'n']

def check_cat_type1(line):
	c = 0
	a = 0
	text = line.split()
#	r = re.find('or')
	for i, words in enumerate(text):
		if any(r in words for r in atom_keywords) == True:
			a+=1
		if any(n in words for n in atom_keywords) == True:
			z = list(text[i+1])
	#		print("z:", z)
			if any(h in z[0] for h in atomsNOE) == True:
				c+=1
	if c == a:
		return True

def check_cat_type2(line):
	c = 0
	a = 0
	text = line.split()
	for i, words in enumerate(text):
		if any(r in words for r in atom_keywords) == True:
			a+=1
		if any(n in words for n in atom_keywords) == True:
			z = list(text[i+1])
			if any(h in z[0] for h in atomsDihedral) == True:
				c+=1
	if c == a:
		return True
	

def check_cat_type3(line):
	return False
	
						  
def read_noe(filenm):
	junk_keywords = ["!", "*", "#"]
	assign_keywords = ["assi", "ASSIGN", "assign"]
	res_keywords = ['resid', 'resi']
	atom_keywords = ['name', 'atomnm']
	noe_list = []
	with tempfile.TemporaryFile('r+') as tmp:
		with open(filenm, 'r') as fn:
			for lines in fn:
				if any(x in lines[:6] for x in junk_keywords) == True:
					continue
				if any(x in lines for x in assign_keywords) == True or (any(x in lines for x in res_keywords) == True and any(x in lines for x in atom_keywords) == True):
					tmp.writelines(lines,)
			tmp.writelines('assign')	
		tmp.seek(0)
		line = tmp.readlines()
		i=-1
		newline = ""
		try:
			while i <= (len(line)+2):
				i = i+1
				if any(x in line[i] for x in assign_keywords) == True:
					newline = line[i].strip()
					while any(x in line[i+1] for x in assign_keywords) == False:
						i = i+1
						newline = newline + ' ' + line[i].strip()
			
				if newline != "":
					if check_cat_type1(newline) == True:					
						#	print chl.process_type1(newline)
				#		print(newline)
						noe_list.append(Noe(newline))
				#	elif check_cat_type2(newline) == True:
				#		process_type2(newline)
				#	elif check_cat_type3(newline) == True:
				#		process_type3(newline)
					else:
						print("Line is not classified")
		except (IndexError) as e:
			print(e) 
#
#	*this is where the MRFILE.py will go 
#	*
#	*
#	*
#	*
#	*
#	*
#	*result is a directly processed file
#	print("noelist:", noe_list)
	return noe_list
	
# Here the fun starts    
if __name__ == '__main__':
	args  = parseArguments()

	if args.mrfile and args.pdbfile:
		dictionary = {}
		an_tab    = AtomNomTable()
		pdb_atoms = MyPdb(args.pdbfile)
		noe_list  = read_noe(args.mrfile)
		itp = open(args.itpfile, "w")
		print(len(noe_list))
		print("ITP FILE OPENED")
		itp.write(" [ distance_restraints ]\n")
		itp.write("; Read an xplor distance restraint file %s\n" % (args.mrfile))
		itp.write("; %s was for the atom numbers\n" % (args.pdbfile))
		index = 0
		key_prev=0
#		for i in range(0, len(noe_list)):
#			print(noe_list[i])
#		for n in noe_list:
#			n.print(itp, pdb_atoms, an_tab, dictionary )
		for keys, values in sorted(dictionary.items()):
			# if key_prev != keys[0]:
			#     key_prev = keys[0]
			itp.write("%5d %5d  %1d %1d %1d %f %f  %f %f\n" % (keys[0], keys[1], values[0], index, values[1],values[2],values[3],values[4],values[5]) )
			index = index + 1
		itp.close()
