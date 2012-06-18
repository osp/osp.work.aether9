"""
mail.Writer
"""


class Writer:
	def __init__(self, mdict):
		self.mail = mdict
		
	def as_string(self):
		ret = []
		ret.append('\\phantomsection')
		ret.append('\\label{mail:%s}'%(self.id,))
		ret.append('\\bf{%s}'%(self.title,))
		ret.append('\\it{%s}'%(self.author,))
		ret.append(self.text)
		return '\n'.join(ret)
		
	def __getattr__(self, name):
		try:
			return self.mail[name]
		except Exception:
			raise AttributeError(name)