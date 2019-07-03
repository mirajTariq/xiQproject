import os
import sys, traceback

from aiohttp import web
import socketio
import datetime
import logging
import json
import ssl
import urllib.parse


logger = logging.getLogger('socketServer')

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

personDict = {}
person_parse_time_log = {}

def is_process_running(file_name):
    is_running = False
    count = 0
    for line in os.popen("ps -aux"):
        if '/bin/sh' not in line and 'sudo' in line and file_name in line:
            count += 1
    if count > 1:
        is_running = True
    return is_running

async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


#********************************************HTTP*******************************************

@sio.on('message')
async def print_message(sid, message):
    # print("Socket ID: " , sid)
    # print(message['profileID'])
    # logger.info('MESSAGE IS: ' + message)
    # print(app.logger())
    # await a successful emit of our reversed message
    # back to the client
    await sio.emit('clientMessage', message['msg'], room=sid)


@sio.on('connect')
async def connect(sid, environ):
    logger.info('connect ' + str(sid))
    print('connect ', sid)
    if environ:
        print('TYPE: ' + str(type(environ)))
        print(environ)

        print('ENVIRONMENT VARIABLE: ' + str(environ['QUERY_STRING']))
        decoded_env_data = urllib.parse.unquote(environ['QUERY_STRING'])
        print('DECODED DATA: ' + str(decoded_env_data))
        env_list = str(decoded_env_data).split('&')
        username = env_list[2][9:]
        identifier = env_list[3][11:]
        print('USERNAME: ' + str(username))
        print('IDENTIFIER: ' + str(identifier))

        # for a in env_list:
        #     print(a)
    # logger.info('connection environment: ' + str(environ))
    # print('connection environment: ' + str())

@sio.on('disconnect')
async def disconnect(sid):
    logger.info('disconnect ' +  str(sid))
    print('disconnect ', sid)


@sio.on('person_data')
async def pushNotification(sid, data):
    room_name = str(data['personid']) + '_room'
    # await print('CREATED ROOM [' + str(room_name) + ']')
    print('created room [' + str(room_name) + ']')

    # await print('PERSON HAVING ID [' + str(data['personid']) + '] AND RESPONSE ID [' + str(data['responseid']) + '] HAS BEEN PARSED')
    print('person having id [' + str(data['personid']) + '] and response id [' + str(data['responseid']) + '] has been parsed')

    try:
        if str(data['personid']) in personDict:
            for x in personDict[str(data['personid' ])]:
                sio.enter_room(x, room_name)

            await sio.emit('profileready', json.dumps(data), room=room_name)
            # await print('PARSED DATA HAS BEEN SENT TO THE CLIENT')
            print('parsed data has been sent to the client')

            del personDict[str(data['personid'])]

            if str(data['personid']) in personDict:
                # await print('PERSON ID NOT DELETED FROM DICTIONARY')
                print('person id not deleted from dictionary')
            else:
                # await print('PERSON ID DELETED FROM DICTIONARY')
                print('person id delted from dictionary')
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    await sio.close_room(room_name)
    await sio.disconnect(sid)



@sio.on('searchperson')
def populateDict(sid, data):
    print('session id: {' + str(sid) + '} request for person having id: {' + str(data['personid']) + '} and response id: {' +  '}')
    print('Person dict length: ' + str(len(personDict)))

    if str(data['personid']) not in personDict:
        personDict[str(data['personid'])] = [sid]
    else:
        if str(sid) not in personDict[str(data['personid'])]:
            personDict[str(data['personid'])].append(sid)


# **************************************HTTPS***************************************

sioS = socketio.AsyncServer()
appS = web.Application()
sioS.attach(appS)

@sioS.on('message')
async def print_message(sid, message):
    # print("Socket ID: " , sid)
    # print(message['profileID'])
    # logger.info('MESSAGE IS: ' + message)
    # print(app.logger())
    # await a successful emit of our reversed message
    # back to the client
    print(message)
    await sioS.emit('clientMessage', message['msg'], room=sid)


@sioS.on('connect')
async def connect(sid, environ):
    print()
    print()
    print()
    username = ''
    identifier = ''

    # logger.info('connect ' + str(sid))
    print('CONNECT|    SID: ', sid)
    print('CONNECT|    ENVIRONMENT VARIABLES: ' + str(environ))

    decoded_env_data = urllib.parse.unquote(environ['QUERY_STRING'])
    env_list = str(decoded_env_data).split('&')

    for var in env_list:
        if 'username' in str(var):
            username = var[9:]
            print('CONNECT|    USERNAME: ' + str(username))
        if 'identifier' in str(var):
            identifier = var[11:]
            print('CONNECT|    IDENTIFIER: ' + str(identifier))

    user_key = username + '|' + identifier
    user_key_exist = 0

    for key, val in personDict.items():
        for k, v in val.items():
            if k == user_key:
                val[k] = sid
                user_key_exist = 1
                print('CONNECT|    USER ALREADY EXIST IN PERSON DICT - ' + str(user_key))

    if user_key_exist == 0:
        print('CONNECT|    USER DOES NOT EXIST IN PERSON DICT - ' + str(user_key))



    # logger.info('connection environment: ' + str(environ))
    # print('connection environment: ' + str())

@sioS.on('disconnect')
async def disconnect(sid):
    print()
    print()
    print()
    # logger.info('disconnect ' +  str(sid))
    print('DISCONNECT|    SID: ', sid)


@sioS.on('person_data')
async def pushNotification(sid, data):
    print()
    print()
    print()
    print('NEW_PERSON_DATA|    NEW PERSON PROFILE DATA RECEIVED')
    room_name = str(data['personid']) + '_room'
    # await print('CREATED ROOM [' + str(room_name) + ']')
    print('NEW_PERSON_DATA|    CREATED ROOM [' + str(room_name) + ']')

    # await print('PERSON HAVING ID [' + str(data['personid']) + '] AND RESPONSE ID [' + str(data['responseid']) + '] HAS BEEN PARSED')
    print("NEW_PERSON_DATA|    PERSON'S PROFILE HAVING ID [" + str(data['personid']) + "] HAS BEEN PARSED")

    person_parse_time_log[str(data['personid'])]['end_time'] = datetime.datetime.now()
    print('NEW_PERSON_DATA|    TIME TAKEN BY NEW PERSON "' + str(data['personid']) + '" PARSE IS: ' + str(person_parse_time_log[str(data['personid'])]['end_time'] - person_parse_time_log[str(data['personid'])]['start_time']))

    try:
        if str(data['personid']) in personDict:
            for key, val in personDict[str(data['personid'])].items():
                sioS.enter_room(val, room_name)

            await sioS.emit('profileready', json.dumps(data), room=room_name)
            # await print('PARSED DATA HAS BEEN SENT TO THE CLIENT')
            print('NEW_PERSON_DATA|    PARSED DATA HAS BEEN SENT TO REGISTERED SIDS')

            del personDict[str(data['personid'])]

            if str(data['personid']) in personDict:
                # await print('PERSON ID NOT DELETED FROM DICTIONARY')
                print('NEW_PERSON_DATA|    PERSON ID NOT DELETED FROM DICTIONARY')
            else:
                # await print('PERSON ID DELETED FROM DICTIONARY')
                print('NEW_PERSON_DATA|    PERSON ID DELETED FROM DICTIONARY')
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    await sioS.close_room(room_name)
    await sioS.disconnect(sid)


@sioS.on('searchperson')
def populateDict(sid, data):
    print()
    print()
    print()
    print('SEARCHPERSON|    NEW PERSON PROFILE REQUEST RECEIVED')
    print('SEARCHPERSON|    SESSION ID: {' + str(sid) + '} REQUEST FOR PERSON HAVING ID: {' + str(data['personid']) + '}')
    print('SEARCHPERSON|    PERSON DICT LENGTH: ' + str(len(personDict)))
    print('SEARCHPERSON|    SIDS FOR PERSON [' + str(data['personid']) + '] ARE: ' + str(len(personDict[str(data['personid'])])))

    if str(data['personid']) not in person_parse_time_log:
        person_parse_time_log[str(data['personid'])] = {}
        person_parse_time_log[str(data['personid'])]['start_time'] = datetime.datetime.now()

    user_key = str(data['username']) + '|' + str(data['identifier'])

    if str(data['personid']) not in personDict:
        # personDict[str(data['personid'])] = [sid]
        personDict[str(data['personid'])] = {}
        personDict[str(data['personid'])][user_key] = sid
    else:
        if user_key not in personDict[str(data['personid'])]:
            personDict[str(data['personid'])][user_key] = sid

    # await sioS.emit('profileready', json.dumps(testDict), room=sid)







@sioS.on('refresh_data')
async def pushNotification(sid, data):
    print()
    print()
    print()
    print('REFRESH_PERSON_DATA|    PERSON REFRESH DATA RECEIVED')
    room_name = str(data['personid']) + '_room'
    # await print('CREATED ROOM [' + str(room_name) + ']')
    print('REFRESH_PERSON_DATA|    CREATED ROOM [' + str(room_name) + ']')

    # await print('PERSON HAVING ID [' + str(data['personid']) + '] AND RESPONSE ID [' + str(data['responseid']) + '] HAS BEEN PARSED')
    print("REFRESH_PERSON_DATA|    PERSON HAVING ID [" + str(data['personid']) + "] HAS BEEN PARSED")

    person_parse_time_log[str(data['personid'])]['end_time'] = datetime.datetime.now()
    print('REFRESH_PERSON_DATA|    TIME TAKEN BY REFRESH PERSON "' + str(data['personid']) + '" IS: ' + str(
        person_parse_time_log[str(data['personid'])]['end_time'] - person_parse_time_log[str(data['personid'])][
            'start_time']))

    try:
        if str(data['personid']) in personDict:
            for key, val in personDict[str(data['personid'])].items():
                sioS.enter_room(val, room_name)

            await sioS.emit('refreshprofileready', json.dumps(data), room=room_name)
            # await print('PARSED DATA HAS BEEN SENT TO THE CLIENT')
            print('REFRESH_PERSON_DATA|    PARSED DATA HAS BEEN SENT TO THE CLIENTS')

            del personDict[str(data['personid'])]

            if str(data['personid']) in personDict:
                # await print('PERSON ID NOT DELETED FROM DICTIONARY')
                print('REFRESH_PERSON_DATA|    PERSON ID NOT DELETED FROM DICTIONARY')
            else:
                # await print('PERSON ID DELETED FROM DICTIONARY')
                print('REFRESH_PERSON_DATA|    PERSON ID DELETED FROM DICTIONARY')
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    await sioS.close_room(room_name)
    await sioS.disconnect(sid)


@sioS.on('refreshperson')
def populateDict(sid, data):
    print()
    print()
    print()
    print('REFRESHPERSON|    PERSON REFRESH REQUEST RECEIVED')
    # print('DATA: ' + str(data))
    print('REFRESHPERSON|    SESSION ID: {' + str(sid) + '} REQUEST FOR PERSON HAVING ID: {' + str(data['personid']) + '}')
    print('REFRESHPERSON|    PERSON DICT LENGTH: ' + str(len(personDict)))
    print('REFRESHPERSON|    SIDS FOR PERSON [' + str(data['personid']) + '] ARE: ' + str(
        len(personDict[str(data['personid'])])))

    if str(data['personid']) not in person_parse_time_log:
        person_parse_time_log[str(data['personid'])] = {}
        person_parse_time_log[str(data['personid'])]['start_time'] = datetime.datetime.now()

    user_key = str(data['username']) + '|' + str(data['identifier'])

    if str(data['personid']) not in personDict:
        # personDict[str(data['personid'])] = [sid]
        personDict[str(data['personid'])] = {}
        personDict[str(data['personid'])][user_key] = sid
    else:
        if str(sid) not in personDict[str(data['personid'])]:
            # personDict[str(data['personid'])].append(sid)
            personDict[str(data['personid'])][user_key] = sid


def http_socket_server():
    app.router.add_get('/', index)
    web.run_app(app, port=27017)



def https_socket_server():
    # appS.router.add_get('/', index)
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('star_xiq_io.crt', 'xiq_io.key')

    web.run_app(appS, port=27018, ssl_context=ssl_context)

def start_socket():
    try:
        if is_process_running(__file__):
            print('SOCKET IS ALREADY RUNNING')
        else:
            # print('STARTING HTTP SOCKET SERVER')
            # http_socket_server()
            print('STARTING HTTPS SOCKET SERVER')
            https_socket_server()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))


start_socket()



























async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        await sio.emit('serverMessage', 'Current Time: ' + str(datetime.datetime.now()))




# @sio.on('connect')
# async def authenticateUser(sid, data):
#     authenticationStatus = verifyUser(data['username'], data['token'])
#
#     if not authenticateUser:
#         sio.disconnect(sid)





# @sio.on('testmessage')
# def testFunction(sid, data):
#     logger.info('Session ID: ' + str(sid))
#     logger.info('Message: ' + str(data))
#     print('Session ID: ' + str(sid))
#     print('Message: ' + str(data))

# async def background_task():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         await sio.sleep(10)
#         await sio.emit('serverMessage', 'Current Time: ' + str(datetime.datetime.now()))