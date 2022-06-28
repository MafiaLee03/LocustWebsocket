from locust import task
from Core.WebSocketIO import SocketIOUser
import time

class testuser(SocketIOUser):

    @task(3)
    def hello_word(self):
        body = {
            'server_id':10000,
            'request':{'hello':'word'},
            'uid':time.time(),
            'code':100
            }
        self.send(body,'注册请求')
        self.sleep_with_heartbeat(2)

    @task(2)
    def hello_word2(self):
        body = {
            'server_id':20000,
            'request':{'hello':'word'},
            'uid':time.time(),
            'code':200
            }
        self.send(body,'登录请求')
        self.sleep_with_heartbeat(2)