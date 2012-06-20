#!/usr/bin/python

import sys
import argparse
import mail
import reference
import os
import fnmatch
import chatlog
import image


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
		
	
	# images	
	for r,d,f in os.walk(args.rootdir):
		reg = fnmatch.translate('*.{jpg,png}')
		for fn2 in fnmatch.filter(f,'*.jpg'):
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
		for fn2 in fnmatch.filter(f,'*chat*.html'):
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
		
	#for m in messages:
		#writers.append(mail.Writer(reference.Factory(m, messages).doc))
	
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
	


