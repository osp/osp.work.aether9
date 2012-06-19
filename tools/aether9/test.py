#!/usr/bin/python

import sys
import argparse
import mail
import os
import fnmatch


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("rootdir", help="root directory for aether9 files")
	
	args = parser.parse_args()
	c = 0
	writers = []
	for r,d,f in os.walk(args.rootdir):
		for fn in fnmatch.filter(f,'list*.txt'):
			#print('Processing %s , %s'%(r,fn))
			fp = os.path.join(r,fn)
			ml = mail.Reader(fp)
			for m in ml.data['thread']:
				m['id'] = c
				writers.append(mail.Writer(m))
				c += 1
				
	ret = []
	ret.append('\\setupoutput[pdftex]')
	ret.append('\\starttext')
	for w in writers:
		ret.append(w.as_string())
		
	ret.append('\\stoptext')
	
	print '\n'.join(ret)
	
	
if __name__ == '__main__':
	main()
	


