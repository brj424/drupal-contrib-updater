# drupdate
Update Drupal contrib modules in seconds, without having to set up a site or
open a browser!


## Installation
Download the repo and run `$ pip install -r requirements.txt` to install
_drupdate_'s dependencies.


## Configuration (Optional)
Open `config.yml` in your favorite text editor, and modify the settings
to suit your needs.

If you do not modify `config.yml`, running `$ python drupdate.py` will ask you
to enter relevant information during runtime.

Sample `config.yml`:

    contrib-location: /home/paranoid4ndr0id/contrib/
    git-username: paranoid4ndr0id
    modules-to-update: metatag, google_analytics


## Usage

**Default**  
By default, you can run `$ python drupdate.py` and it will ask for
whatever information it needs from you.

**Force Git Support**  
Running `$ python drupdate.py -g` will force-enable git support, so you won't
have to enable it during runtime.

**Using the Config**  
If you **did** modify `config.yml`, then `$ python drupdate.py` will read
the information it needs from there.

**Skipping the Config**  
If you **did not** modifiy `config.yml`, then you can either:
1. Provide arguments:

    `$ python drupdate.py -p /home/paranoid4ndr0id/contrib -u paranoid4ndr0id
      -m metatag -m google_analytics -m features`

2. Enter the information when prompted:

    `$ python drupdate.py`

        Path containing contrib modules (ex. /home/your_username/drupal8/contrib ):
        /home/paranoid4ndr0id/contrib

        Utilize git? (y|n):
        n

        Modules to update (type * for all):
        metatag google_analytics

**Help**  
`$ python drupdate.py -h` or `$ python drupdate.py --help` has a list of neat
features you may want to take advantage of, so be sure to check it out.


## Why use this over Drush?
First, if Drush works for you, use it. It has a much larger base for
contributors, so it's constantly being updated.

One downside to Drush's update command is that it requires you have a site
completely installed and setup before you can use it.

_drupdate_, on the other hand, will update any or all contrib modules in any
directory, whether or not a site is set up.

On top of that, _drupdate_ features git-support. It will automatically
create a new branch for the updates it performs, then push it to your repo.

_drupdate_ is also a lot smaller than Drush. You won't have to install a
bunch of dependencies to use it, and you won't have to familiarize yourself
with dozens of different commands.

It's readily available, and simple to use!

---

![Drupal Logo](https://www.drupal.org/files/druplicon-small.png)
