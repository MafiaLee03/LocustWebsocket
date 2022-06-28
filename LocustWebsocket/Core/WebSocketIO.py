from http import server
import json
import logging
import re
import time
import gevent
import websocket
from locust import User

SERVER_ID_TRANSLATE = {
    10000:'测试用注册',
    20000:'测试用登录',
    30000:'心跳'
}

class SocketIOUser(User):
    """
    A locust that includes a socket io websocket connection.
    You could easily use this a template for plain WebSockets,
    socket.io just happens to be my use case. You can use multiple
    inheritance to combine this with an HttpUser
    (class MyUser(HttpUser, SocketIOUser)
    """

    abstract = True
    message_regex = re.compile(r"(\d*)(.*)")
    description_regex = re.compile(r"<([0-9]+)>$")

    def __init__(self, environment):
        super().__init__(environment)
        self.host = 'ws://localhost:8765/'

    def connect(self, host: str, header=[]):
        self.ws = websocket.create_connection(host, header=header)
        gevent.spawn(self.receive_loop)

    def on_message(self, message):  # override this method in your subclass for custom handling
        # m = self.message_regex.match(message)
        try:
            m = json.loads(message)
        except:
            raise Exception('json.loads失败,接收消息不是json格式\n{}'.format(message))
        response_time = 0  # unknown
        # if m is None:
        #     # uh oh...
        #     raise Exception(f"got no matches for {self.message_regex} in {message}")

        server_id = m['server_id']
        json_dict = m['request']
        code = m['code']
        if server_id in SERVER_ID_TRANSLATE.keys():
            name = SERVER_ID_TRANSLATE[server_id]
        else:
            name = server_id

        if code != 200:
            self.environment.runner.stats.log_error('response',name,code)
        if server_id != 30000:
            current_timestamp = time.time()
            # obj = json.loads(json_string)
            # logging.debug(json_string)
            # ts_type, payload = obj
            # name = f"{code} {ts_type} apiUri: {payload['apiUri']}"

            if 'uid' in m.keys():
                sent_timestamp = int(m['uid'])
                response_time = current_timestamp - sent_timestamp
            else:
                name += "_missingTimestamp"
        # else:
        #     print(f"Received unexpected message: {message}")
        #     return
        self.environment.events.request.fire(
            request_type="response",
            name=name,
            response_time=response_time,
            response_length=len(message),
            exception=None,
            context=self.context(),
        )

    def receive_loop(self):
        while True:
            message = self.ws.recv()
            logging.debug(f"response: {message}")
            self.on_message(message)

    def send(self, body, name=None, context={}):
        if not name:
            if body['server_id'] == 30000:
                name = '心跳'
            else:
                name = body['server_id']
        body = json.dumps(body)
        self.environment.events.request.fire(
            request_type="request",
            name=name,
            response_time=None,
            response_length=len(body),
            exception=None,
            context={**self.context(), **context},
        )
        logging.debug(f"request: {body}")
        self.ws.send(body)

    def sleep_with_heartbeat(self, seconds):
        body = {
            'server_id':30000,
            'request':'',
            'uid':time.time(),
            'code':200
            }
        while seconds >= 0:
            gevent.sleep(min(15, seconds))
            seconds -= 15
            self.send(body)

    def on_start(self):
        self.connect(self.host)