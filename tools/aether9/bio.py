"""
bio.Reader
bio.Writer
"""

import os.path as opath
import re
import time

class FileDoesNotExist(Exception):
	def __init__(self, fname):
		self.filename = fname
	def __str__(self):
		return '%s does not exist'%(self.filename)

class Reader:
	bio_sep_pattern = r'\n\n'
	line_sep_pattern = r'\n'
	infos_sep_pattern = r':\s+'
	included_fields = ['name', 'nick', 'bio', 'url']

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
		self.data['bios'] = []
		
		if data_str:
			data = re.split(self.bio_sep_pattern, data_str, flags=re.MULTILINE)
			
			for bloc in data:
				self.process_bloc(bloc.strip())
				
	def process_bloc(self, bloc):
		bio = {'type': 'bio'}
		for line in re.split (self.line_sep_pattern, bloc, flags=re.MULTILINE):
			parts = re.split (self.infos_sep_pattern, line)
			
			if parts[0].lower() in self.included_fields:
				bio[parts[0].lower()] = parts[1]
				
		bio['bio_text'] = bio['bio']
		
		self.data['bios'].append(bio)
		
class Writer:
	tex_special_chars = {r'&': '\\&', r'%': '\\%', r'$': '\\$', r'#': '\\#', r'_': '\\_', r'{': '\\{', r'}': '\\}', r'~': '\\textasciitilde{}', r'^': '\\textasciicircum{}', '\\' : '\\textbackslash{}', '|':'\\textbar{}'}
	et_pat = '[%s]'%(re.escape(''.join(tex_special_chars.keys())),)
	def __init__(self, bdict):
		self.bio = bdict
		
	def as_string(self):
		aref = []
		#for r in self.ref['author']:
			#aref.append('\\in{section}[%s](p.\\at{page}[%s])'%(r,r))
		#	aref.append('%s.%s'%('\\ref[p]['+r+']', r.split(':')[-1]))
		
		ret = []
		ret.append('\\stylepiece')
		#ret.append('%d'%self.id)
		ret.append('\\styleinfos')
		ret.append('%s\n\n%s'%(self.name, self.nick))
		ret.append('\\stylebio')
		ret.append(self.bio_text)
		return '\n'.join(ret)
		
	def escape_tex(self, pt):
		r = pt.group()
		#print('matched: %s'%r)
		if r in self.tex_special_chars:
			return self.tex_special_chars[r]
		return r
			
		
	def __getattr__(self, name):
		try:
			return re.sub(et_pat, getattr(self, 'escape_tex'), self.bio[name])
		except Exception:
			try:
				return self.bio[name]
			except Exception:
				raise AttributeError(name)
		
if __name__ == '__main__':
	reader = Reader ('../../TEXT_FILES/biographies.txt')
	print Writer (reader.data['bios'][0]).as_string()