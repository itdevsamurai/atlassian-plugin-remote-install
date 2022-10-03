import logging
import time
from pathlib import Path

import click

from atlassian.jira import JiraServer
from config import Config
from utils.apprise_notify import NotifyType, apprise_notify

logger = logging.getLogger(__name__)


@click.command(help="Install plugin on Atlassian server instance")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--url", "-url", default="", type=str, help="Atlassian instance base URL")
@click.option("--username", "-u", default="", type=str, help="Username to login")
@click.option("--password", "-p", default="", type=str, help="Password to login")
@click.option(
    "--notify",
    "-n",
    default=[],
    type=str,
    multiple=True,
    help="Apprise notification URL",
)
@click.option("--timeout", default=120, help="Install timeout in second")
def install_plugin_server(
    filepath: str,
    url: str,
    username: str,
    password: str,
    notify: list[str],
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
        "url": url if url else Config.ATLAS_URL,
        "username": username if username else Config.ATLAS_USERNAME,
        "password": password if password else Config.ATLAS_PASSWORD,
    }
    for key, val in vars.items():
        if val == "":
            raise ValueError(f"'{key}' is not set")
    if len(notify) == 0 and Config.NOTIFY_TITLE != "":
        notify = [Config.NOTIFY_URL]

    filepath = click.format_filename(filepath)
    logger.info(f"Installing plugin to {url} using '{filepath}'. Timeout: {timeout}")
    jira = JiraServer(
        url=url,
        username=username,
        password=password,
    )
    if jira.status is False:
        msg = f"Instance '{url}' is not reachable."
        logger.error(msg)
        if notify:
            apprise_notify(
                notify_url_list=notify,
                body=msg,
                notify_type=NotifyType.WARNING,
            )
        raise Exception(msg)

    # Upload the plugin to instance
    upload_res = jira.upload_plugin(Path(filepath))
    task_id = upload_res["id"]
    timeout_at = time.time() + timeout

    # Checking if task is finished successfully
    err_flag: bool = False
    final_msg: str = ""
    while True:
        if time.time() >= timeout_at:
            err_flag = True
            final_msg = f"Installing plugin is taking too long. Timeouted after {timeout} seconds"
            break

        task_info_res = jira.get_plugin_pending_task_info(task_id=task_id)

        # still pending or failed
        if "status" in task_info_res:
            status = task_info_res["status"]
            done = status["done"]
            err = status["errorMessage"] if "errorMessage" in status else None

            # failed task
            if err:
                final_msg = f"Error installing plugin {status['name']}: {err}"
                err_flag = True
                break

            # done but no error? this path should not happen
            if done:
                final_msg = f"Task {task_id} status is {done} but error is {err}"
                err_flag = True
                break

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
        final_msg = (
            f"Plugin '{task_info_res['key']}' is installed."
            f" Enabled: {task_info_res['enabled']}."
            f" Version: {task_info_res['version']}."
        )
        break

    if notify:
        status = apprise_notify(
            notify_url_list=notify,
            body=final_msg,
            title=Config.NOTIFY_TITLE,
            notify_type=NotifyType.FAILURE if err_flag else NotifyType.SUCCESS,
        )

        if status is None:
            logger.info("No notification was sent.")
        elif status:
            logger.info(f"Notification sent to {len(notify)} urls.")
        else:
            logger.error(f"Unable to send some notifications.")

    if err_flag:
        logger.error(final_msg)
        raise Exception(final_msg)

    logger.info(final_msg)
