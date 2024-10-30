## 🚀 Installation Procedure

## 1. Prerequisites

Installation Guides:

-   [Git Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
-   ~~[IDE Installation Guide (Pycharm)](https://www.jetbrains.com/help/pycharm/installation-guide.html)~~
-   [New IDE Installation Guide (VSCode)](https://code.visualstudio.com/docs/setup/setup-overview)
-   Install FFMPEG from [FFMPEG builds](https://www.gyan.dev/ffmpeg/builds), extract it and add it to your path [How to add FFMPEG to Path](https://www.thewindowsclub.com/how-to-install-ffmpeg-on-windows-10#:~:text=Add%20FFmpeg%20to%20Windows%20path%20using%20Environment%20variables&text=In%20the%20Environment%20Variables%20window,bin%5C%E2%80%9D%20and%20click%20OK.)
-   [Create a discord server for the bot to join](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server)
-   [Set up a bot and have it join your channel](https://discordpy.readthedocs.io/en/stable/discord.html). For the purposes of testing this bot, when giving it permissions selecting admin is fine, but for a proper deployment, it is very important to give it only the strictly necessary permissions.
-   After creating the bot, in the discord developer portal navigate to the 'Bot' tab for the application you made in the previous step, and select 'Reset Token'. Copy and paste this token into a file named `.env` with this format: `DISCORD_TOKEN=SECRET_TOKEN`, where `SECRET_TOKEN` is replaced with the token you just copied

-   [Video Guide](https://youtu.be/jibnRsfhnug)

## 2. Running Code

First, clone the repository and cd into the folder:

```
$ git clone git@github.com:rahulgautam21/Enigma.git
$ cd Enigma
```

### 3. Create a .env file with the discord token info: DISCORD_TOKEN=#SECRET_TOKEN#

### Join the same server as the bot, and connect to any voice channel.

```
$ pip install -r requirements.txt
$ python bot.py
```

Use the `/join` command to get the bot to join the same voice channel as you.

You can now use the discord bot to give music recommendations! Use `/help` to see all functionalities of bot.
