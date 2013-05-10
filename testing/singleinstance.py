# http://code.activestate.com/recipes/474070-creating-a-single-instance-application/
# http://code.activestate.com/recipes/546512-creating-a-single-instance-application-linux-versi/
# http://stackoverflow.com/questions/464253/mutex-names-best-practice


## {{{ http://code.activestate.com/recipes/546512/ (r1)
import commands
import os
import platform

# class Linux(object):
# 	"""
# 	singleinstance - based on Windows version by Dragan Jovelic this is a Linux
# 					 version that accomplishes the same task: make sure that
# 					 only a single instance of an application is running.

# 	"""
						
# 	def __init__(self, pid_path):
# 		'''
# 		pid_path - full path/filename where pid for running application is to be
# 				  stored.  Often this is ./var/<pgmname>.pid
# 		'''
# 		self.pid_path=pid_path

# 		if os.path.exists(pid_path):
# 			#
# 			# Make sure it is not a "stale" pidFile
# 			#
# 			pid = open(pid_path, 'r').read().strip()
# 			#
# 			# Check list of running pids, if not running it is stale so
# 			# overwrite
# 			#

# 			try:
# 				kill(pid, 0)
# 				pid_running = 1
# 			except OSError:
# 				pid_running = 0

# 			# pid_running = commands.getoutput('ls /proc | grep %s' % pid)
# 			if pid_running:
# 				self.last_error = True

# 			else:
# 				self.last_error = False

# 		else:
# 			self.last_error = False

# 		if not self.last_error:
# 			#
# 			# Write my pid into pidFile to keep multiple copies of program from
# 			# running.
# 			#
# 			fp = open(pid_path, 'w')
# 			fp.write(str(os.getpid()))
# 			fp.close()

# 	def already_running(self):
# 		return self.last_error

# 	def __del__(self):
# 		if not self.last_error:
# 			os.unlink(self.pid_path)

class Linux(object):
	def __init__(self, path, app_name, parent=None):
		self.parent = None
		self.app_name = app_name


	import fcntl, sys
pid_file = 'program.pid'
fp = open(pid_file, 'w')
try:
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    # another instance is running
    sys.exit(0)

def single_instance(app_name):
	if platform.system() == 'Linux':
		return Linux(app_name)

	elif platform.system() == 'Windows':
		single_instance = Windows()



