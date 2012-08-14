types = {'mail': 'crimbase', 'general': 'crimbase', 'technical': 'consolbase', 'quotes': 'crimbig', 'piece': 'kafat', 'perfo': 'kabase', 'infos': 'kasmall', 'chatlog': 'kabase', 'bio': 'consolbase'}
roads = ['slow', 'chat', 'patch','red','network','cash','science','themes','performers','tech']

for type, font in types.items():
	for road in roads:
		if road == 'performers':
			print '\def\styleref%s%s#1%%' % (type,road)
			#print '{'
			print '{{\cap{\%s#1}}}' % (font)
			#print '}'
		else:
			print '\def\styleref%s%s#1%%' % (type,road)
			#print '{'
			print '{{\%s%s #1}}' % (font, road)
			#print '}'