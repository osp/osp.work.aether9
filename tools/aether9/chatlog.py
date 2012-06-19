"""
chatlog.Reader
chatlog.Writer
"""

from HTMLParser import HTMLParser
import time
import datetime
import sys

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
	def __init__(self, filename):
		sp = SkypeParser()
		sp.start(filename)
		self.chat = sp.chat
		
