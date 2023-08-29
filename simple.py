from locust import FastHttpUser, between, task


class WebsiteUser(FastHttpUser):
    wait_time = between(2, 3)

    @task
    def root(self):
        self.client.get("/")
