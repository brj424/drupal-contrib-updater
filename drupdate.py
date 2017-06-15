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
__version__   = "1.0.2"
__status__    = "Development"

"""
USAGE

First, it's recommended you modify config.yml to suit your needs.
Next/Otherwise, just run:

$ python drupdate.py

And you're set!
"""

""" IMPORTS """
# Used for our naming convention of git branch.
import time
# Used for parsing config.yml
import yaml
# Used for getting list of contribs in contrib dir.
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
parser.add_option("-g", "--git", action="store_true", dest="enabled_git", \
                  help="Force git support.")
parser.add_option("-p", "--path", "--contrib", dest="contrib_path", \
                  help="Set contrib module path.", metavar='<PATH>')
parser.add_option("-u", "--username", "--user", dest="username", \
                  help="Set git username.", metavar='<USERNAME>')
parser.add_option("-m", "--modules", dest="modules", action="append", \
                  default=[], help="Specify modules to update.", \
                  metavar='<MODULE>')
(options, args) = parser.parse_args()

# Prompted user for project info
contrib_path     = options.contrib_path
git_username     = options.username
enabled_git      = options.enabled_git
updating_modules = options.modules

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

# To prevent premature deletion, we will store a list of
# commands that will remove outdated contrib folders.
# These commands get run at the end of our script.
rm_commands = []


""" FUNCTIONS """

def exit_program(reason):
    """Terminates program and displays the reason why."""
    print 'Aborting! Reason: ' + reason
    exit()


def display_banner():
    banner = """
          _                      _       _
         | |                    | |     | |
       __| |_ __ _   _ _ __   __| | __ _| |_ ___
      / _` | '__| | | | '_ \ / _` |/ _` | __/ _ \\
     | (_| | |  | |_| | |_) | (_| | (_| | ||  __/
      \__,_|_|   \__,_| .__/ \__,_|\__,_|\__\___|
                      | |
                      |_|

     Version 1.01 - http://github.com/brj424/drupdate

    """
    print banner


def read_config():
    """Tries to read from config.yml"""
    global contrib_path, git_username, updating_modules
    with open("config.yml", 'r') as config_yml:
        try:
            config_settings = yaml.load(config_yml)
            # If config_settings isn't empty, then grab the git-username,
            # contrib-location, and modules-to-update, if they exist.
            if config_settings != None:
                if enabled_git and 'git-username' in config_settings:
                    git_username = config_settings['git-username']
                if 'contrib-location' in config_settings:
                    contrib_path = config_settings['contrib-location']
                if 'modules-to-update' in config_settings:
                    # This gets us the modules as one string.
                    str_mods = config_settings['modules-to-update']
                    # Break up the string based on commas.
                    # Store as list.
                    list_mods = str_mods.split(',')
                    # As long as list_mods has something in it,
                    # add the modules to updating_modules.
                    if list_mods:
                        updating_modules = []
                        for m in list_mods:
                            m = m.strip()
                            updating_modules.append(m)
            # Prompt user for any missing info.
            init_prompts()
        except yaml.YAMLError as exc:
            print exc
        config_yml.close()


def init_prompts():
    """Prompts user for info."""
    global contrib_path, git_username, updating_modules, enabled_git
    # If the user hasn't specified a path to their contrib modules,
    # ask them for one.
    if not contrib_path:
        contrib_path = raw_input("\nPath containing contrib modules (ex." \
                                " /home/your_username/drupal8/contrib ):\n")
    # If the user hasn't specified whether or not they want to use git,
    # ask them.
    if enabled_git == None:
        choice = raw_input("\nUtilize git? (y|n):\n")
        if choice == 'y' or choice == 'Y' or choice == 'yes':
            enabled_git = True
        else:
            enabled_git = False
    # If the user hasn't specified a git username (which is only used for
    # naming the git branch), ask them for one, if they are utilizing git.
    if enabled_git and not git_username:
        git_username = raw_input("\nGit username:\n")
    if not updating_modules or updating_modules[0] == 'None' \
     or not updating_modules[0].strip():
        # Modules will be inputted as a str, so we'll have to break that up.
        mod_str = raw_input("\nModule(s) to update (separate multiple modules" \
                            " with a space, type * for all):\n")
        mod_list = mod_str.split(' ')
        updating_modules = [] # [0] was None, so let's start over.
        for m in mod_list:
            updating_modules.append(m)
    verify_prompts()


def verify_prompts():
    global contrib_path, git_username, updating_modules
    # contrib_path needs to end with a / for programmer's convenience.
    # We'll be traversing into contrib_path/.tmp-drupdate, so doing this once
    # and in the beginning will make our lives easier.
    if contrib_path and contrib_path[-1] != '/':
        contrib_path += '/'
    # If any required information is missing, display a warning and
    # prompt the user again.
    if not contrib_path or (enabled_git and not git_username) or \
       not updating_modules[0].strip() or updating_modules[0] == 'None':
        print '\nWarning!\nPlease submit a proper value:'
        init_prompts()


def new_git_branch():
    """Creates new git branch containing updated modules."""
    global git_username, date, contrib_path
    # Bash call that checkouts a new branch with the following naming
    # convention: YYYYMMDD-USER
    rc = subprocess.call(['git', 'checkout', '-b', date + '-' + git_username],
                         cwd=contrib_path)
    print '[*] New git branch: ' + date + '-' + git_username


def fill_proj_urls():
    """Gets URLs for every project in contrib path."""
    global proj_urls, contrib_path, default_url, proj_names, updating_modules
    # If the user specified *, then they want to update all their modules.
    # We can get the module names on our own by 'walking' through their
    # contrib path and grabbing the directory names.
    # ---
    # Else, the names have already been specified, so use those.
    if updating_modules[0] == '*':
        proj_names = os.walk(contrib_path).next()[1]
    else:
        proj_names = updating_modules
    # Fill list with all the project URLs.
    # Drupal uses a simple naming convention:
    # http://www.drupal.org/project/project_name/
    # Each item in proj_names should follow its Drupal-counterpart's name.
    for name in proj_names:
        proj_urls.append(default_url + name)


def create_tmp_download_dir():
    """Creates new directory for project review."""
    global contrib_path, tmp_dirname
    # Bash call to create our temporary directory in the contrib path.
    # The temporary directory will store the downloaded .tar.gz files,
    # along with their extractions.
    # This folder's contents will be moved, and the folder will be
    # deleted by the end of this script.
    rc = subprocess.call(['mkdir', tmp_dirname], cwd=contrib_path)


def get_project_info():
    """Gets content from project webpage, then extracts desired data."""
    global proj_urls
    for proj_url in proj_urls:
        # Use BeautifulSoup to get contents of our project's webpage.
        # Get download links for each available version, and take
        # those links to the get_downloadable_files(x) function.
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
    # If the user does not choose to download any of the versions,
    # prompt them again with the versions to download.
    if not proj_download:
        print "End of possibile files. Recycling..."
        return get_downloadable_files(temp_proj_download)
    download_project(download_link, proj_download)


def download_project(download_link, proj_download):
    """Downloads and untars project."""
    global contrib_path, rm_commands
    # Download and extract each module into the temp directory.
    # Remove the .tar.gz file after extraction.
    # Add command to remove outdated project folder to rm_commands.
    # rm_commands gets used during cleanup().
    downloadto_path = contrib_path + tmp_dirname
    rc = subprocess.call(['wget', proj_download], cwd=downloadto_path)
    rc = subprocess.call(['tar', '-xzf', proj_download[38::]], cwd=downloadto_path)
    proj_name = proj_download[38::].split('-')[0]
    rc = subprocess.call(['rm', proj_download[38::]], cwd=downloadto_path)
    rm_commands.append('rm -rf ' + proj_name)


def cleanup():
    """Moves new projects from tmp folder to contrib folder."""
    global contrib_path, tmp_dirname, rm_commands
    # Call all the commands in rm_commands.
    # This will remove all the outdated project directories.
    for comm in rm_commands:
        rc = subprocess.call(comm, shell=True, cwd=contrib_path)
    downloadto_path = contrib_path + tmp_dirname
    # Move all the directories in our tmp folder up one level, which
    # will be the user's contrib_path.
    # Then remove the temp folder.
    rc = subprocess.call('mv * ..', shell=True, cwd=downloadto_path)
    rc = subprocess.call(['rm', '-rf', tmp_dirname], cwd=contrib_path)


def push_git_branch():
    """Pushes branch to Git."""
    global contrib_path
    try:
        # Display list of git branches in contrib_path, and get the name
        # of the branch we are currently on.
        current_branch = subprocess.Popen(['git', 'branch'],
                                          stdout=subprocess.PIPE,
                                          cwd=contrib_path)
        current_branch = subprocess.check_output(['grep', '\*'],
                                          stdin=current_branch.stdout,
                                          cwd=contrib_path)
        # Inform user of the branch they are on, and ask if they're sure they
        # want to push to git.
        choice = raw_input("You are currently on branch " + current_branch + \
                           "Would you like to git add and git push this branch (y|n)? ")
        # If the user wants to push to git, we'll run Bash commands to
        # git add -A, git commit -m (where the user will be prompted to
        # enter a commit message), and git push.
        if choice == 'y' or choice == 'Y':
            rc = subprocess.call(['git', 'add', '-A'], cwd=contrib_path)
            commit_msg = raw_input('Enter a Commit Message: ')
            rc = subprocess.call(['git', 'commit', '-m', commit_msg], cwd=contrib_path)
            current_branch = current_branch[2::].rstrip()
            rc = subprocess.call(['git', 'push', '--set-upstream', 'origin', current_branch],
                                 cwd=contrib_path)
    except:
        # If the above fails, it's most likely due to the user's
        # contrib_path not being a git repo.
        print '\n[!] Git push failed! Is directory a valid git repository?\n'
        print '[*] drupdate has finished running, but was unable to git push.'
        print '[*] Contrib modules have been updated locally.\n'


def main():
    global enabled_git
    display_banner()
    read_config()
    if enabled_git:
        new_git_branch()
    fill_proj_urls()
    create_tmp_download_dir()
    get_project_info()
    cleanup()
    if enabled_git:
        push_git_branch()


"""PROCESS"""
if __name__ == "__main__":
    main()
