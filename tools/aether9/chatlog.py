"""
chatlog.Reader
chatlog.Writer
"""

from HTMLParser import HTMLParser
import time
import datetime
import sys
import re

# create a subclass and override the handler methods
class SkypeParser(HTMLParser):
	states = [ 'no_op' ,'created', 'new_message_local_user', 'new_message_remote', 'remote_user', 'user_end' , 'time', 'content' ]
	
	def start(self, filename):
		data_str = False
		self.state = 'no_op'
		self.current = {}
		self.chat = []
		try:
			f = open(filename)
			data_str = f.read()
		except IOError:
			print 'Cannot open %s: expect missing data'%(filename,)
		except Exception as e:
			print 'Unhandle exception: %s'%(e,)
		finally:
			f.close()
			
		
		
		self.feed(data_str.replace(r'<BR>','\n'))
		
	def handle_starttag(self, tag, attrs):
		da = {}
		for a in attrs:
			da[a[0]] = a[1].split()
		try:
			getattr(self, tag)(da)
		except AttributeError:
			pass

	def dt(self, da):
		if 'class' in da:
			if 'remote' in da['class']:
				self.state = 'new_message_remote'
			elif 'local' in da['class']:
				self.state = 'new_message_local_user'
				
	def a(self, da):
		if self.state == 'new_message_remote':
			self.state = 'remote_user'
		
	def span(self, da):
		if self.state == 'user_end':
			self.state = 'time'
			
	def p(self, da):
		if self.state == 'no_op':
			self.state = 'created'
	
	def dd(self, da):
		if self.state == 'time':
			self.state = 'content'
			
	#def handle_endtag(self, tag):
		#pass
		
	def new_message_local_user(self,data):
		#sys.stderr.write('=> new_message_local_user\n')
		self.current['author'] = data
		self.state = 'user_end'
		
	def remote_user(self,data):
		#sys.stderr.write('=> remote_user\n')
		self.current['author'] = data
		self.state = 'user_end'
		
	def time(self, data):
		dt = data.split(':')
		tmp_t = datetime.time(int(dt[0]),int(dt[1]),int(dt[2]))
		#if tmp_t.hour < self.start_date.hour:
			#raise
		dc = datetime.datetime.combine(self.start_date, tmp_t)
		self.current['date'] = dc
		
	def content(self, data):
		#sys.stderr.write('=> content\n')
		self.current['text'] = data
		self.current['type'] = 'chatlog'
		self.state = 'no_op'
		self.chat.append(self.current)
		#sys.stderr.write('=> %s\n'%(self.current,))
		self.current = {}
		
	def created(self, data):
		self.start_date = datetime.datetime.strptime(data, 'Created on %Y-%m-%d %H:%M:%S.')
		self.state = 'no_op'
		
	def handle_data(self, data):
		try:
			getattr(self, self.state)(data)
		except AttributeError:
			pass
		
class Reader:
	def __init__(self, filename, images = [], delta = 30):
		sp = SkypeParser()
		sp.start(filename)
		t_delta = datetime.timedelta(0,delta,0)
		self.chat = []
		c_len = len(sp.chat)
		c_idx = 0
		in_flag = False
		for im in images:
			for c in xrange(c_idx, c_len):
				itvl = self.abs_itvl(im['date'], sp.chat[c]['date'])
				if itvl < t_delta:
					in_flag = True
					self.chat.append(sp.chat[c])
				elif in_flag:
					in_flag = False
					break
				c_idx = c 
		
	def abs_itvl(self, a, b):
		if a < b:
			return b - a
		else:
			return a - b
			
		
class Writer:
	tex_special_chars = {r'&': '\\&', r'%': '\\%', r'$': '\\$', r'#': '\\#', r'_': '\\_', r'{': '\\{', r'}': '\\}', r'~': '\\textasciitilde{}', r'^': '\\textasciicircum{}', '\\' : '\\textbackslash{}', '|':'\\textbar{}'}
	def __init__(self, cldict):
		self.log = cldict
		
	def as_string(self):
		et_pat = '[%s]'%(re.escape(''.join(self.tex_special_chars.keys())),)
		esc_text = re.sub(et_pat, getattr(self, 'escape_tex') , self.text)
		ret = []
		ret.append('\\subject[chat:%d]{%d}'%(self.id,self.id))
		ret.append('\\it{%s /%s/} '%(self.author, self.date.strftime('%d.%m.%Y')))
		ret.append('\\tf{%s}'%(esc_text,))
		ret.append('\n')
		
		return '\n'.join(ret)
		
	def escape_tex(self, pt):
		r = pt.group()
		#print('matched: %s'%r)
		if r in self.tex_special_chars:
			return self.tex_special_chars[r]
		return r
			
		
	def __getattr__(self, name):
		try:
			return self.log[name]
		except Exception:
			raise AttributeError(name)
		
