types = {'mail': 'karla'}
roads = ['slow', 'chat', 'patch','red','network','cash','science','themes','performers','tech']

for type in types:
	for road in roads:
		print '\def\styleref%s%s#1%%' % (type,road)
		print '{'
		print '\t{'
		print '\t\t\crim%s #1' % (road)
		print '\t}'
		print '}'