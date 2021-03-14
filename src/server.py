"""The server for Pycord. Does all the heavy lifting by handling the requests
of the clients that connect to it.
"""

import sys
import logging
import settings
import utilities
import communication
import authentication
import asyncio
from discord import Client
from threading import Thread

# Extracts the token, and creates directories.
utilities.initialize()
settings_file = settings.get_settings_file()
pycord_settings = settings.extract_settings(settings_file, utilities.default_settings)
login_token = authentication.extract_token(settings_file)

DiscordClient = Client()
command_queue = []

# Logger creation
logger = utilities.new_logger("pycord-main", use_console=utilities.LOG_TO_CONSOLE)
logger.info(f"Started Pycord daemon at {utilities.get_time()}")
logger.info("Loaded settings.")
logger.info("Attempting to login...")

if login_token == "":
    logger.critical("Invalid token passed! Cannot login to Discord. Exiting.")
    sys.exit(1)


def handle_queue(server: communication.Listener):
    """Handles requests to the server.
    """

    while True:
        connection = server.accept()
        command_queue.append((connection, connection.recv()))


@DiscordClient.event
async def on_ready():
    full_name = f"{DiscordClient.user.name}#{DiscordClient.user.discriminator}"
    logger.info(f"Successfully logged into Discord as: {full_name}")

    # Starts the request queue
    server = communication.create_server()
    Thread(target=handle_queue, args=(server,)).start() 

    # Handle the Queue.
    while True:
        if len(command_queue) > 0:
            connection, command = command_queue.pop(0)
            connection.close()
            print("Closing connection!")
        await asyncio.sleep(0.5)


@DiscordClient.event
async def on_message(message):
    print(f"New message: {message}")

    # Check if this new message is in the currently selected
    # channel, and if it is, add it to the cached-message list.
    # also redraw the window.


DiscordClient.run(login_token, bot=False)
