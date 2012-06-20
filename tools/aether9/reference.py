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
	roads_ = {}
	networks_ = {}
	unknown_ = {}
	def __init__(self, root_dir, base):
		_d('Factory',root_dir, len(base[0]))
		self.base = base
		self.get_kw_lists(root_dir)
		for k in self.keywords:
			try:
				#getattr(self, k['mode'])(k['name'], k['keywords'])
				self.build_refs(k['name'], k['keywords'], k['mode'])
			except Exception:
				_d('Booo\n')
				
		for r in self.networks_:
			_d('##',r,'##')
			for p in self.networks_[r]:
				_d(p[0]['key'], len(p))
		for r in self.roads_:
			_d('##',r,'##')
			for p in self.roads_[r]:
				_d(p[0]['key'], len(p))
				
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
				for r in xrange(0,rlen):
					current = road[r]
					back = road[r-1]
					forward = None
					try:
						forward = road[r+1]
					except Exception:
						forward = road[0]
					#_d(current)
					res = '\\styleroadback{%d}%s\\styleroadforward{%d}'%(back['id'],current['key'],forward['id'])
					bid = self.lookup_idx(current['id'])
					self.base[0][bid]['text'] = self.base[0][bid]['text'].replace(current['key'], res, 1)
			
	
	def output_networks(self):
		pass
		
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
		_d('build_refs',name,target)
		tdict = getattr(self,'%s_'%target)
		tdict[name] = []
		for kw in kws:
			current_ref = []
			for item in self.base[0]:
				try:
					getattr(self, '%s_%s'%(target, item['type']))(item, kw, current_ref)
				except:
					pass
			tdict[name].append(current_ref)
			
	def networks_mail(self, item, kw, cr):
		kwl = kw.split(',')
		for k in kwl:
			sk = k.strip()
			ret0 = re.search(sk, item['text'], flags=re.IGNORECASE)
			ret1 = re.search(sk, item['author'], flags=re.IGNORECASE)
			if  ret0 or ret1:
				cr.append({'id':item['id'], 'key': kwl[0].strip(), 'type':item['type']})

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
		
		
		