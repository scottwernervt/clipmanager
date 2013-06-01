#
# Regular cron jobs for the clipmanager package
#
0 4	* * *	root	[ -x /usr/bin/clipmanager_maintenance ] && /usr/bin/clipmanager_maintenance
