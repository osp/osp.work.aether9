#!/usr/bin/python

import sys
import argparse
import mail
import reference
import os
import fnmatch
import chatlog
import image
import general
import technical
import bio
import perfo
import quotes
import re

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("rootdir", help="root directory for aether9 files")
	parser.add_argument("--style", help="Specify a stylesheet")
	
	args = parser.parse_args()
	c = 0
	
	items = []
	writers = {}
	for i in range(1900, 2100):
		writers[i] = []
	clogs = []
	
	# e-mails
	for r,d,f in os.walk(args.rootdir):
		for fn in fnmatch.filter(f,'list*.txt'):
			sys.stderr.write('Processing %s , %s\n'%(r,fn))
			fp = os.path.join(r,fn)
			ml = mail.Reader(fp)
			cm = 0
			for m in ml.data['thread']:
				cm +=1
				items.append(m)
			sys.stderr.write(' => %d\n'%(cm,))
		
	
	# general discussion
	fp = os.path.join (args.rootdir, 'TEXT_FILES', 'emails-general-discussions.txt')
	sys.stderr.write('Processing %s \n'%(fp))
	ml = general.Reader (fp)
	cm = 0
	for m in ml.data['thread']:
		cm +=1
		items.append(m)
	sys.stderr.write(' => %d\n'%(cm,))
	
	# technical discussion
	fp = os.path.join (args.rootdir, 'TEXT_FILES', 'emails-technical-discussions.txt')
	sys.stderr.write('Processing %s \n'%(fp))
	ml = technical.Reader (fp)
	cm = 0
	for m in ml.data['thread']:
		cm +=1
		items.append(m)
	sys.stderr.write(' => %d\n'%(cm,))
	
	# quotes
	fp = os.path.join (args.rootdir, 'TEXT_FILES', 'great-quotes.txt')
	sys.stderr.write('Processing %s \n'%(fp))
	ml = quotes.Reader (fp)
	cm = 0
	for m in ml.data['quotes']:
		cm +=1
		items.append
	sys.stderr.write(' => %d\n'%(cm,))
	
	# images	
	for r,d,f in os.walk(args.rootdir):
		files = []
		for fn2 in fnmatch.filter(f,'*.jpg'):
			files.append(fn2)
		for fn2 in fnmatch.filter(f,'*.png'):
			files.append(fn2)
		for fn2 in files:
			sys.stderr.write('Processing %s , %s\n'%(r,fn2))
			fp = os.path.join(r,fn2)
			try:
				items.append(image.Reader(fp).img)
			except image.NoDate as e:
				sys.stderr.write('%s\n'%e)
	
	# chatlog
	# we need a list of images to insert less chatlogs
	images = []
	for i in items:
		if i['type'] == 'image':
			images.append(i)
	
	images.sort(key=lambda x:x['date'])
			
	for r,d,f in os.walk(args.rootdir):
		files = []
		for fn2 in fnmatch.filter(f,'*chat*.html'):
			files.append(fn2)
		for fn2 in fnmatch.filter(f,'*chat*.txt'):
			files.append(fn2)
		for fn2 in files:
			sys.stderr.write('Processing %s , %s\n'%(r,fn2))
			fp = os.path.join(r,fn2)
			cl = chatlog.Reader(fp, images)
			cm = 0
			for m in cl.chat:
				cm +=1
				items.append(m)
			sys.stderr.write(' => %d\n'%(cm,))
			
	# bios
	fp = os.path.join (args.rootdir, 'TEXT_FILES', 'biographies.txt')
	sys.stderr.write('Processing %s \n'%(fp))
	ml = bio.Reader (fp)
	cm = 0
	for m in ml.data['bios']:
		cm +=1
		items.append(m)
	sys.stderr.write(' => %d\n'%(cm,))
	
	# performances
	fp = os.path.join (args.rootdir, 'TEXT_FILES', 'perfo_descriptions.txt')
	sys.stderr.write('Processing %s \n'%(fp))
	ml = perfo.Reader (fp)
	cm = 0
	for m in ml.data['perfos']:
		cm +=1
		items.append(m)
	sys.stderr.write(' => %d\n'%(cm,))
	
	items.sort(key=lambda x:x['date'])
	
	for i in range(len(items)):
		items[i]['id'] = i
		
	ref = reference.Factory('%s/nodes'%args.rootdir, [items])
	
	for i in range(len(items)):
		wr = globals()[items[i]['type']].Writer
		writers[items[i]['date'].year].append(wr(items[i]))
		
	
	
	
	
	
	products = []
	for wrt in writers:
		ret = []
		if not writers[wrt]:
			continue
		products.append(wrt)
		f = open('aether_%s.tex'%(wrt,), 'w')
		ret.append('\\startproduct aether_%s'%(wrt,))
		ret.append('\\starttext')
		ret.append('\\part[%s]{%s}'%(wrt,wrt))
		ret.append('\\marking[P]{%s}'%(wrt,))
		#ret.append('\\startcolumnset[duo]')
		for w in writers[wrt]:
			ret.append(re.sub ('((([^\s<>]+)?)(@|mailto\:|(news|(ht|f)tp(s?))\s?\://)\S+)', hyphenate_urls, w.as_string()))
		#ret.append('\\stopcolumnset')	
		ret.append('\\stoptext')
		ret.append('\\stopproduct')
	
		f.write( '\n\n'.join(ret) )
		f.close()
		
	
	fpr = []
	fpr.append('\\startproject aether')
	if args.style:
		fpr.append('\\environment %s'%args.style)
	for p in products:
		fpr.append('\\product aether_%s'%(p,))
	fpr.append('\\stopproject')
	
	
	final_r = open('aether.tex', 'w')
	final_r.write('\n'.join(fpr))
	final_r.close

def hyphenate_urls (matchObject):
	esc_text = re.sub ('\\\\textasciitilde\{\}', '~', matchObject.group(0))
	return '\\hyphenatedurl{%s}' % esc_text 
	
if __name__ == '__main__':
	main()
	


