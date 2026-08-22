"""Canonical persistent-data classifications."""

from enum import StrEnum


class DataClass(StrEnum):
    """Storage class used to prevent app/user data mixing."""

    IMMUTABLE_APP_DATA = "immutable_app_data"
    USER_CONFIG = "user_config"
    USER_CONTENT = "user_content"
    DERIVED_DATA = "derived_data"
    OPERATIONAL_DATA = "operational_data"
    RECOVERY_DATA = "recovery_data"
