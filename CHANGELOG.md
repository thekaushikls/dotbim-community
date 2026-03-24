# Changelog

## [Unreleased]

### Changed

- **`__eq__` methods now return `False` instead of `NotImplemented`** when comparing with incompatible types.
  The original classes returned `NotImplemented` to allow Python's reflected equality mechanism.
  The new Pydantic models return `False` directly, which is semantically clearer for value objects
  that have no reason to support cross-type equality. Tests that previously asserted
  `obj.__eq__(5) == NotImplemented` need to be updated to `obj.__eq__(5) == False`.

- Migrated `Color`, `Vector`, and `Rotation` from plain classes to Pydantic `BaseModel` subclasses.

- Replaced `setup.py` / `setup.cfg` with `pyproject.toml` using `hatchling` build backend.

- Package management moved from pip to uv.
