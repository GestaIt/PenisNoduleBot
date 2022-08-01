# main.py
# This file will contain the entrypoint for the application.
# This application will have a self bot send anti-racist & homophobic message every x minutes.
# 7/31/22
#

import asyncio
import configparser
import random
import time

import discord

# This array will contain people of have chatted, along with their previous chat time.
member_chats: dict[str: float] = {}

# Create our config parser.
config: configparser.RawConfigParser = configparser.RawConfigParser(
    converters={'list': lambda x: [i.strip() for i in x.split(',')]})
config.read("config.properties")  # Read our properties file.


# This method will check a message for profanities.
# Possible profanities are contained in profanities.txt.
def contains_profanities(message: str) -> (bool, str):
    lower_message: str = message.lower()

    with open("profanities.txt") as file:
        for word in file.readlines():
            if word.lower().strip() in lower_message:
                return True, word

        return False, ""


# This method is the entrypoint.
def main() -> None:
    messages_per_minute: float = config.getfloat("BotConfig", "messages-per-minute")
    inactive_time: float = config.getfloat("BotConfig", "inactive-label-minute-time")
    channel_id: int = config.getint("BotConfig", "channel-id")
    discord_token: str = config.get("Discord", "discord.token")
    messages: [str] = [i.rstrip(",\\\\") for i in config.get("BotConfig", "messages").split("\n")]
    profane_messages: [str] = [i.rstrip(",\\\\") for i in config.get("BotConfig", "profane-messages").split("\n")]
    new_comer_messages: [str] = [i.rstrip(",\\\\") for i in config.get("BotConfig", "new-comer-messages").split("\n")]

    # We'll just cache the time since we don't want to be doing calculations every single loop.
    sleep_time: float = (1 / messages_per_minute) * 60

    # Construct the class for the bot.
    class PenisNoduleBot(discord.Client):
        # This method will add our own fields into this class.
        def __init__(self):
            super().__init__()
            self.counter: int = 0
            self.channel: discord.TextChannel | None = None

        async def send_message(self):
            # Increment our counter field.
            self.counter += 1

            print(f"Sending message #{self.counter}!")

            # Fetch a random message from the list.
            current_message: str = random.choice(messages)

            # Send "hi", then the message.
            await self.channel.send("Hi.")

            # Sleep for an amount of seconds to make us look human.
            await asyncio.sleep(3)

            # Finally, send the selected message.
            await self.channel.send(current_message)

        async def on_ready(self):
            print("Successfully logged on as", self.user)

            # Fetch the channel that we'll be sending the messages in.
            self.channel: discord.TextChannel = self.get_channel(channel_id)

            # Make sure the channel exists.
            if self.channel is None:
                raise Exception("The channel doesn't exist.")

            # This loop will send the messages.
            while True:
                await asyncio.sleep(sleep_time)

                # This method will send the message for us asynchronously.
                await self.send_message()

        async def on_message(self, message: discord.Message):
            current_time: float = time.time()

            # If the message is from us, or if the message content is empty, exit the method.
            if message.author == self.user or message.content == "" or message.author.bot:
                return

            # Find the last time the person has chatted.
            previous_time: float = message.author.id in member_chats and member_chats[message.author.id] or -1

            # Make sure to greet the person if they haven't sent a message yet.
            if previous_time == -1:
                print(f"Found a new person chatting, {message.author.name}!")

                # Say a friendly greeting.
                await message.reply(f"Welcome to the chat, <@{message.author.name}>")

            # If the person hasn't chatted in a while, make sure to welcome them.
            # If it's -1, then the person hasn't chatted yet.
            if previous_time + (inactive_time * 60) < current_time and previous_time != -1:
                print(f"Just welcomed a new person, {message.author.name}!")

                # Figure out the seconds between the previous time and this time.
                seconds_between: int = int(current_time - previous_time)  # Casting it to an int will remove decimal
                # points.
                minutes_between: int = int(seconds_between / 60)

                # Welcome them!
                await message.reply(random.choice(new_comer_messages).format(
                    mention=f"<@{message.author.id}>",
                    seconds=seconds_between,
                    minutes=minutes_between
                ))

            # This method will check if the users' message contains profanities.
            profanity_check: (bool, str) = contains_profanities(message.content)

            # If profanity_check[0] is True, the message contains profanities.
            if profanity_check[0]:
                # Log the message.
                print(f"Successfully caught a bad message from {message.author.name}.")

                # If the message does contain profanities, reply with one of the random messages.
                # Make sure to format the message.
                await message.reply(random.choice(profane_messages).format(
                    mention=f"<@{message.author.id}>",
                    slur=profanity_check[1]  # The second value is the slur that they used.
                ))

            # Cache the persons message.
            member_chats[message.author.id]: float = current_time

    # Finally, run a new instance of the bot.
    PenisNoduleBot().run(discord_token)


if __name__ == "__main__":
    main()
