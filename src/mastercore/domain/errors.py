"""Typed MASTERCORE errors.

Technical exceptions are normalized into stable application-facing error classes.
"""


class MastercoreError(Exception):
    """Base class for expected MASTERCORE failures."""


class ValidationError(MastercoreError):
    """Input, schema, or invariant validation failed."""


class ConfigurationError(MastercoreError):
    """Configuration is missing, invalid, or contradictory."""


class PermissionDeniedError(MastercoreError):
    """An operation is not authorized for the selected path or resource."""


class StorageError(MastercoreError):
    """A filesystem/storage operation failed safely."""


class DataIntegrityError(StorageError):
    """Written or loaded data failed integrity verification."""


class RecoveryError(StorageError):
    """Recovery or rollback could not complete safely."""


class StateConflictError(MastercoreError):
    """The observed state no longer matches the state expected by the operation."""
