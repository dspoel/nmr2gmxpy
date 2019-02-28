l1 = [['A', '12'], 'or', ['B', '10'], ['C', '15']]
l2 = [['A', '12'],  ['B', '10'], 'or', ['C', '15']]
l3 = [['A', '12'], 'or', ['B', '10'], 'or', ['C', '15'], ['D', '16']]
l4 = [['A', '12'], ['B', '10'], 'or', ['C', '15'], 'or', ['D', '16']]
l5 = [['A', '12'], ['B', '10'], 'or', ['C', '15'],  ['D', '16']]
# l1 = "A or B C"
# l2= "A B or C"
# l3 = "A or B or C D"
# l4 = "A B or C or D"
# l5 = "A B or C D or E F or G H"

def makePairs( words ):
	pairs = []
	firstAtom = ""
	secondAtoms = []
	# words = line.split()
	for i in range( len(words) ):
		w = words[i]
		isLastWord = i == len(words)-1
		if w != 'or':
			if (not isLastWord) and (words[i+1] != 'or'):
				pairs.append([w,words[i+1]])

			if ((not isLastWord) and (words[i+1] == 'or')) or (i > 0 and words[i-1] == 'or'):
				secondAtoms.append(w)
			else:
				firstAtom = w
					

	if len(pairs) > 1:
		return pairs

	pairs = []
	# print secondAtoms
	# print firstAtoms
	for a in secondAtoms:
		pairs.append( [firstAtom, a] )

	return pairs

if __name__ == '__main__':
	print "l1", makePairs(l1)
	print "l2", makePairs(l2)
	print "l3", makePairs(l3)
	print "l4", makePairs(l4)
	print "l5", makePairs(l5)