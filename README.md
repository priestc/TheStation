# TheStation

Overview
========

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
