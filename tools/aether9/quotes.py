"""
quotes.Reader
quotes.Writer
"""

import os.path as opath
import re
from datetime import datetime

class FileDoesNotExist(Exception):
	def __init__(self, fname):
		self.filename = fname
	def __str__(self):
		return '%s does not exist'%(self.filename)

class Reader:
	quotes_sep_pattern = '\n---\n'
	infos_sep_pattern = r':'
	content_sep_pattern = r'QUOTE:'

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
		self.data['quotes'] = []
		
		if data_str:
			data = re.split('---', data_str, flags=re.MULTILINE)
			
			for bloc in data:
				self.process_bloc(bloc.strip())
				
	def process_bloc(self, bloc):
		#lines = bloc.splitlines()
		tmpa_ = bloc.split('QUOTE:')
		tmp_b = tmpa_[0]
		head = tmp_b.splitlines()


		author_a = head[0].split(':')
		date_str = head[1].split(':')[1].strip()
		author = None
		if len(author_a) > 0:
			author = author_a[1].strip()
		
		date = datetime.strptime(date_str, '%Y-%m-%d')
		
		content = tmpa_[1]
		self.data['quotes'].append({'type':'quotes', 'author':author, 'date': date, 'text':content})
		
		
		
		
class Writer:
	tex_special_chars = {r'&': '\\&', r'%': '\\%', r'$': '\\$', r'#': '\\#', r'_': '\\_', r'{': '\\{', r'}': '\\}', r'~': '\\textasciitilde{}', r'^': '\\textasciicircum{}', '\\' : '\\textbackslash{}', '|':'\\textbar{}'}
	def __init__(self, mdict):
		self.mail = mdict
		
	def as_string(self):
		et_pat = '[%s]'%(re.escape(''.join(self.tex_special_chars.keys())),)
		esc_text = re.sub(et_pat, getattr(self, 'escape_tex') , self.text)
		aref = []
		#for r in self.ref['author']:
			#aref.append('\\in{section}[%s](p.\\at{page}[%s])'%(r,r))
		#	aref.append('%s.%s'%('\\ref[p]['+r+']', r.split(':')[-1]))
		
		ret = []
		ret.append('\\startcolumnsetspan[wide]')
		ret.append('\\stylepiece')
		ret.append('%d'%self.id)
		ret.append('\\styleinfos')
		ret.append('%s'%( self.author))
		ret.append('\\stylequote')
		ret.append(esc_text)
		ret.append('\\stopcolumnsetspan')
		return '\n\n'.join(ret)
		
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
		