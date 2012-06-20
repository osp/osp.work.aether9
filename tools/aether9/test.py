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


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("rootdir", help="root directory for aether9 files")
	parser.add_argument("--style", help="Specify a stylesheet")
	
	args = parser.parse_args()
	c = 0
	
	items = []
	writers = []
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
			
			
	items.sort(key=lambda x:x['date'])
	
	for i in range(len(items)):
		items[i]['id'] = i
		wr = globals()[items[i]['type']].Writer
		writers.append(wr(items[i]))
		
	ref = reference.Factory('%s/nodes'%args.rootdir, items)
	
	ret = []
	
	if args.style:
		ret.append('\\input %s'%args.style)
	
	ret.append('\\starttext')
	ret.append('\\startcolumnset[duo]')
	for w in writers:
		ret.append(w.as_string())
	ret.append('\\stopcolumnset')	
	ret.append('\\stoptext')
	
	print '\n'.join(ret)
	
	
if __name__ == '__main__':
	main()
	


