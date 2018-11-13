from sys import argv
from twisted.internet import reactor
import re
import datetime
import time
from modules import diffusion
from modules.parseWS import basketball
from twisted.python import log
from twisted.internet import reactor
import redis
import subprocess
import os
import run
from multiprocessing import Process
class game_update(diffusion.DiffusionClient):
    def _get_factory(self):
        factory = diffusion.DiffusionFactory(
            self._connection_url,
            headers=self._headers,
            protocols=self._get_protocols(),
            useragent=self._USER_AGENT,
        )

        factory.message_handler = self._message_handler
        factory.trigger = self._trigger
        factory.session_id = self._session_id
        factory.protocol = myDiffusionProtocol
        factory.topics = self._topics

        factory.setProtocolOptions(perMessageCompressionAccept=self._accept)
        factory.setProtocolOptions(perMessageCompressionOffers=[self._get_offer()])

        return factory

class myDiffusionProtocol(diffusion.DiffusionProtocol):
    r = redis.Redis(host='127.0.0.1', port=6379)
    def onMessage(self, payload, isBinary):
        self.factory.message_handler.pre_message()
        log.msg('received messages: %s', repr(payload))
        messages = bytes.decode(payload).split(self._DELIMITERS_MESSAGE)
        while len(messages):
            message = messages.pop()
            type = message[0]
            if type == self.factory.trigger:
                for topic in self.factory.topics:
                    self._send(self._MESSAGES_SUBSCRIPTION % topic)
                    self.Flag = True
                continue
            elif '\x14OVInPlay' in message[:10] and self.Flag:
                bb=basketball()
                games = bb.parse_OVInPlay(message)
                past = self.r.smembers('messages')
                past_str = set([x.decode() for x in past])
                for value in past:
                    self.r.srem('messages', value)
                now = set()
                for cell in games:
                    self.r.sadd('messages',cell['messages'])
                    self.r.sadd('games', cell['games'])
                    now.add(cell['messages'])
                update = now - past_str
                for cell in update:
                    self.r.sadd('update',cell)
                for cell in self.r.smembers('update'):
                    self.r.srem('update',cell)
                # self._send(self._MESSAGES_SUBSCRIPTION % 'OVInPlay_1_3')


def main(options):

    topic_2 = [
        '__host',
        'CONFIG_1_3',
        'Media_l1_Z3',
        'OVInPlay_1_3',
        'XL_L1_Z3_C1_W1',
    ]

    bet365(topic_2)
    reactor.run()
    return

def bet365(topics):

    diffusion_client = game_update(
        'wss://premws-pt1.365lpodds.com/zap/',
        trigger = '1',
        # session_url='https://www.288365.com/',
        session_url='https://www.348365365.com',
        protocol='zap-protocol-v1',
        headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',

    },
        topics=topics,
    )
    if diffusion_client.can_connect():
        try:
            diffusion_client.connect()
        except KeyboardInterrupt:
            diffusion_client.disconnect()
        except Exception:
            diffusion_client.disconnect()



def bet365_game(topics):

    diffusion_client = diffusion.DiffusionClient(
        'wss://premws-pt1.365lpodds.com/zap/',
        trigger ='1',
        # session_url='https://www.288365.com/',
        session_url='https://www.635288.com/',
        protocol='zap-protocol-v1',
        headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',

    },
        topics=topics,
    )
    if diffusion_client.can_connect():
        try:
            diffusion_client.connect()
        except KeyboardInterrupt:
            diffusion_client.disconnect()
        except Exception:
            diffusion_client.disconnect()



main(argv)

