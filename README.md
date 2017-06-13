# drupdate
Update Drupal contrib modules in seconds, without having to set up a site or
open a browser!


## Installation
Download the repo and run `$ pip install -r requirements.txt` to install
_drupdate_'s dependencies.


## Configuration (Optional)
Open `config.yml` in your favorite text editor, and modify the settings
to suit your needs.

If you do not modify `config.yml`, running `drupdate.py` will ask you to
enter relevant information during runtime.


## Usage
By default, you can run `$ python drupdate.py` and it will ask you for
whatever information it needs from you.

If you've modified `config.yml`, then `drupdate.py` will read the information
it needs from there.


## Why use this over Drush?
First, if Drush works for you, use it. It has a much larger base for
contributors, so it's constantly being updated.

One downside to Drush's update command is that it requires you have a site
completely installed and setup before you can use it.

_drupdate_, on the other hand, will update any or all contrib modules in any
directory, whether or not a site is set up.

_drupdate_ is also a lot smaller than Drush. You won't have to install a
bunch of dependencies to use it, and you won't have to familiarize yourself
with dozens of different commands.

It's readily available, and simple to use!

---

![Drupal Logo](https://www.drupal.org/files/druplicon-small.png)
