from locust import HttpLocust, HttpUser,TaskSet,task,User


class MyUser(User):
    pass

class UserBehavior(HttpUser):
    "Locust任务集,定义每个locust的行为"
    def on_start(self):
        self.client.post("/login",{
            "username":"test",
            "password":"123456"
        })
        return super().on_start()
    @task(1)
    def get_root(self):
        response = self.client.get('/Hello',name = 'get_root')
        if not response.ok:
            print(response.text)
            response.failure('Got wrong response')

class TestLocust(HttpLocust):
    """自定义Locust类 可设置Locust参数"""
    task_set = UserBehavior
    host = "https://www.baidu.com"
    min_wait = 5000 #最小等待时间 即最少等待多少秒后Locust选择执行一个任务
    max_wait = 9000 #最大等待时间 即……