from __future__ import annotations

from pathlib import Path

import pytest

from galactic_wrestling.app import GalacticApp, main
from galactic_wrestling.ui.screens import LoginScreen


def test_main_runs_app(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[bool] = []

    class FakeApp:
        def run(self) -> None:
            calls.append(True)

    monkeypatch.setattr("galactic_wrestling.app.GalacticApp", lambda: FakeApp())
    main()
    assert calls == [True]


@pytest.mark.asyncio
async def test_app_mounts_login_screen(isolated_data_dir: Path) -> None:
    app = GalacticApp()
    async with app.run_test(size=(80, 24)) as pilot:
        assert isinstance(app.screen, LoginScreen)
        assert pilot.app is app


@pytest.mark.asyncio
async def test_app_on_mount_calls_ensure_ai_opponents(
    isolated_data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[bool] = []

    def stub() -> None:
        calls.append(True)

    monkeypatch.setattr("galactic_wrestling.app.ensure_ai_opponents", stub)
    app = GalacticApp()
    async with app.run_test(size=(80, 24)):
        assert calls == [True]
