import json
from pathlib import Path

import requests

from .atlassian_api import AtlassianServerAPI, AtlassianServerAPIHeaders


class JiraServer(AtlassianServerAPI):
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        session: requests.Session | None = None,
    ) -> None:
        super().__init__(url, username, password, session)

    def upload_plugin(self, plugin_path: Path) -> dict:
        self.logger.info(f"Uploading plugin '{plugin_path}' to instance.")
        files = {"plugin": open(plugin_path, "rb")}
        upm_token = self.request(
            method="GET",
            path="/rest/plugins/1.0/",
            headers=AtlassianServerAPIHeaders.NO_CHECK,
        ).headers["upm-token"]
        res = self.request(
            method="POST",
            path=f"/rest/plugins/1.0/?token={upm_token}",
            headers=AtlassianServerAPIHeaders.NO_CHECK,
            files=files,
        )
        self.logger.debug(f"Upload plugin response: {res.status_code} | {res.text}")
        res.raise_for_status()
        if res.status_code != 202:
            self.logger.error(f"Unable to upload plugin.")
            raise Exception(f"")

        data = res.text
        # This API response can have redundant textarea tag wrapping json data
        data = data.replace("<textarea>", "")
        data = data.replace("</textarea>", "")
        return json.loads(data)

    def get_plugin_pending_tasks(self) -> list:
        self.logger.info(f"Getting pending tasks...")
        res = self.request(
            method="GET",
            headers=AtlassianServerAPIHeaders.DEFAULT,
            path="/rest/plugins/1.0/",
        )
        res.raise_for_status()
        data_json = res.json()
        return data_json["tasks"]

    def get_plugin_pending_task_info(self, task_id: str) -> dict:
        self.logger.info(f"Getting plugin pending task info for task id: {task_id}")
        res = self.request(
            method="GET",
            headers=AtlassianServerAPIHeaders.DEFAULT,
            path=f"/rest/plugins/1.0/pending/{task_id}",
            allow_redirects=False,
        )
        res.raise_for_status()

        if 300 <= res.status_code < 400:
            redirect_url = res.headers["Location"]
            self.logger.info(
                f"Plugin task {task_id} is done, redirecting to: {redirect_url}"
            )
            res = self.request(
                method="GET",
                headers=AtlassianServerAPIHeaders.NO_CHECK,
                url=redirect_url,
            )
            res.raise_for_status()

        res_json = res.json()

        # "status" is from task info
        # "key" is from plugin info, redirected from task
        # if none applied, need to handle later -> TBD
        if "status" not in res_json and "key" not in res_json:
            msg = f"Task {task_id} has unexpected response: {res_json}"
            self.logger.error(msg)
            raise ValueError(msg)

        return res_json
