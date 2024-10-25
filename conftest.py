"""
This is the configuration file for the dpytest plugin. It is used to created a simulated discord environment for testing the bot features
"""

import os
import sys

import discord.ext.test as dpytest
import pytest_asyncio
import discord
from discord.ext import commands
import glob

from os.path import dirname as d
from os.path import abspath

root_dir = d(d(abspath("test/test_bot.py")))
sys.path.append(root_dir)

@pytest_asyncio.fixture
async def bot():
    """
    This fixture is used to create a bot instance for testing
    """

    # Setup
    intents = discord.Intents.all()
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Load all cogs
    # dir_path = d(abspath(__file__))
    # os.chdir(dir_path)
    # os.chdir("cogs")

    for filename in os.listdir("./cogs"):
        if filename.endswith("_cog.py"):
            cog_name = filename[:-3]
            cog_path = f"cogs.{cog_name}"
            try:
                await bot.load_extension(cog_path)
                print(f"{cog_name} loaded successfully")
            except Exception as e:
                print(f"Error loading cog {cog_path}: {e}")
    
    await bot._async_setup_hook()
    dpytest.configure(bot, ["Testing"], ["general"], ["General"], ["member1", "member2"])

    yield bot

    # Teardown
    await dpytest.empty_queue()


def pytest_sessionfinish(session, exitstatus):
    """ Code to execute after all tests. """

    # dat files are created when using attachements
    print("\n-------------------------\nClean dpytest_*.dat files")
    fileList = glob.glob('./dpytest_*.dat')
    for filePath in fileList:
        try:
            os.remove(filePath)
        except Exception:
            print("Error while deleting file : ", filePath)