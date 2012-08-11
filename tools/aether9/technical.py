"""
technical.Reader
technical.Writer
"""

import mail
import re

class Reader (mail.Reader):
	type = 'technical'
	
	def __init__ (self, fname):
		mail.Reader.__init__ (self, fname)
		mail.Reader.type = 'technical'
	
class Writer (mail.Writer):
	type = 'technical'
	
	def __init__ (self, fname):
		mail.Writer.__init__ (self, fname)
		mail.Writer.type = 'technical'
		
	def as_string(self):
		esc_text = self.text
		if 'tex_escaped' not in self.mail:
			esc_text = self.escape_tex(self.text)
		
		ret = []
		
		
		ret.append('\\stylepiece{%d}'%self.id)
		ret.append('\\stylemailtitle')
		ret.append(self.title)
		ret.append('\\styleinfos')
		ret.append('%s\n\n%s'%( self.author, self.date.strftime('%d.%m.%Y') ))
		ret.append('\\stylemail')
		ret.append(esc_text)
		return '\n\n'.join(ret)