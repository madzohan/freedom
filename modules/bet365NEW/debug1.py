from parseWS import basketball
import pickle
import json
with open('messages20180721印第安纳狂热vs洛杉矶火花.pickle','rb') as f:
    ms = pickle.load(f)

bb= basketball(1)
for message in ms:
    if bb.Flag:
        # print(repr(message))
        if 'HA=131.5' in message:
            print('d')
        bb.parseVC(message)

        if bb.GameOver:
            bb.save()
            break
    else:
        try:
            # print(repr(message))
            bb.parseID(message)
        except KeyError:
            continue

