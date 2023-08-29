from locust import between, events, task
from locust.contrib.fasthttp import FastHttpUser

import common.rate_limiter


def logout_user(user_instance):
    headers = {"Authorization": f"Bearer {user_instance.token}"}
    user_instance.client.post("/auth/token/logout", headers=headers)


logout_rate_limiter = common.rate_limiter.RateLimiter(25)


class WebsiteUser(FastHttpUser):
    wait_time = between(2, 3)
    token = ""

    def on_start(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.client.post(
            "/auth/token/login",
            {
                "username": "admin@example.com",
                "password": "password",
            },
            headers=headers,
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]

    def on_stop(self):
        logout_rate_limiter.limit(logout_user, self)

    @task(1)
    def root(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.client.get("/", headers=headers)

    @task(1)
    def get_users_me(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.client.get("/users/me", headers=headers)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    for user in environment.runner.user_greenlets:
        user.user_instance.on_stop()
