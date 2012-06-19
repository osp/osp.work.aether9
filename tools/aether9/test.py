#!/usr/bin/python

import sys
import argparse
import mail
import reference
import os
import fnmatch
import chatlog


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("rootdir", help="root directory for aether9 files")
	
	args = parser.parse_args()
	c = 0
	
	messages = []
	writers = []
	clogs = []
	for r,d,f in os.walk(args.rootdir):
		for fn in fnmatch.filter(f,'list*.txt'):
			sys.stderr.write('Processing %s , %s\n'%(r,fn))
			fp = os.path.join(r,fn)
			ml = mail.Reader(fp)
			cm = 0
			for m in ml.data['thread']:
				cm +=1
				messages.append(m)
			sys.stderr.write(' => %d\n'%(cm,))
		
	for r,d,f in os.walk(args.rootdir):
		for fn2 in fnmatch.filter(f,'*chat*.html'):
			sys.stderr.write('Processing %s , %s\n'%(r,fn2))
			fp = os.path.join(r,fn2)
			cl = chatlog.Reader(fp)
			cm = 0
			for m in cl.chat:
				cm +=1
				clogs.append(m)
			sys.stderr.write(' => %d\n'%(cm,))
				
	messages.sort(key=lambda x:x['date'])
	
	for i in range(len(messages)):
		messages[i]['id'] = i
		
	for m in messages:
		writers.append(mail.Writer(reference.Factory(m, messages).doc))
	
	ret = []
	ret.append('\\setupoutput[pdftex]')
	ret.append('\\starttext')
	for w in writers:
		ret.append(w.as_string())
		
	ret.append('\\stoptext')
	
	print '\n'.join(ret)
	
	
if __name__ == '__main__':
	main()
	


