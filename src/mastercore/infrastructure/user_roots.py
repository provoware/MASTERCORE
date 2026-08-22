"""Platform-aware user-data roots with deterministic test hooks."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Mapping

from mastercore.domain.data_classes import DataClass
from mastercore.domain.errors import ConfigurationError


@dataclass(frozen=True, slots=True)
class UserRoots:
    """Canonical roots for mutable MASTERCORE data classes."""

    config: Path
    content: Path
    cache: Path
    logs: Path
    backups: Path
    exports: Path

    def ensure(self) -> None:
        """Create all mutable roots with parent directories."""

        for path in self.all():
            path.mkdir(parents=True, exist_ok=True)

    def for_data_class(self, data_class: DataClass) -> Path:
        """Map a mutable data class to its canonical default root."""

        mapping = {
            DataClass.USER_CONFIG: self.config,
            DataClass.USER_CONTENT: self.content,
            DataClass.DERIVED_DATA: self.cache,
            DataClass.OPERATIONAL_DATA: self.logs,
            DataClass.RECOVERY_DATA: self.backups,
        }
        try:
            return mapping[data_class]
        except KeyError as exc:
            raise ConfigurationError(
                f"Data class {data_class.value} is not a mutable user-data root"
            ) from exc

    def all(self) -> tuple[Path, ...]:
        return (
            self.config,
            self.content,
            self.cache,
            self.logs,
            self.backups,
            self.exports,
        )


def resolve_user_roots(
    app_name: str = "MASTERCORE",
    *,
    home: Path | None = None,
    env: Mapping[str, str] | None = None,
    platform: str | None = None,
) -> UserRoots:
    """Resolve user-owned storage roots without writing to disk.

    ``home``, ``env`` and ``platform`` are injectable so tests do not depend on
    the machine that runs them.
    """

    _validate_app_name(app_name)
    environment = os.environ if env is None else env
    user_home = (Path.home() if home is None else Path(home)).expanduser().resolve(
        strict=False
    )
    current_platform = sys.platform if platform is None else platform

    if current_platform.startswith("win"):
        roaming = _env_path(environment, "APPDATA", user_home / "AppData" / "Roaming")
        local = _env_path(
            environment,
            "LOCALAPPDATA",
            user_home / "AppData" / "Local",
        )
        config = roaming / app_name
        data = local / app_name
        cache = data / "cache"
        logs = data / "logs"
    elif current_platform == "darwin":
        support = user_home / "Library" / "Application Support" / app_name
        config = support / "config"
        data = support / "data"
        cache = user_home / "Library" / "Caches" / app_name
        logs = user_home / "Library" / "Logs" / app_name
    else:
        config_home = _env_path(environment, "XDG_CONFIG_HOME", user_home / ".config")
        data_home = _env_path(
            environment,
            "XDG_DATA_HOME",
            user_home / ".local" / "share",
        )
        cache_home = _env_path(environment, "XDG_CACHE_HOME", user_home / ".cache")
        state_home = _env_path(
            environment,
            "XDG_STATE_HOME",
            user_home / ".local" / "state",
        )
        config = config_home / app_name
        data = data_home / app_name
        cache = cache_home / app_name
        logs = state_home / app_name / "logs"

    return UserRoots(
        config=config.resolve(strict=False),
        content=(data / "content").resolve(strict=False),
        cache=cache.resolve(strict=False),
        logs=logs.resolve(strict=False),
        backups=(data / "backups").resolve(strict=False),
        exports=(data / "exports").resolve(strict=False),
    )


def _env_path(environment: Mapping[str, str], key: str, fallback: Path) -> Path:
    raw = environment.get(key)
    return Path(raw).expanduser() if raw else fallback


def _validate_app_name(app_name: str) -> None:
    if not app_name or app_name in {".", ".."}:
        raise ConfigurationError("app_name must be a non-empty path component")
    if Path(app_name).name != app_name or "/" in app_name or "\\" in app_name:
        raise ConfigurationError("app_name must not contain path separators")
