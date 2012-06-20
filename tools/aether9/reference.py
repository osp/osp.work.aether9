"""
reference.Factory
"""

class FileDoesNotExist(Exception):
	def __init__(self, fname):
		self.filename = fname
	def __str__(self):
		return '%s does not exist'%(self.filename)


class Factory:
	def __init__(self, root_dir, base):
		self.base = base
		
	def get_kw_lists(self, rd):
		pass
		
	#def mail(self):
		## test with author name
		#aname = self.doc['author']
		#self.doc['ref'] = {'author':[]}
		#for m in self.base:
			#if m['type'] == 'mail' and not m['id'] == self.doc['id']:
				#if m['author'] == aname:
					#self.doc['ref']['author'].append('mail:%d' % m['id'])
	