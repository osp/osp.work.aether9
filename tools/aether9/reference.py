"""
reference.Factory
"""
import os
import glob
import sys
import re


def _d(*args):
	for a in args:
		sys.stderr.write('%s '%a)
	sys.stderr.write('\n')

class FileDoesNotExist(Exception):
	def __init__(self, fname):
		self.filename = fname
	def __str__(self):
		return '%s does not exist'%(self.filename)


class Factory:
	tex_special_chars = {r'&': '\\&', r'%': '\\%', r'$': '\\$', r'#': '\\#', r'_': '\\_', r'{': '\\{', r'}': '\\}', r'~': '\\textasciitilde{}', r'^': '\\textasciicircum{}', '\\' : '\\textbackslash{}', '|':'\\textbar{}'}

	roads_ = {}
	networks_ = {}
	unknown_ = {}
	def __init__(self, root_dir, base):
		_d('Factory',root_dir, len(base[0]))
		self.et_pat = '[%s]'%(re.escape(''.join(self.tex_special_chars.keys())),)
		self.base = base
		self.get_kw_lists(root_dir)
		for k in self.keywords:
			try:
				_d(k['name'], ' | ', k['keywords'], ' | ', k['mode'], ' \n ')
				self.build_refs(k['name'], k['keywords'], k['mode'])
			except Exception:
				_d('Booo\n')
				
		#self.output_networks()
		self.output_roads()
				
	def lookup_idx(self, tid):
		blen = len(self.base[0])
		for i in xrange(0,blen):
			if self.base[0][i]['id'] == tid:
				return i
		return None
		
	def output_roads(self):
		#_d(self.roads_)
		for name in self.roads_:
			for road in self.roads_[name]:
				rlen = len(road) 
				_d('\nReference road:', name)
				if road and road[0]:
					for r in xrange(0,rlen):
						sys.stderr.write('%d '%r)
						current = road[r]
						
						back = road[r-1]
						forward = None
						try:
							forward = road[r+1]
						except Exception:
							forward = road[0]
						#_d(current)
						if current['type'] == 'mail':
							res = '\\stylerefroadback{%d}\\stylerefmailslow{%s}\\stylerefroadforward{%d}'%(back['id'],current['key'],forward['id'])
						else:
							res = '\\stylerefroadback{%d}%s\\stylerefroadforward{%d}'%(back['id'],current['key'],forward['id'])
						bid = self.lookup_idx(current['id'])
						txt = ''
						if 'tex_escaped' not in self.base[0][bid]:
							txt = self.escape_tex(self.base[0][bid]['text']).replace(current['key'], res, 1)
						else:
							txt = self.base[0][bid]['text'].replace(current['key'], res, 1)
						#_d(txt)
						self.base[0][bid]['text'] = txt
						self.base[0][bid]['tex_escaped'] = True
				
		#sys.exit()
			
	
	def output_networks(self):
		for name in self.networks_:
			for network in self.networks_[name]:
				rlen = len(network) 
				_d('\nReference network:', name)
				#_d(' ', network)
				if network and network[0]:
					for r in xrange(0,rlen):
						sys.stderr.write('%d '%r)
						current = network[r]
						
						_d('Key:', current['key'])
						itargets = set()
						for t in xrange(0,rlen):
							itargets.add(network[t]['id'])
						
						tmptargets = []
						for it in itargets:
							tmptargets.append(it)
						tmptargets.sort()
						targets = []
						for ta in tmptargets:
							targets.append('%s'%ta)
						#_d('Network',targets.keys());
						#_d(current)
						res = '\\stylerefnet{%s}%s'%(', '.join(targets), current['key'])
						bid = self.lookup_idx(current['id'])
						txt = ''
						if 'tex_escaped' not in self.base[0][bid]:
							txt = self.escape_tex(self.base[0][bid]['text']).replace(current['key'], res, 1)
						else:
							txt = self.base[0][bid]['text'].replace(current['key'], res, 1)
						#_d(txt)
						self.base[0][bid]['text'] = txt
						self.base[0][bid]['tex_escaped'] = True
		
	def get_kw_lists(self, rd):
		fl = glob.glob('%s/*'%rd)
		self.keywords = []
		for lf in fl:
			fn = lf.split('/').pop()
			_d('KF',fn)
			if not os.path.exists(lf):
				raise FileDoesNotExist(lf)
			data_str = None
			try:
				f = open(lf)
				data_str = f.read()
			except IOError:
				_d( 'Cannot open %s: expect missing data'%(lf,))
			except Exception as e:
				_d( 'Unhandle exception: %s'%(e,))
			finally:
				f.close()
			if data_str:
				parts = fn.split('_')
				self.keywords.append({'name':parts[0],'mode':parts[1],'keywords':data_str.splitlines()})
				
	def build_refs(self, name, kws, target):
		_d('build_refs',name,target,kws)
		tdict = getattr(self,'%s_'%target)
		tdict[name] = []
		for kw in kws:
			current_ref = []
			for item in self.base[0]:
				try:
					getattr(self, '%s_%s'%(target, item['type']))(item, kw, current_ref)
				except Exception as e:
					#_d('Failed to process:', '%s_%s'%(target, item['type']), item['id'])
					#_d(e)
					pass
			tdict[name].append(current_ref)
			
	def networks_mail(self, item, kw, cr):
		#_d('networks_mail',item,kw,cr)
		kwl = kw.split(',')
		for k in kwl:
			sk = k.strip()
			ret0 = re.search(sk, item['text'], flags=re.IGNORECASE)
			ret1 = re.search(sk, item['author'], flags=re.IGNORECASE)
			if  ret0 or ret1:
				_d('Appending Match:', item['id'], kwl[0].strip(), item['type'])
				cr.append({'id':item['id'], 'key': k.strip(), 'type':item['type']})

	def networks_technical(self, item, kw, cr):
		networks_mail(item, kw, cr)
		
	def networks_general(self, item, kw, cr):
		networks_mail(item, kw, cr)
		
	
	
	def roads_mail(self, item, kw, cr):
		kwl = kw.split(',')
		for k in kwl:
			sk = k.strip()
			ret = re.search(sk, item['text'], flags=re.IGNORECASE)
			if  ret:
				cr.append({'id':item['id'], 'key': sk, 'type':item['type']})
				
	def roads_chatlog(self, item, kw, cr):
		kwl = kw.split(',')
		for k in kwl:
			sk = k.strip()
			ret = re.search(sk, item['text'], flags=re.IGNORECASE)
			if  ret:
				cr.append({'id':item['id'], 'key': sk, 'type':item['type']})
				
	def roads_technical(self, item, kw, cr):
		roads_mail(item, kw, cr)
		
	def roads_general(self, item, kw, cr):
		roads_mail(item, kw, cr)
		
	def escape_tex_cb(self, pt):
		r = pt.group()
		if r in self.tex_special_chars:
			return self.tex_special_chars[r]
		return r
			
	def escape_tex(self, text):
		return re.sub(self.et_pat, getattr(self, 'escape_tex_cb') , text)