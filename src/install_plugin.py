import logging
import os
import time
from pathlib import Path

import click

from atlassian.jira import JiraServer

logger = logging.getLogger(__name__)


@click.command(help="Install plugin on Atlassian server instance")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--url", "-url", default="", type=str, help="Atlassian instance base URL")
@click.option("--username", "-u", default="", type=str, help="Username to login")
@click.option("--password", "-p", default="", type=str, help="Password to login")
@click.option("--timeout", default=90, help="Install timeout in second")
def install_plugin_server(
    filepath: str,
    url: str,
    username: str,
    password: str,
    timeout: float,
):
    """Install plugin on Atlassian server instance

    Args:
        filepath (str): path to plugin file
        url (str): instance base url
        username (str): admin username
        password (str): admin password
        timeout (float): timeout threshold before giving up installing

    Raises:
        TimeoutError: when timeout threshold is reached
    """
    # Setting up vars
    vars = {
        "url": url if url else os.getenv("ATLAS_URL", ""),
        "username": username if username else os.getenv("ATLAS_USERNAME", ""),
        "password": password if password else os.getenv("ATLAS_PASSWORD", ""),
    }
    for key, val in vars.items():
        if val == "":
            raise ValueError(f"'{key}' is not set")

    filepath = click.format_filename(filepath)
    logger.info(f"Installing plugin to {url} using '{filepath}'. Timeout: {timeout}")
    jira = JiraServer(
        url=url,
        username=username,
        password=password,
    )

    upload_res = jira.upload_plugin(Path(filepath))
    task_id = upload_res["id"]
    timeout_at = time.time() + timeout

    plugin_data = {
        "key": "",
        "enabled": None,
        "version": "",
    }
    while True:
        if time.time() >= timeout_at:
            raise TimeoutError(f"Timeout after {timeout} seconds")

        task_info_res = jira.get_plugin_pending_task_info(task_id=task_id)

        # still pending or failed
        if "status" in task_info_res:
            status = task_info_res["status"]
            done = status["done"]
            err = status["errorMessage"] if "errorMessage" in status else None

            # failed task
            if err:
                msg = f"Error installing plugin {status['name']}: {err}"
                logger.error(msg)
                raise Exception(msg)

            # done but no error?
            if done:
                msg = f"Task {task_id} status is {done} but error is {err}"
                logger.error(msg)
                raise Exception(msg)

            # not done, still pending, retry!
            ping_after = float(task_info_res["pingAfter"]) / 1000

            logger.info(
                f"Task {task_id} status is {done},"
                f" amount downloaded: {status['amountDownloaded']}."
                f" Pinging after: {ping_after} sec"
            )
            time.sleep(ping_after)
            continue

        # redirected to plugin info
        plugin_data = {
            "key": task_info_res["key"],
            "enabled": task_info_res["enabled"],
            "version": task_info_res["version"],
        }
        break
    logger.info(
        f"Plugin '{plugin_data['key']}' is installed."
        f" Enabled: {plugin_data['enabled']}."
        f" Version: {plugin_data['version']}."
    )
