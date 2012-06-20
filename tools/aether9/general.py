import mail
import re

class Reader (mail.Reader):
	type = 'general'
	
	def __init__ (self, fname):
		mail.Reader.__init__ (self, fname)
		mail.Reader.type = 'general'
	
class Writer (mail.Writer):
	def __init__ (self, fname):
		mail.Writer.__init__ (self, fname)
		mail.Writer.type = 'general'
		self.type = 'general'
		
	def as_string(self):
		et_pat = '[%s]'%(re.escape(''.join(self.tex_special_chars.keys())),)
		esc_text = re.sub(et_pat, getattr(self, 'escape_tex') , self.text)
		aref = []
		try:
			for r in self.ref['author']:
				#aref.append('\\in{section}[%s](p.\\at{page}[%s])'%(r,r))
				aref.append('\n%s.%s'%('\\ref[p]['+r+']', r.split(':')[-1]))
		except:
			pass
		
		ret = []
		
		ret.append('\\startpiece')
		ret.append('%d'%self.id)
		ret.append('\\stoppiece')
		ret.append('\\startgeneraltitle')
		ret.append(self.title)
		ret.append('\\stopgeneraltitle')
		ret.append('\\startinfos')
		ret.append('%s\n\n%s'%( self.author, self.date.strftime('%d.%m.%Y') ))
		ret.append('\\stopinfos')
		ret.append('\\startgeneral')
		ret.append(esc_text)
		ret.append('\\stopgeneral')
		return '\n'.join(ret)