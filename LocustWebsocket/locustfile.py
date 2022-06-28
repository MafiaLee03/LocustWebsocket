from locust import HttpUser, task
from locust.exception import RescheduleTask

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        with self.client.get("/login",catch_response = True) as response:
            if response.status_code == 404:
                print(response)
                response.success()
            else:
                print(self.__class__.__name__)
        self.client.get("/world")