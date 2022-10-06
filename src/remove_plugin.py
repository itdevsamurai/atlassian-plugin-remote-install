import logging
import time
import click
from atlassian.jira import JiraServer
from config import Config
from utils.apprise_notify import NotifyType, apprise_notify

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

    logger.info(f"Removing plugin from {url}. Timeout: {timeout}")
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

    # Remove the plugin from instance
    timeout_at = time.time() + timeout

    # Checking if task is finished successfully
    final_msg: str = ""
    retryTime: int = 1
    err_flag: bool = False
    while time.time() < timeout_at:
        remove_res = jira.remove_plugin(plugin_key)
        if remove_res != True:
            final_msg = f"Removing plugin failed. Retry {retryTime}. Timeouted after {timeout} seconds"
        else:
            err_flag = False
            final_msg = f"Removing plugin is successful"
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
