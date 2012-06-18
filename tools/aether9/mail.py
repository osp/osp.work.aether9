"""
mail.Reader
mail.Writer
"""

import os.path as opath
import re

class FileDoesNotExist(Exception):
	def __init__(self, fname):
		self.filename = fname
	def __str__(self):
		return '%s does not exist'%(self.filename)

class Reader:
	start_pattern = r'^\[aether\]'
	end_header_pattern = r'^Messages sorted by'
	
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
			print('Got %d pieces off data_str with sp(%s)'%(len(data),self.start_pattern))
			for piece in data:
				self.process_piece(piece)
				
	def process_piece(self, piece):
		lines = piece.splitlines()
		#print('Got %d lines off piece'%(len(lines),))
		print('==============================================\n%s\n'%(piece,))
		if len(lines) < 4:
			#raise Exception('Not enough pieces')
			return
		# l0 => title
		# l1 => author
		# l2 => date
		# ... until "Message sorted by" pattern
		# +1 the message!
		
		title = lines.pop(0)
		author = lines.pop(0)
		date = lines.pop(0)
		for l in lines:
			if re.match(self.end_header_pattern, l):
				lines.pop(0)
				lines.pop(0) # ??
				break
			else:
				lines.pop(0)
				
		text = '\n'.join(lines)
		self.data['thread'].append({'title':title, 'author':author, 'date': date, 'text':text})
		
		
		
		
class Writer:
	def __init__(self, mdict):
		self.mail = mdict
		
	def as_string(self):
		ret = []
		ret.append('\\placeintermezzo[here][mail:%d]{}{'%(self.id,))
		ret.append('\\bf{%s}'%(self.title,))
		ret.append('\\it{%s}'%(self.author,))
		ret.append(self.text)
		ret.append('}')
		return '\n'.join(ret)
		
	def __getattr__(self, name):
		try:
			return self.mail[name]
		except Exception:
			raise AttributeError(name)
		