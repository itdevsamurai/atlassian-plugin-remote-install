import logging

from apprise import Apprise, NotifyType

logger = logging.getLogger(__name__)


def apprise_notify(
    notify_url_list: list[str],
    body: str,
    title: str = "",
    notify_type: NotifyType = NotifyType.INFO,
) -> bool | None:
    ar = Apprise()
    for url in notify_url_list:
        ar.add(url)
        logger.debug(f"Added apprise url: {url}")
    status = ar.notify(
        body=body,
        title=title,
        notify_type=notify_type,
    )
    logger.debug(f"Apprise notify status: {status}")
    return status
