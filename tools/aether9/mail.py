"""
mail.Reader
mail.Writer
"""

import os.path as opath
import re
import time
import datetime

class FileDoesNotExist(Exception):
	def __init__(self, fname):
		self.filename = fname
	def __str__(self):
		return '%s does not exist'%(self.filename)

class Reader:
	start_pattern = r'^\[aether\]'
	end_header_pattern = r'^Messages sorted by'
	address_sep_pattern = r' at '
	
	def __init__(self, filename):
		if not opath.exists(filename):
			raise FileDoesNotExist(filename)
		data_str = False
		try:
			f = open(filename)
			data_str = f.read()
		except IOError:
			print 'Cannot open %s: expect missing data'%(filename,)
		except Exception as e:
			print 'Unhandle exception: %s'%(e,)
		finally:
			f.close()
		
		self.data = {}
		self.data['thread'] = []
		
		if data_str:
			data = re.split(self.start_pattern, data_str, flags=re.MULTILINE)
			#print('Got %d pieces off data_str with sp(%s)'%(len(data),self.start_pattern))
			for piece in data:
				self.process_piece(piece)
				
	def process_piece(self, piece):
		lines = piece.splitlines()
		#print('Got %d lines off piece'%(len(lines),))
		#print('==============================================\n%s\n'%(piece,))
		if len(lines) < 4:
			#raise Exception('Not enough pieces')
			return
		# l0 => title
		# l1 => author
		# l2 => date
		# ... until "Message sorted by" pattern
		# +1 the message!
		
		title = lines.pop(0).strip()
		author = lines.pop(0).split(self.address_sep_pattern)[0]
		date_str = lines.pop(0).strip()
		date = time.gmtime()
		try:
			date = datetime.datetime.strptime(date_str, '%a %b %d %H:%M:%S %Z %Y')
		except Exception:
			print('Failed to build date with "%s"'%(date_str,))
			raise
		for l in lines:
			if re.match(self.end_header_pattern, l):
				lines.pop(0)
				lines.pop(0) # ??
				break
			else:
				lines.pop(0)
				
		text = '\n'.join(lines)
		self.data['thread'].append({'type':'mail', 'title':title, 'author':author, 'date': date, 'text':text})
		
		
		
		
class Writer:
	tex_special_chars = {r'&': '\\&', r'%': '\\%', r'$': '\\$', r'#': '\\#', r'_': '\\_', r'{': '\\{', r'}': '\\}', r'~': '\\textasciitilde{}', r'^': '\\textasciicircum{}', '\\' : '\\textbackslash{}', '|':'\\textbar{}'}
	def __init__(self, mdict):
		self.mail = mdict
		
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
		#ret.append('\\section[mail:%d]{%d}{%s}{'%(self.id,self.id,self.title))
		#ret.append('\\startinfos %s --- %s\n\\stopinfos\n'%(self.author, self.date.strftime('%d.%m.%Y')))
		#ret.append('\\startmail %s\\stopmail\n'%(esc_text,))
		#ret.append('}')
		ret.append('\\startpiece')
		ret.append('%d'%self.id)
		ret.append('\\stoppiece')
		ret.append('\\startmailtitle')
		ret.append(self.title)
		ret.append('\\stopmailtitle')
		ret.append('\\startinfos')
		ret.append('%s\n\n%s'%( self.author, self.date.strftime('%d.%m.%Y') ))
		ret.append('\\stopinfos')
		ret.append('\\startmail')
		ret.append(esc_text)
		ret.append('\\stopmail')
		return '\n'.join(ret)
		
	def escape_tex(self, pt):
		r = pt.group()
		#print('matched: %s'%r)
		if r in self.tex_special_chars:
			return self.tex_special_chars[r]
		return r
			
		
	def __getattr__(self, name):
		try:
			return self.mail[name]
		except Exception:
			raise AttributeError(name)
		