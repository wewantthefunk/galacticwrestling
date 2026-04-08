from __future__ import annotations

import warnings

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Quiet pytest-cov noise when the package is imported before coverage starts."""
    del config  # required hook signature
    try:
        from coverage.exceptions import CoverageWarning
    except ImportError:
        return
    warnings.filterwarnings(
        "ignore",
        message="Module galactic_wrestling was previously imported*",
        category=CoverageWarning,
    )


@pytest.fixture
def isolated_data_dir(monkeypatch: pytest.MonkeyPatch, tmp_path) -> object:
    """Point app data at an empty temp directory (each test gets a fresh path)."""
    monkeypatch.setenv("GALACTIC_WRESTLING_DATA_DIR", str(tmp_path))
    return tmp_path
