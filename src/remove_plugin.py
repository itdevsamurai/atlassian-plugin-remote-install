import logging
import time

import click

from atlassian.jira import JiraServer
from config import Config
from utils.apprise_notify import NotifyType, apprise_notify
from utils.helper import check_required_params

logger = logging.getLogger(__name__)


@click.command(help="Remove plugin on Atlassian server instance")
@click.argument("plugin_key", type=str)
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
@click.option("--timeout", default=120, help="Remove timeout in second")
def remove_plugin_server(
    plugin_key: str,
    url: str,
    username: str,
    password: str,
    notify: list[str],
    timeout: float,
):
    # Setting up vars
    url = url if url else Config.ATLAS_URL
    username = username if username else Config.ATLAS_USERNAME
    password = password if password else Config.ATLAS_PASSWORD
    check_required_params(
        {
            "url": url,
            "username": username,
            "password": password,
        }
    )

    if len(notify) == 0 and Config.NOTIFY_TITLE != "":
        notify = [Config.NOTIFY_URL]

    logger.info(f"Removing plugin from {url}. Timeout: {timeout}")
    jira = JiraServer(
        url=url,
        username=username,
        password=password,
    )

    if jira.version is None:
        msg = f"Instance '{url}' is not reachable."
        logger.error(msg)
        if notify:
            apprise_notify(
                notify_url_list=notify,
                body=msg,
                notify_type=NotifyType.WARNING,
            )
        raise Exception(msg)

    # Remove the plugin from instance
    timeout_at = time.time() + timeout

    # Conduct removing, retry if not succeed
    final_msg: str = ""
    retryTime: int = 1
    err_flag: bool = False
    while time.time() < timeout_at:
        remove_res = jira.remove_plugin(plugin_key)
        if remove_res != True:
            final_msg = f"Removing plugin failed. Retry {retryTime}. Timeouted after {timeout} seconds"
        else:
            err_flag = False
            final_msg = "Removing plugin is successful"
            break

    # append jira info to the top of the final msg
    final_msg = f"{url} - Jira *v{jira.version}*\n" + final_msg

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
            logger.error("Unable to send some notifications.")

    if err_flag:
        logger.error(final_msg)
        raise Exception(final_msg)

    logger.info(final_msg)
