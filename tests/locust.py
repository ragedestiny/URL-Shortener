import random
from locust import HttpUser, task, between
from requests.exceptions import RequestException

class WebsiteUser(HttpUser):
    wait_time = between(1, 8)
    jwt_token = None
    short_urls = ["Soijwf09wf0i", "62_I2kencrLe2GP", "adofijwef98w"]

    def on_start(self):
        self.login()

    def login(self):
        form_data = {
            "username": "331@user.com",
            "password": "Password2"
        }
        try:
            response = self.client.post("/login", data=form_data)
            response.raise_for_status()  # Raise exception for non-2xx responses
            self.jwt_token = response.json().get("access_token")
        except RequestException as e:
            self.log_error("Login failed", e)

    @task
    def load_list_my_urls(self):
        try:
            self.ensure_jwt_token()
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            response = self.client.get("/list_my_urls", headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx responses
        except RequestException as e:
            self.log_error("Failed to list URLs", e)

    @task
    def load_change_password(self):
        try:
            self.ensure_jwt_token()
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            new_password_data = {"password": "Password2"}
            response = self.client.patch("/change_password", json=new_password_data, headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx responses
        except RequestException as e:
            self.log_error("Failed to change password", e)

    @task
    def load_lookupURL(self):
        try:
            shorturl = random.choice(self.short_urls)
            response = self.client.get("/lookupURL", params={"shorturl": shorturl})
            response.raise_for_status()  # Raise exception for non-2xx responses
        except RequestException as e:
            self.log_error("Failed to lookup URL", e)

    @task
    def test_redirect(self):
        try:
            shorturl = random.choice(self.short_urls)
            response = self.client.get(f"/redirect/{shorturl}")
            response.raise_for_status()  # Raise exception for non-2xx responses
            print(f"Redirect successful for short URL: {shorturl}")
        except RequestException as e:
            self.log_error(f"Redirect failed for short URL: {shorturl}", e)

    def ensure_jwt_token(self):
        if not self.jwt_token:
            self.log_error("JWT token not available")
            self.login()  # Retry login if token is missing or expired

    def log_error(self, message, exception=None):
        if exception:
            self.environment.events.request_failure.fire(
                request_type="Locust Error",
                name="Locust Error",
                response_time=0,
                exception=exception,
                response_length=0,
                response_status=0,
                message=message,
            )
        else:
            self.environment.events.request_failure.fire(
                request_type="Locust Error",
                name="Locust Error",
                response_time=0,
                exception=None,
                response_length=0,
                response_status=0,
                message=message,
            )
