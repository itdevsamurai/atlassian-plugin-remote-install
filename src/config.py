import logging
import os


class Config:
    LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)
    ATLAS_URL = os.getenv("ATLAS_URL", "")
    ATLAS_USERNAME = os.getenv("ATLAS_USERNAME", "")
    ATLAS_PASSWORD = os.getenv("ATLAS_PASSWORD", "")

    # Notify
    NOTIFY_TITLE = os.getenv("NOTIFY_TITLE", "Plugin Remote Install")
    NOTIFY_URL = os.getenv("NOTIFY_URL", "")
