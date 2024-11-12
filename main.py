import re
import time
from typing import Tuple
from httpx import Client


class RouterManager:
    def __init__(self, client: Client):
        self.client = client

    def extract_captcha_and_csrf(self) -> Tuple[str, str]:
        response = self.client.get("http://192.168.1.1/admin/login.asp").text
        captcha = re.search(
            r"document\.getElementById\('check_code'\)\.value='(.*?)'", response
        )
        csrf = re.search(r"name='csrftoken' value='(.*?)'", response)

        if not captcha or not csrf:
            raise ValueError("Could not find captcha or CSRF token.")

        return captcha.group(1), csrf.group(1)

    def login(self, captcha: str, csrf_token: str) -> None:
        response = self.client.post(
            "http://192.168.1.1/boaform/admin/formLogin",
            data={
                "username1": "admin",
                "psd1": "admin@123",
                "verification_code": captcha,
                "username": "admin",
                "psd": "admin@123",
                "sec_lang": "0",
                "loginSelinit": "",
                "ismobile": "",
                "csrftoken": csrf_token,
            },
        )
        print("Login Response:", response.text)

    def get_dev_csrf_token(self) -> str:
        response = self.client.get("http://192.168.1.1/mgm_dev_reboot.asp").text
        csrf = re.search(r"name='csrftoken' value='(.*?)'", response)

        if not csrf:
            raise ValueError("Could not find CSRF token.")

        return csrf.group(1)

    def reboot_wlan(self, csrf_token: str) -> None:
        response = self.client.post(
            "http://192.168.1.1/boaform/admin/formReboot",
            data={
                "submit-url": "/mgm_dev_reboot.asp",
                "csrftoken": csrf_token,
            },
        )
        print("Reboot Response:", response.text)


def main():
    client = Client(follow_redirects=True)
    router_manager = RouterManager(client)

    while True:
        try:
            captcha, csrf_token = router_manager.extract_captcha_and_csrf()
            print("Captcha Value:", captcha)
            print("CSRF Token:", csrf_token)

            router_manager.login(captcha, csrf_token)

            dev_csrf_token = router_manager.get_dev_csrf_token()
            print("Dev CSRF Token:", dev_csrf_token)

            router_manager.reboot_wlan(dev_csrf_token)

        except Exception as e:
            print("Error:", e)

        time.sleep(10)


if __name__ == "__main__":
    main()
