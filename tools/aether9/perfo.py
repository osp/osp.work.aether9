"""
perfo.Reader
perfo.Writer
"""

import os.path as opath
import re
import time
from datetime import datetime

class FileDoesNotExist(Exception):
	def __init__(self, fname):
		self.filename = fname
	def __str__(self):
		return '%s does not exist'%(self.filename)

class NoDate(Exception):
	def __init__(self, fname):
		self.filename = fname
	def __str__(self):
		return '%s does not provide any date info'%(self.filename)		
		
class Reader:
	performance_sep_pattern = r'\n---\n'
	line_sep_pattern = r'\n'
	infos_sep_pattern = r':\s+'
	included_fields = ['title', 'description', 'performers', 'duration', 'date', 'time', 'event', 'location']

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
		self.data['perfos'] = []
		
		if data_str:
			data = re.split(self.performance_sep_pattern, data_str, flags=re.MULTILINE)
			
			for bloc in data:
				self.process_bloc(bloc.strip())
				
	def process_bloc(self, bloc):
		perfo = {'type': 'perfo'}
		for line in re.split (self.line_sep_pattern, bloc, flags=re.MULTILINE):
			parts = re.split (self.infos_sep_pattern, line)
			
			if parts[0].lower() in self.included_fields:
				perfo[parts[0].lower()] = parts[1].strip()

		time = None
		
		if 'time' in perfo:
			time = re.search ('\d{2}:\d{2}', perfo['time'])
		
		if time <> None:
			perfo['date'] = datetime.strptime ('%s %s' % (perfo['date'], time.group(0)), '%m %d, %Y %H:%M')
			del perfo['time']
		else:
			try:
				perfo['date'] = datetime.strptime (perfo['date'], '%m %d, %Y')
				del perfo['time']
			except Exception as e:
				raise NoDate (e)
			
		if 'performers' in perfo:
			perfo['seperate_performers'] = map(lambda performer: performer.strip(), perfo['performers'].split (','))
		
		# If we transform to uppercase in the writer we also uppercase the tex commands.
		if 'description' in perfo:
			perfo['description'] = perfo['description'].upper()
		
		self.data['perfos'].append(perfo)
		
class Writer:
	tex_special_chars = {r'&': '\\&', r'%': '\\%', r'$': '\\$', r'#': '\\#', r'_': '\\_', r'{': '\\{', r'}': '\\}', r'~': '\\textasciitilde{}', r'^': '\\textasciicircum{}', '\\' : '\\textbackslash{}', '|':'\\textbar{}'}
	et_pat = '[%s]'%(re.escape(''.join(tex_special_chars.keys())),)
	def __init__(self, pdict):
		self.perfo = pdict
		
	def as_string(self):
		aref = []
		#for r in self.ref['author']:
			#aref.append('\\in{section}[%s](p.\\at{page}[%s])'%(r,r))
		#	aref.append('%s.%s'%('\\ref[p]['+r+']', r.split(':')[-1]))
		
		ret = []
		ret.append('\\stylepiece{%d}'%self.id)
		ret.append('')
		ret.append('\\styleinfos')
		ret.append('\\startinfopar \perfotitle{%s}\n\n\\infopar %s\n\n\\infopar %s\n\n\\infopar %s\n\n\\infopar %s\\stopinfopar'%(self.title,self.date,self.event,self.location,'\n'.join(self.performers.split())))
		ret.append('\\blackrule[color=black, width=65mm, height=0.5pt, depth=0mm]')
		ret.append('\\styleperfo')
		ret.append(self.description)
		ret.append('\\blackrule[color=black, width=65mm, height=0.5pt, depth=0mm]')
		#ret.append('\\stopcolumnsetspan')
		return '%s' % '\n'.join(ret)
		
	def escape_tex(self, pt):
		r = pt.group()
		#print('matched: %s'%r)
		if r in self.tex_special_chars:
			return self.tex_special_chars[r]
		return r
			
		
	def __getattr__(self, name):
		try:
			return re.sub(et_pat, getattr(self, 'escape_tex'), self.perfo[name])
		except Exception:
			try:
				return self.perfo[name]
			except Exception:
				raise AttributeError(name)
		
if __name__ == '__main__':
	reader = Reader ('../../TEXT_FILES/perfo_descriptions.txt')
	print reader.data['perfos'][0]
	print Writer (reader.data['perfos'][0]).as_string()
