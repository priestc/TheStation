# TheStation

## Overview

The Station is a software package for managing an online radio station.

It includes:

    * A station listen page where you can listen to the station
    * An upload form with Last.FM support for getting album art.
    * Autotip support, so listeners can send bitcoin tips to the artist of the
      currently playing song.
    * An API for apps can be made to listen to TheStation streams.
    * A CMS like backend for managing song metadata. Powered by the Django Admin.

The code for selecting the next song to play is tuned to favor variety over
playing the same artist or genre over and over again.

The music stream is synchronized. All listeners who listen to the stream are
hearing the same song.

## Installation

Note: These directions are very terse. If you can't figure out how complete the steps,
feel free to ask for help on reddit or in the github issues.

First, make a new server on your favorite VM hosting service (EC2, or DigitalOcean).

SSH into the server, navigate to your home folder, and clone the repo.

    cd ~
    sudo apt-get install git
    git clone git@github.com:priestc/TheStation.git

Install postgres and then make the database:

    sudo apt-get install postgresql
    createdb thestation

Install python dependencies:

    sudo apt-get install python-pip
    sudo pip install -r ~/TheStation/requirements.txt

Run the migration script to get started:

    python ~/TheStation/manage.py migrate

Modify the `local_settings.py` file with your Amazon S3 credentials. See the
section below for full instructions of all settings you can tweak.

Now install nginx and uwsgi on this server. If you are on ubuntu, you'd do:

    sudo apt-get install uwsgi nginx

Install the uwsgi conf file into the uwsgi `apps-enabled` folder,
and move the nginx conf into the nginx `sites-enabled` folder:

    ln -s ~/TheStation/thestation-uwsgi.yaml /etc/uwsgi/apps-enabled
    ln -s ~/TheStation/thestation-nginx.conf /etc/nginx/sites-enabled

Restart nginx and uwsgi. Now go to the server's IP in your browser.
You should see the station page. You can now upload songs from the /upload url
in your browser.


# Local Settings

The file `local_settings.py` contains a bunch of variables that you an modify.
They are as follows:

* `LASTFM_KEY`: 32 char string. You can get an Last.FM API key from
signing up at last.fm. This is used to get album at info on the upload page.

* `TITLE`: A string containng the title of your station. This string should
contain HTML. When all HTML tags are stripped, there should still be the title
in words. In other words, this value needs to be text, not just an `img` tag,
for instance.

* `BANDWIDTH_FUND_ADDRESS`: A bitcoin address for users to donate to for bandwidth.
This should be the public key.
