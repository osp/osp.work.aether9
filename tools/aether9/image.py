"""
mail.Reader
mail.Writer
"""

import os.path as opath
from os.path import getctime
import re
import time
from datetime import datetime
from PIL import Image
from math import ceil

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
	def __init__(self, filename, root = False):
		self.type = 'image'
		if root <> False:
			filename = opath.join (root, filename)
		if not opath.exists(filename):
			raise FileDoesNotExist(filename)
		try:
			im = Image.open (filename)
		except IOError:
			print 'Cannot open %s: expect missing data'%(filename,)
		except Exception as e:
			print 'Unhandle exception: %s'%(e,)

		self.img = {}
		self.img['filename'] = filename
		#self.creationtime = self.get_creationtime (im)
		self.img['date'] = self.get_creationtime_fromfilename (filename)
		self.img['fullpage'] = self.is_fullpage ()

	def get_creationtime_fromfilename (self, filename):
		tail = opath.split (filename)[1]
		date_patt = '(\d{4})(\d{2})(\d{2})_(\d{2})h(\d{2})m(\d{2})s'
		alt_date_patt = '(\d{4})(\d{2})(\d{2})'
		d = re.search (date_patt, tail)
		if d <> None:
			return datetime (int (d.group(1)), int (d.group(2)), int(d.group(3)), int(d.group (4)), int(d.group (5)), int(d.group(6)))
		else:
			d = re.search (alt_date_patt, tail)
			if d <> None:
				return datetime (int (d.group(1)), int (d.group(2)), int(d.group(3)), 0, 0, 0)
			else:
				raise NoDate(filename)

	def is_fullpage (self):
		return re.search ('^.*FULL.[^LEFT|RIGHT]*$', opath.split (self.img['filename'])[1]) <> None

	def get_creationtime(self, im):
		exif = im._getexif();
		ctime = datetime.fromtimestamp (getctime (self.img['filename'] ))

		if exif <> None:
			for field in [306,36868,36867]:
				if field in exif:
					new_time = datetime.strptime (exif[field], '%Y:%m:%d %H:%M:%S')
					if new_time <> None and (ctime == None or (time.mktime (new_time.timetuple()) > 0 and new_time < ctime)):
						ctime = new_time	

		return ctime
		
class Writer:
	tex_special_chars = {r'&': '\\&', r'%': '\\%', r'$': '\\$', r'#': '\\#', r'_': '\\_', r'{': '\\{', r'}': '\\}', r'~': '\\textasciitilde{}', r'^': '\\textasciicircum{}', '\\' : '\\textbackslash{}', '|':'\\textbar{}'}
	def __init__(self, reader):
		self.image = reader

	def as_string(self,width=False, place='left', caption='none'):
		if (self.fullpage == True):
			parts = self.splitImage ()
			buff = '\n\page[left]'
			buff += '\n\placefigure[left,top]{{}}{{\externalfigure[{0}][width=16.5cm]}}'.format (parts[0])
			buff += '\n\page[right]'
			buff += '\n\placefigure[left,top]{{}}{{\externalfigure[{0}][width=16.5cm]}}'.format (parts[1])
			buff += '\n\page[left]'
		else:
			imgpts = [self.filename]
			if width <> False:
				imgpts.append (width)
			
			buff = '\n\placefigure[{0}]{{{1}}}{{\externalfigure[{2}]}}'.format (place, caption, ']['.join (imgpts))

		return buff


	def escape_tex(self, pt):
		r = pt.group()
		#print('matched: %s'%r)
		if r in self.tex_special_chars:
			return self.tex_special_chars[r]
		return r


	def __getattr__(self, name):
		try:
			self.image[name]
		except Exception:
			raise AttributeError(name)

	def splitImage (self):
		im = Image.open (self.filename)
		leftWidth = int (ceil (float(im.size[0]) * 0.5))
		rightWidth = im.size[0] - leftWidth
		left = Image.new (im.mode, (leftWidth, im.size[1]), (255,255,255))
		right = Image.new (im.mode, (im.size[0] - leftWidth, im.size[1]), (255,255,255))
		left.paste (im.copy (), (0,0))
		right.paste (im.copy (), (-leftWidth,0))
		fparts = self.filename.rsplit ('.', 1)
		paths = ('%s-LEFT.png' % (fparts[0]), '%s-RIGHT.png' % (fparts[0]))
		right.save (paths[1])
		left.save (paths[0])
		
		return paths

if __name__ == '__main__':
	from glob import glob

	root = '/home/gijs/Documents/osp/osp.work.aether9'

	for filename in glob (opath.join (root, 'PAR-PERFO/*/img/*.jpg')):
		reader = Reader (filename)
		if reader.creationtime <> None or reader.fullpage == True:
			writer = Writer (reader)
			print writer.as_string ()
