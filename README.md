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

Make a new server.

In your home folder, clone the repo.

    cd ~
    git clone git@github.com:priestc/TheStation.git

Install postgres and then make the database:

    sudo apt-get install postgresql
    createdb thestation

Run the migration script to get started:

    ./manage.py migrate

Now install nginx and uwsgi on this server. If you are on ubuntu, you'd do:

    sudo apt-get install uwsgi nginx

Install the uwsgi conf file into the uwsgi `apps-enabled` folder,
and move the nginx conf into the nginx `sites-enabled` folder.

    ln -s ~/TheStation/thestation-uwsgi.conf /etc/uwsgi/apps-enabled
    ln -s ~/TheStation/thestation-nginx.conf /etc/nginx/sites-enabled

Restart nginx and uwsgi. Now go to the server's IP in your browser.
You should see the station page. You can now upload songs from the /upload url
in your browser.
