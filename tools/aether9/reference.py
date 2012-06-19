"""
reference.Factory
"""

class Factory:
	def __init__(self, doc, base):
		self.base = base
		self.doc = doc
		doctype = doc['type']
		sub = getattr(self, doctype)
		sub()
		
	def mail(self):
		# test with author name
		aname = self.doc['author']
		self.doc['ref'] = {'author':[]}
		for m in self.base:
			if m['type'] == 'mail':
				if m['author'] == aname:
					self.doc['ref']['author'].append('mail:%d' % m['id'])
	