import os
import json
from random import random, randint
from tempfile import TemporaryFile

import requests


class QualiAPISession:
    def __init__(self, host, username='', password='', token='', domain='Global', port=9000):
        self._api_base_url = "http://{}:{}/Api".format(host, port)
        self._session = requests.session()
        self.login(username, password, token, domain)

    def login(self, username, password, token, domain):
        if token:
            headers = {"token": token, "domain": domain}
        elif username and password:
            headers = {"username": username, "password": password, "domain": domain}
        else:
            raise ValueError("Must supply Username / Password OR token_id")

        login_result = requests.put(f"{self._api_base_url}/Auth/Login", headers)
        if not login_result.ok:
            raise Exception("Invalid status on login. Status - {}. {}".format(login_result.status_code,
                                                                              login_result.text))

        # strip the extraneous quotes
        token_str = login_result.text[1:-1]
        self._session.headers.update({"Authorization": f"Basic {token_str}"})

    def attach_file_to_reservation(self, sandbox_id: str, target_filename="sandbox_file", data_str="", disk_file_path="",
                                   overwrite_if_exists=True):
        """
        Attach a file to a Sandbox
        """
        payload = {"reservationId": sandbox_id,
                   "saveFileAs": target_filename,
                   "overwriteIfExists": overwrite_if_exists}

        if disk_file_path:
            with open(disk_file_path, "rb") as f:
                self._send_attach_request(payload, f)
        elif data_str:
            tmp_file_name = f"temp_{randint(1,5000)}"
            with open(tmp_file_name, "w") as f:
                f.write(data_str)

            with open(tmp_file_name, "rb") as f:
                self._send_attach_request(payload, f)
            os.remove(tmp_file_name)
        else:
            raise ValueError("Either data string or file path must be specified")

    def _send_attach_request(self, payload, attached_file):
        response = self._session.post(f"{self._api_base_url}/Package/AttachFileToReservation",
                                      data=payload,
                                      files={'QualiPackage': attached_file})
        if not response.ok:
            raise Exception(f"Failed to attach file. Response code: {response.status_code}. Reason: {response.reason}")

        if not json.loads(response.text)["Success"]:
            raise Exception(f"Failed Attach operation:\n{json.dumps(response.text, indent=4)}")


if __name__ == "__main__":
    SANDBOX_ID = "cf8ccf01-f349-4636-950a-d4fc5e5bbd91"
    api = QualiAPISession("localhost", "admin", "admin")
    # api.attach_file_to_reservation(SANDBOX_ID, "", "q.txt", "test.txt")
    api.attach_file_to_reservation(SANDBOX_ID, "datatest.txt", "heyooooo")