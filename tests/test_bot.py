"""
This file contains various test cases for the bot using dpytest to simulate the discord environment
"""

import discord
import os
import asyncio
import pytest
import discord.ext.test as dpytest
from discord.ext import commands


@pytest.mark.asyncio
async def test_ping(bot):
    """
    Test the ping command
    """
    await dpytest.message("!ping")
    assert dpytest.verify().message().content("Pong!")
