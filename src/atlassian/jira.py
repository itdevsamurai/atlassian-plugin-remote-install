import json
import re
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
        self.version = self._get_jira_version()

    def _get_jira_version(self) -> str | None:
        try:
            res = self.request(
                method="GET",
                path="/secure/AboutPage.jspa",
            )
            self.logger.debug(f"Getting Jira version: {res.status_code} | {res.text}")
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code
            handled_err_code = {
                401: "Invalid username/password",
                403: "Forbidden to view the page or instance is protected by CAPTCHA.",
            }
            if status_code in handled_err_code.keys():
                msg = f"Error {status_code}: {handled_err_code[status_code]}"
                self.logger.error(msg)
                raise Exception(msg)
            self.logger.error(f"Error getting Jira version: {status_code}")
            raise err

        except requests.exceptions.ConnectionError:
            return None
        version_regex = re.search(r"<h3>Jira v([\d\.]+)<\/h3>", res.text)
        if version_regex is None:
            return None
        return version_regex.group(1)

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
            msg = f"Unable to upload plugin. Response: {res.status_code} | {res.text}"
            self.logger.error(msg)
            raise Exception(msg)

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

    def get_plugin_marketplace_info(self, plugin_key: str) -> dict:
        self.logger.info(f"Getting marketplace info for plugin '{plugin_key}'")
        res = self.request(
            method="GET",
            path=f"/rest/plugins/1.0/{plugin_key}/marketplace",
            headers=AtlassianServerAPIHeaders.NO_CHECK,
        )
        self.logger.debug(
            f"Getting marketplace info of plugin {plugin_key}: "
            f"{res.status_code} | {res.text}"
        )
        res.raise_for_status()
        return res.json()

    def remove_plugin(self, plugin_key: str) -> bool:
        """Remove plugin from server instance

        Remove plugin from server instance using api, retry if fails

        Args:
            plugin_key (str): Or App key, available on App manage setting

        Returns:
            bool: status

        Raises:
            Exception: An exception raised when response code is not 204
        """
        self.logger.info(f"Removing plugin '{plugin_key}' from instance.")
        res = self.request(
            method="DELETE",
            path=f"/rest/plugins/1.0/{plugin_key}-key",
            headers=AtlassianServerAPIHeaders.NO_CHECK,
        )
        self.logger.debug(f"Removing plugin response: {res.status_code} | {res.text}")
        res.raise_for_status()
        if res.status_code != 204:
            msg = f"Unable to remove plugin. Response: {res.status_code} | {res.text}"
            self.logger.error(msg)
            raise Exception(msg)

        return True
