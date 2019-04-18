from aiohttp import web
import socketio
import datetime
import json
from collections import defaultdict

import base64
from urllib import parse as urlparse


# def Verify(username = "", token = "", by_pass_activation = False):
#     if len(token) >= 35:
#         encryption_key = config('ENCRYPTION_KEY')
#         if not encryption_key:
#             return False
#         token = TokenDecrypt(token, encryption_key)
#         if not token:
#             return False
#     p1 = User.objects.filter(username = username, token = token)
#     if not by_pass_activation:
#         p1 = p1.filter(activestatus=1)
#     if len(p1):
#         if p1[0].isdeleted:
#             return False
#         return True
#     else:
#         p1 = User.objects.filter(fullname = username, token = token)
#         if not by_pass_activation:
#             p1 = p1.filter(activestatus=1)
#         if len(p1):
#             if p1[0].isdeleted:
#                 return False
#             return True
#         return False
#
#
# def TokenDecrypt(key, encryption_key):
#     try:
#         key = urlparse.unquote(key)
#         cipher = AES.new(encryption_key.encode(), AES.MODE_ECB)
#         decoded = cipher.decrypt(base64.b64decode(key.encode())).decode()
#         decoded = decoded.split("~")
#         token = decoded[1]
#         return token
#     except Exception:
#         exc_type, exc_value, exc_traceback = sys.exc_info()
#         logger.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
#     return None


sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        await sio.emit('serverMessage', 'Current Time: ' + str(datetime.datetime.now()))


async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

# @sio.on('connect')
# async def authenticateUser(sid, data):
#     authenticationStatus = verifyUser(data['username'], data['token'])
#
#     if not authenticateUser:
#         sio.disconnect(sid)


@sio.on('message')
async def print_message(sid, message):
    # print("Socket ID: " , sid)
    # print(message['profileID'])
    # logger.info('MESSAGE IS: ' + message)
    # print(app.logger())
    # await a successful emit of our reversed message
    # back to the client
    await sio.emit('clientMessage', message['msg'], room=sid)

personDict = defaultdict(list)


@sio.on('person_data')
async def pushNotification(sid, data):
    for ls, dt in personDict:
        print(dt)

    room_name = str(data['personid']) + '_room'
    print('Response id: ' + str(data['responseid']))
    print('Person id: ' + str(data['personid']))
    print('creating room: ' + room_name)
    print('sending notification for person: {' + str(data['personid']) + '} to ' + str(len(personDict[data['personid']])) + ' sessions')

    print("Current person session ids list: " + str(personDict[data['personid']]))

    for x in personDict[data['personid']]:
        sio.enter_room(x, room_name)

    await sio.emit('profileready', data, room=room_name)
    del personDict[data['personid']]

    print('closing room: ' + room_name)
    await sio.close_room(room_name)


    # print()
    # print('Response ID: ' + str(data['response_id']))
    await sio.disconnect(sid)


@sio.on('searchperson')
async def populateDict(sid, data):
    print('session id: {' + str(sid) + '} request for person having id: {' + str(data['personid']) + '}')
    personDict[data['personid']].append(sid)



# async def background_task():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         await sio.sleep(10)
#         await sio.emit('serverMessage', 'Current Time: ' + str(datetime.datetime.now()))

app.router.add_get('/', index)

# We kick off our server
if __name__ == '__main__':
    sio.start_background_task(background_task)
    web.run_app(app, port=27017)