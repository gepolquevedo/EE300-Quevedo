#!/usr/bin/env python
import subprocess
import shlex
import os
import glob
import re
import time
import sys
#import standard cachehandler here
from BitTorrent.CacheHandler import Cache_handler
import shutil
import random


TORRENT_DIR = '/home/gepol/torrents/'
CACHE_DIR = '/home/gepol/cache/'
UPLOADER_CMD = './bittorrent-console.py --upload_only --save_in '
DOWNLOADER_CMD = './bittorrent-console.py --save_in '
SET_UPLOAD_RATE = '--max_upload_rate '
TYPE_UPLOADER = 0
TYPE_DOWNLOADER = 1
MAX_SIZE = 5000000
LOG_NAME = 'bitlog-'

starttime = None
lognum = None

processes = []
process_type = []
process_num = []
process_file = []
log_files = []
#methods for handling the cache file

def _get_bottom():
    f = open('.cachestatus', 'r')
    entries = f.readlines()
    lastEntry = entries[0]
    m = re.findall('^[a-zA-Z0-9\.\/\ \&]*',lastEntry)
    filepath = m[0]
    f.close()
    return filepath

def delete_entry(filename):
    print filename
    f = open('.cachestatus', 'r')
    entries = f.readlines()
    f.close
    for entry in entries:
    	m= re.findall('^[a-zA-Z0-9\.\/\ \&]*',entry)[0]
	if m == filename:
		del entries[entries.index(entry)]
    f= open('.cachestatus', 'w')
    for entry in entries:
	f.write(entry)
    f.close()

def _add_new(file):
	pass    
	#use cachehandler here

def start_old_torrents(folder, upload_rate):
	if os.path.isdir(folder):
		filelist = glob.glob(folder+'*')
		for files in filelist:
			strippedName = os.path.split(files)[1]
			name = TORRENT_DIR+strippedName+'.torrent'
			if os.path.getsize(files) > 0:			
				_run_uploader(name, upload_rate)
			
	else:
		print 'not a directory'
	print 'processes', processes

def start_new_torrent(torrentfile, upload_rate):
	_reset_flag()
	#add new file to folder
	filename = os.path.split(torrentfile)[1]
	shutil.copy(torrentfile,TORRENT_DIR+filename)
	#delete files if necessary
	currentsize = _get_cache_size()	
	while currentsize >= MAX_SIZE:
		bottomfile = _get_bottom()
		print 'bottomfile ',bottomfile
		_kill_uploader(bottomfile)
		delete_entry(bottomfile)
		_delete(bottomfile)
		currentsize = _get_cache_size()
	#stop the current downloader
	_kill_downloader(upload_rate)
	#start downloading
	_kill_uploader(TORRENT_DIR+filename)
	_run_downloader(TORRENT_DIR+filename, upload_rate)

def _turn_uploader():
	pass
    
def _get_cache_size():
    filelist = glob.glob(CACHE_DIR+'*')
    totalsize = 0
    for file in filelist:
        if os.path.isfile(file):
            size = os.path.getsize(file)
        else: print 'item not a file'
        totalsize += size
    
    return totalsize
    
    
def create_log():
    global lognum 
    lognum += 1
    f = open(LOG_NAME+str(lognum), 'w')
    log_files.append(f)
    #f.close()
    
    return f

def _run_uploader(torrentfile, upload_rate):
    logfile = create_log()
    torrentfile = torrentfile.replace(' ','\\ ')
    command = UPLOADER_CMD + CACHE_DIR+' '+SET_UPLOAD_RATE+' '+str(upload_rate)+' '+torrentfile+' &'
    args = shlex.split(command)
    p = subprocess.Popen(args,stdout = logfile.fileno(), shell=False)
    processes.append(p)
    print 'pid',p.pid
    process_type.append(TYPE_UPLOADER)
    #get file name without the file extension
    torrentfile = torrentfile.replace('\\ ',' ')
    filename = os.path.splitext(torrentfile) 
    filename = os.path.split(filename[0])
    process_file.append(filename[1])
    
    #edit .cachestatus file? or let the program edit that
    
def _run_downloader(torrentfile, upload_rate):
    logfile = create_log()
    torrentfile = torrentfile.replace(' ','\\ ')
    command = DOWNLOADER_CMD + CACHE_DIR+' '+SET_UPLOAD_RATE+str(upload_rate)+' ' + torrentfile+' &'
    args = shlex.split(command)
    p = subprocess.Popen(args,stdout = logfile.fileno(),shell=False)
    print 'pid',p.pid
    processes.append(p)
    process_type.append(TYPE_DOWNLOADER)
    #get file name without the file extension
    torrentfile = torrentfile.replace('\\ ',' ')
    file = os.path.splitext(torrentfile) 
    file = os.path.split(file[0])
    process_file.append(file[1])
    
    
    #measure of the size of cache. get the bottom dweller and delete if necessary
def _kill_uploader(torrentfile):
    #filename = os.path.splitext(torrentfile)
    filename = os.path.split(torrentfile)[1]
    #try catch block here
    try:
        proc = processes[process_file.index(filename)]
        os.kill(proc.pid,9)
	del process_type[processes.index(proc)]
	del process_file[processes.index(proc)]	
	del processes[processes.index(proc)]
	
    except ValueError:
        print 'upload process not on the list'
    	#sys.exit(1)
    except OSError:
        print 'no such process'
	#sys.exit(1)
	
def _kill_downloader(upload_rate):
	filename = None
	for process in process_type:
		if process is TYPE_DOWNLOADER:
			filename = process_file[process_type.index(process)]			
			try:
				proc = processes[process_type.index(process)]
				os.kill(proc.pid,9)
				del process_type[processes.index(proc)]	
				del process_file[processes.index(proc)]
				del processes[processes.index(proc)]
			
			except ValueError:
				print 'download process not on the list'
				#sys.exit(1)
			except OSError:
				print 'no such process'
				#sys.exit(1)
			torrentname = TORRENT_DIR+filename+'.torrent'			
			_run_uploader(torrentname,upload_rate)
			break

#methods for handling all files being used
def _delete(file):
    if os.path.isfile(file):
	os.remove(file)
    else:
	 print 'file doenst exist or its a directory'

def file_check():
	pass
    #checks if files listed in .cachestatus matches the files existing in the cache folder

#monitoring progress from bT

def _reset_flag():
	f = open('.finished', 'w')
	f.write('')
	f.close

def shutdown():
	for process in processes:
		os.kill(process.pid,9)
		del process_type[processes.index(process)]
		del process_file[processes.index(process)]
		del processes[processes.index(process)]
	for log in log_files:
		log.close()

def start_time():
	global starttime
	starttime = time.time()
	
def duration():
	endtime = time.time()
	duration = endtime - starttime

def wait_to_finish():
	filename = '.finished'
	#oldtime = os.path.getatime(filename)
	#print time.localtime(oldtime)
	while True:
		f = open(filename, 'r')
		stat = f.readline()
		f.close()
		if stat == 'F':
			#raise NameError
			print 'yes'
			return
		else:
			time.sleep(3)			
			continue

def set_fixed_delay(secs):
	time.sleep(secs)

def set_random_delay(sec_range):
	time.sleep(random.randint(sec_range))

def del_cache():
	folder = '/home/gepol/cache/'
	filelist = glob.glob(folder+'*')
	for files in filelist:
		os.remove(files)					

if __name__ == '__main__':
	filename = '/home/gepol/videos/Innovate Like Google.MP4.torrent'
	filename2 = '/home/gepol/Videos/Developing the CEO Within You.MP4.torrent'
	folder = '/home/gepol/cache/'	
	rate =  60 #default rate
	for arg in sys.argv:
		if arg == '--max_upload':
			try:
				rate = sys.argv[sys.argv.index(arg) + 1]
			except IndexError:
				print 'incomplete argument'
				sys.exit(1)
			try:
				rate = int(rate)
			except ValueError:
				print 'invalid rate value'
				sys.exit(1) 		
	lognum = 0 			
	
	#del_cache()	
	cachehandler = Cache_handler()
	cachehandler.generate_cache_from_folder()
	for n in range(5):	
		start_old_torrents(folder, rate)
		#set_fixed_delay(0)	
		#start_new_torrent(filename, rate)
		#start_new_torrent(filename2, rate)
		set_fixed_delay(600)
		#wait_to_finish()		
		
		#delete_entry(filename)
		#_run_downloader(filename)
		set_fixed_delay(60) #additional delay due to peer 1 lag
		set_fixed_delay(110) #fixed delay before repeating download
		shutdown()
