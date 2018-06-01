from __future__ import absolute_import
import base64
import json
import unittest
from furl import furl
from dxlstreamingconsumerclient.channel import (Channel, ChannelAuth)
from sample import fake_consumer_service

BASE_CHANNEL_URL = "http://localhost"


class Test(unittest.TestCase):
    def test_service(self):
        with fake_consumer_service.ConsumerService(0) as service:
            channel_url = furl(BASE_CHANNEL_URL).set(port=service.port)
            with Channel(channel_url,
                         auth=ChannelAuth(
                             channel_url,
                             fake_consumer_service.AUTH_USER,
                             fake_consumer_service.AUTH_PASSWORD),
                         consumer_group=fake_consumer_service.CONSUMER_GROUP) \
                    as channel:
                channel.create()
                channel.subscribe()

                expected_records = \
                    [json.loads(base64.b64decode(
                        record['message']['payload']).decode())
                     for record in fake_consumer_service.DEFAULT_RECORDS]
                records_consumed = channel.consume()
                self.assertEqual(expected_records, records_consumed)

                channel.commit()
                self.assertEqual([], channel.consume())

                self.assertEqual(len(service._active_consumers), 1)
            self.assertEqual(len(service._active_consumers), 0)
