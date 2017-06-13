#!/usr/bin/env python

"""
drupdate.py: Downloads newer Drupal Contrib modules.

Fill in config.yml, and drupdate will do the rest!
"""

__author__    = "Brian Jopling"
__copyright__ = "Copyright 2017, University of Pennsylvania School of " \
				"Arts and Sciences."
__credits__   = ["Brian Jopling", "Clay Wells"]
__license__   = "GNU GENERAL PUBLIC LICENSE"
__version__   = "1.0.1"
__status__    = "Development"

"""
USAGE

First, it's recommended you modify config.yml to suit your needs.
Next/Otherwise, just run:

$ python drupdate.py

And you're set!
"""

""" IMPORTS """
import time
import yaml
import os
# Used for running bash commands.
import subprocess
# Used for getting args.
from optparse import OptionParser
# Used for web scraping.
import urllib2
from bs4 import BeautifulSoup

""" GLOBALS """
# Get & Set Options / Args
parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", \
                  help="Print each step made by the program.")
parser.add_option("-p", "--path", "--contrib", dest="contrib_path", \
                  help="Set contrib module path.", metavar='PATH')
parser.add_option("-u", "--username", "--user", dest="username", \
                  help="Set git username.", metavar='USERNAME')
parser.add_option("-m", "--modules", dest="modules", \
                  help="Specify modules to delete.", metavar='\'MODULE-1 MODULE-2\'')
(options, args) = parser.parse_args()

# Prompted user for project info
verbose          = options.verbose
contrib_path     = options.contrib_path
git_username     = options.username
updating_modules = []

list_mods = str(options.modules).split(' ')
if list_mods:
	for m in list_mods:
		updating_modules.append(m)

# Obtained project info
proj_downloads = []
proj_names     = []
proj_urls      = []

# Today's date used as git branch name.
# ex. May 9th, 2015 becomes 150509
date = time.strftime("%y%m%d")

# The formatting for this URL must be precise.
# Make sure there is a back-slash "/" at the end of the url.
default_url = 'https://www.drupal.org/project/'
tmp_dirname = '.tmp-drupdate/'

rm_commands = []


""" FUNCTIONS """

def exit_program(reason):
    """Terminates program and displays the reason why."""
    print 'Aborting! Reason: ' + reason
    exit()


def read_config():
	"""Tries to read from config.yml"""
	global contrib_path, git_username
	with open("config.yml", 'r') as config_yml:
		try:
			config_settings = yaml.load(config_yml)
			if 'git-username' in config_settings:
				git_username = config_settings['git-username']
			if 'contrib-location' in config_settings:
				contrib_path = config_settings['contrib-location']
			if 'modules-to-update' in config_settings:
				list_mods = config_settings['modules-to-update'].split(',')
				if list_mods:
					for m in list_mods:
						m = m.strip()
						updating_modules.append(m)
			init_prompts()
		except yaml.YAMLError as exc:
			print exc
		config_yml.close()


def init_prompts():
	"""Prompts user for info."""
	global contrib_path, git_username, updating_modules
	if not contrib_path:
		contrib_path = raw_input("\nPath containing contrib modules (ex." \
								" /home/your_username/drupal8/contrib ):\n")
	if not git_username:
		git_username = raw_input("\nGit username:\n")
	if not updating_modules or updating_modules[0] == 'None' or not updating_modules[0].strip():
		updating_modules[0] = raw_input("\nModules to update (type * for all):\n")
	verify_prompts()


def verify_prompts():
    global contrib_path, git_username, updating_modules
    if not contrib_path or not git_username or not updating_modules[0].strip() or updating_modules[0] == 'None':
        print '\nWarning!\nPlease submit a proper value:'
        init_prompts()


def new_git_branch(proj_name):
    """Creates new git branch containing updated modules."""
    global git_username, date
    rc = subprocess.call(['git', 'checkout', 'master'])
    rc = subprocess.call(['git', 'pull', 'origin', 'master'])
    rc = subprocess.call(['git', 'checkout', '-b', date + '-' + git_username])
    if verbose:
	    print '[*] New git branch: ' + date + '-' + username


def fill_proj_urls():
	"""Gets URLs for every project in contrib path."""
	global proj_urls, contrib_path, default_url, proj_names, updating_modules
	if updating_modules[0] == '*':
		proj_names = os.walk(contrib_path).next()[1]
	else:
		proj_names = updating_modules
	for name in proj_names:
		proj_urls.append(default_url + name)


def create_tmp_download_dir():
	"""Creates new directory for project review."""
	global contrib_path, tmp_dirname
	rc = subprocess.call(['mkdir', tmp_dirname], cwd=contrib_path)


def get_project_info():
	"""Gets content from project webpage, then extracts desired data."""
	global proj_urls
	for proj_url in proj_urls:
		# Get Drupal Project page content
		try:
			drupal_proj_html = urllib2.urlopen(proj_url).read()
			drupal_proj_info = BeautifulSoup(drupal_proj_html, "html.parser")
			# Get Download file
			temp_proj_download = drupal_proj_info.find_all('td', {'data-th':'Download'})
			print ''
			print '[*] Project: ' + proj_url[31::]
			proj_download = get_downloadable_files(temp_proj_download)
		except urllib2.HTTPError:
			print '[!] WARNING: Could not find project at ' + proj_url
			print '[-] Skipping!'



def get_downloadable_files(temp_proj_download):
	download_link = ''
	proj_download = ''
	# Display all available project versions.
	print "\nThese are the available project versions:"
	for block in temp_proj_download:
		download_link = block.find('a').get('href')
		proj_version = download_link[38::]
		print proj_version
	print ""
	# Let user cycle through choices.
	for block in temp_proj_download:
		download_link = block.find('a').get('href')
		proj_version = download_link[38::]
		choice = raw_input('Download ' + proj_version + ' (y|n)? ')
		if choice == 'y' or choice == 'Y':
			proj_download = download_link
			break
	if not proj_download:
		print "End of possibile files. Recycling..."
		return get_downloadable_files(temp_proj_download)
	download_project(download_link, proj_download)


def download_project(download_link, proj_download):
	"""Downloads and untars project."""
	global contrib_path, rm_commands
	downloadto_path = contrib_path + '' + tmp_dirname
	rc = subprocess.call(['wget', proj_download], cwd=downloadto_path)
	rc = subprocess.call(['tar', '-xzf', proj_download[38::]], cwd=downloadto_path)
	proj_name = proj_download[38::].split('-')[0]
	rc = subprocess.call(['rm', proj_download[38::]], cwd=downloadto_path)
	rm_commands.append('rm -rf ' + proj_name)


def cleanup():
	"""Moves new projects from tmp folder to contrib folder."""
	global contrib_path, tmp_dirname, rm_commands
	# Remove all old project folders.
	for comm in rm_commands:
		rc = subprocess.call(comm, shell=True, cwd=contrib_path)
	downloadto_path = contrib_path + '/' + tmp_dirname
	# Move new ones to old spots.
	rc = subprocess.call('mv * ..', shell=True, cwd=downloadto_path)
	rc = subprocess.call(['rm', '-rf', tmp_dirname], cwd=contrib_path)


def push_git_branch():
    """Pushes branch to Git."""
    current_branch = subprocess.Popen(['git', 'branch'],
	                                  stdout=subprocess.PIPE)
    current_branch = subprocess.check_output(['grep', '\*'],
	                                  stdin=current_branch.stdout)
    choice = raw_input("You are currently on branch " + current_branch + \
	                   "Would you like to git add and git push this branch (y|n)? ")
    if choice == 'y' or choice == 'Y':
		rc = subprocess.call(['git', 'add', '-A'])
		commit_msg = raw_input('Enter a Commit Message: ')
		rc = subprocess.call(['git', 'commit', '-m', commit_msg])
		current_branch = current_branch[2::].rstrip()
		rc = subprocess.call(['git', 'push', '--set-upstream', 'origin', current_branch])


def main():
	read_config()
	new_git_branch()
	fill_proj_urls()
	create_tmp_download_dir()
	get_project_info()
	cleanup()
	push_git_branch()


"""PROCESS"""
if __name__ == "__main__":
	main()
