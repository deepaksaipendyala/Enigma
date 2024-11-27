<h1 align="center">
  Enigma 🤖 - A music recommender bot for Discord1
  
 [![Open Source Love](https://badges.frapsoft.com/os/v3/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
</h1>

<div align="center">

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<!-- [![DOI](https://zenodo.org/badge/533639670.svg)](https://zenodo.org/badge/latestdoi/533639670) -->
<!-- [![Build Status](https://github.com/rahulgautam21/Enigma/actions/workflows/github-actions-build.yml/badge.svg)](https://github.com/rahulgautam21/Enigma/actions) -->
<!-- [![GitHub Release](https://img.shields.io/github/release/rahulgautam21/Enigma.svg)](https://github.com/rahulgautam21/Enigma/releases) -->
<!-- [![GitHub Repo Size](https://img.shields.io/github/repo-size/rahulgautam21/Enigma.svg)](https://img.shields.io/github/repo-size/rahulgautam21/Enigma.svg) -->

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub contributors](https://img.shields.io/badge/contributors-4-green)](https://github.com/NCSU-CSC-510-F2024/Enigma/graphs/contributors)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/NCSU-CSC-510-F2024/Enigma)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/NCSU-CSC-510-F2024/Enigma)
![Supports Python](https://img.shields.io/pypi/pyversions/pytest)
[![style: autopep8](https://github.com/NCSU-CSC-510-F2024/Enigma/actions/workflows/code-formatter.yml/badge.svg)](https://github.com/NCSU-CSC-510-F2024/Enigma/actions/workflows/code-formatter.yml)
[![Test status](https://github.com/NCSU-CSC-510-F2024/Enigma/actions/workflows/run-tests.yml/badge.svg?event=push)](https://github.com/NCSU-CSC-510-F2024/Enigma/actions/workflows/run-tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/NCSU-CSC-510-F2024/Enigma/badge.svg?branch=main)](https://coveralls.io/github/NCSU-CSC-510-F2024/Enigma?branch=main)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14009527.svg)](https://doi.org/10.5281/zenodo.14009527)

</div>

<p align="center">
    <a href="https://github.com/rahulgautam21/Enigma/issues/new/choose">Report Bug</a>
    ·
    <a href="https://github.com/rahulgautam21/Enigma/issues/new/choose">Request Feature</a>
</p>

<h1> 💡 Features </h1>

<div>
<ul>
  <li>Recommend songs based on user input and play them on discord voice channel</li>
  <li>Can be used by teams/friends to listen to the same songs together</li>
  <li>Acts as an amplifier - can be used to play same music on multiple speakers to give a surround sound effect and increase volume output</li>
  <li>Ability to toggle music pause/resume</li>
  <li>Ability to play custom song without having to search the song on youtube</li>
  <li>Ability to switch back and forth between songs</li>
</ul>
If you want to get added to the music server on discord to test the bot, drop an email to spriyad2@ncsu.edu
</div>
  
<h1> Features added by Group 17</h1>

<div>
<ul>
  <li>Added a new data set [this](https://www.kaggle.com/datasets/saurabhshahane/music-dataset-1950-to-2019) which has approximately 24000 songs</li>
  <li>Added a new functionality to shuffle the songs within the queue</li>
  <li>Added a new functionality to add a custom song to the queue</li>
  <li>Fixed the issue of fetching songs from Youtube</li>
  <li>Extended the application to be deployed on Microsoft Azure</li>
</ul>
</div>

<h1> Features added by group 36, fall 2024 </h1>
<div>
<ul>
  <li>New Poll Command</li>
  <li>New Recommendation Algorithm</li>
  <li>Use web scraping and EDA to get a better database for the discord bot</li>
  <li>Improved Queue System</li>
</ul>
</div>

<h1> Features added by group 19, fall 2024 </h1>
<div>
<ul>
  <li>Search song from different sources</li>
  <li>Search optimation using spotify</li>
  <li>Give your own songs to playlist</li>
  <li>Improved audio quality and playback</li>
  <li>Add loggin</li>
</ul>
</div>

<h1> ⚒️ Installation Procedure </h1>

See the installation instructions listed in [`Install`](INSTALL.md)

<h1> 🚀 Demo </h1>

https://user-images.githubusercontent.com/20087273/194780603-f163caf6-2c9e-4d74-8fbd-c93f30e8935a.mp4

<h1> 🚀 Demo 2 - Group 17 </h1>

https://user-images.githubusercontent.com/21155121/205782352-426dcee7-f145-43f1-af2e-a6eead2ccea3.mp4

<h1> 🚀 Demo 3 - Group 36, Fall 2024 </h1>

[link](https://youtu.be/CKdSPDz1jI8)

<h1> 🚀 Demo 4 - Group 19, Fall 2024 </h1>

[V4: Fall 2024 Demo](https://youtu.be/4pq8weKVvBk)

<h1>📍RoadMap </h1>

#### What We've Done:

1. Created a Discord Bot via the Discord Developer Portal.
2. Incorporated a [dataset](https://www.kaggle.com/datasets/leonardopena/top-spotify-songs-from-20102019-by-year) to our application.
3. Added functionalities to the Discord bot (explained in the [Features](https://github.com/rahulgautam21/Enigma/blob/main/README.md) section above.
4. Use the Discord Bot to play music based on the user's recommendations.
5. Can also use the Bot to play custom songs without having to search for it on YouTube.
6. Extend the application to be deployed online (via a website or an application).
7. Alternatively, use [this](https://www.kaggle.com/datasets/saurabhshahane/music-dataset-1950-to-2019) as the primary data source to make better recommendations.
8. Added some more functionality to the discord bot:
    - Add a custom song to the queue
    - Shuffle songs within the queue

#### New in v3.0

9. New Poll Command: This new poll command allows you to select up to 10 songs you like in order to curate a custom playlist for you to listen to
10. New Recommendation Algorithm: Our new and improved recommendation algorithm now uses cosine similarity to identify songs similar to songs you have indicated that you like.
11. Use web scraping and EDA to get a better database for the discord bot.
12. Improved Queue System:
    - Queue command: Now outputs the queue in a much nicer format compared to last version where it was just a list of song names
    - New Move Command: Users now have the ability to move songs within a queue by specifying the song and the position in queue
    - New Clear Queue Command: New ability to clear queue of all songs
    - Next Song Played Automatically: The next song in queue automatically starts playing once the current song stops instead of having to call next song command

#### New in v4.0

🎧  Choose Your Source: Stream from YouTube (yt) or SoundCloud (sc) with ease!   
🔗  Add Songs Instantly: Simply paste the URL to queue your favorite tracks.   
🎶  Accurate Song Titles: Played songs automatically update with official titles from websites for easy recognition.   
🔍  Spotify-Powered Searches: Find the exact song you want using Spotify’s accurate search info!   
🔊  Volume Control: Take full control of the volume for the perfect listening experience.   
✨  Enhanced Music Quality: Enjoy superior sound for every beat and melody.  
📋  Improved Code Logging and Debugging: Streamlined and efficient logging for seamless troubleshooting and performance monitoring.  
✅  Enhanced Code Coverage and Testing: Comprehensive test cases ensure reliability and maintainability of the bot.  


#### What We've Yet To Do:

1. Integrating dislikes (taking into account the feedback of users) in the recommendation logic.
2. Playlists: Add a new feature to upload a list of songs in a .csv or .txt file to create a playlist that can be saved and played.
3. Improved Polling: Instead of having the bot select 10 random songs for the user to choose from, have the user input the songs they like to send to the recommend algorithm
4. Integrate Spotify/Apple Music: Instead of getting songs from YouTube (which has issues with playing audio that isn’t always songs) use other services such as Spotify or Apple Music to get audio.

<h1>📖 Documentation</h1>

Documentation for the code available at - <a href="https://ncsu-csc-510-f2024.github.io/Enigma/">Enigma Docs</a>

<h1> 👥 Contributors <a name="Contributors"></a> </h1>

### Group 17

<table>
  <tr>
    <td align="center"><a href="https://github.com/Sneha1b"><img src="https://avatars.githubusercontent.com/u/29037428?v=4" width="75px;" alt=""/><br /><sub><b>Sneha Madle</b></sub></a></td>
    <td align="center"><a href="https://github.com/yugaleepatil"><img src="https://avatars.githubusercontent.com/u/91028926?v=4" width="75px;" alt=""/><br /><sub><b>Yugalee Patil</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/cnangia-ncsu"><img src="https://avatars.githubusercontent.com/u/89174495?v=4" width="75px;" alt=""/><br /><sub><b>Chirrag Nangia</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/SASWAT123"><img src="https://avatars.githubusercontent.com/u/21155121?v=4" width="75px;" alt=""/><br /><sub><b>Saswat Priyadarshan</b></sub></a><br /></td>
  </tr>
</table>

### Group 36, Fall 2024

<table>
  <tr>
    <td align="center"><a href="https://github.com/NicoField"><img src="" width="75px;" alt=""/><br /><sub><b>Nico Field</b></sub></a></td>
    <td align="center"><a href="https://github.com/Symplexity"><img src="" width="75px;" alt=""/><br /><sub><b>Riley Joncas</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/birukayalew"><img src="" width="75px;" alt=""/><br /><sub><b>Biruk Tadesse</b></sub></a><br /></td>

  </tr>
</table>

### Group 19, Fall 2024

<table>
  <tr>
    <td align="center"><a href="https://github.com/Captain-Tim"><img src="https://avatars.githubusercontent.com/u/62422680?v=4" width="75px;" alt=""/><br /><sub><b>YiTing Hou</b></sub></a></td>
    <td align="center"><a href="https://github.com/deepaksaipendyala"><img src="https://avatars.githubusercontent.com/u/76196490?v=4" width="75px;" alt=""/><br /><sub><b>Deepak Sai Pendyala</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/LiuKang-11"><img src="https://avatars.githubusercontent.com/u/13636671?v=4" width="75px;" alt=""/><br /><sub><b>Leslie Liu</b></sub></a><br /></td>

  </tr>
</table>

<h1> Contributing </h1>

Please see [`CONTRIBUTING`](CONTRIBUTING.md) for contributing to this project.

<h1> Data </h1>

The data for this project is present [here](https://www.kaggle.com/datasets/saurabhshahane/music-dataset-1950-to-2019)

<!-- <h1> Support </h1>
For any support reach out to spriyad2@ncsu.edu -->
