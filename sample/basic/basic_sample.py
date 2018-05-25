from __future__ import absolute_import
import json
import os
import sys
import time

from dxldbconsumerclient.channel import Channel, ChannelAuth, ConsumerError
from dxldbconsumerclient import globals

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir + "/../..")
sys.path.append(root_dir + "/..")

# Import common logging and configuration
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

CHANNEL_URL = "http://127.0.0.1:5000"
CHANNEL_USERNAME = "me"
CHANNEL_PASSWORD = "secret"
CHANNEL_CONSUMER_GROUP = "mcafee_investigator_events"
WAIT_BETWEEN_QUERIES = 5

channel = Channel(CHANNEL_URL,
                  auth=ChannelAuth(CHANNEL_URL,
                                   CHANNEL_USERNAME,
                                   CHANNEL_PASSWORD),
                  consumer_group=CHANNEL_CONSUMER_GROUP)

logger.info("Starting event loop")
while not globals.interrupted:
    # loop over the channel and wait for events
    channel.create()
    channel.subscribe()

    consumer_error = False
    while not consumer_error and not globals.interrupted:
        try:
            records = channel.consume()
            logger.info("Consumed records: \n%s",
                        json.dumps(records, indent=4, sort_keys=True))
            channel.commit()
            time.sleep(WAIT_BETWEEN_QUERIES)
        except ConsumerError as exp:
            logger.error("Resetting consumer loop: %s", exp)
            consumer_error = True

logger.info("Unsubscribing and deleting consumer")
try:
    channel.unsubscribe()
    channel.delete()
except Exception as exp:
    logger.warning(
        "Error while attempting to unsubscribe and stop "
        "consumer with ID '%s': %s", channel.consumer_id, exp)