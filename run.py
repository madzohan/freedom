from sys import argv
from twisted.internet import reactor
import re
import time
from modules import diffusion
from modules.parseWS import basketball
from twisted.python import log
from twisted.internet import reactor
import redis
from multiprocessing import Process, Pipe
import time, threading
import psutil


def main(id,it):
    topic = [
        '__host',
        'CONFIG_1_3',
        'Media_l1_Z3',
        'OVInPlay_1_3',
        'XL_L1_Z3_C1_W1',
    ]
    topic.append(id)
    topic.append(it)
    bet365_game(topic)
    # for cell in messages:
    #     ids= bytes.decode(cell).split('@')[:2]
    #     topics = topic+ids
    #     bb = basketball()
    #     bet365_game(topics)
    reactor.run()
    return



def bet365_game(topics):

    diffusion_client = diffusion.DiffusionClient(
        'wss://premws-pt1.365lpodds.com/zap/',
        trigger ='1',
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


if __name__ == '__main__':
    r = redis.Redis(host='127.0.0.1', port=6379)
    past = []
    while True:
        ms = list(r.smembers('messages'))
        update = [x for x in ms if x not in past]
        process =[]
        if update !=[]:
            for cell in update:
                parent_conn, child_conn = Pipe()
                ids = bytes.decode(cell).split('@')
                id = ids[0]
                it = ids[1]
                p = Process(target=main, args=(id, it))
                print('Child process will start.')
                print(cell)
                p.start()
                process.append(p)
            time.sleep(120)
            past = ms
        for p in process:
            print('process is alive', p.is_alive())


