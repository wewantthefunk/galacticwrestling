from __future__ import annotations

import pytest

from galactic_wrestling.ui.wrestler_list_ids import (
    wrestler_list_item_dom_id,
    wrestler_uuid_from_list_item_dom_id,
)

_SAMPLE = "38f0dc78-0af1-40c4-ac26-df58ad2d2099"
_EXPECTED_DOM = "w38f0dc780af140c4ac26df58ad2d2099"


def test_roundtrip_lowercase() -> None:
    dom = wrestler_list_item_dom_id(_SAMPLE)
    assert dom == _EXPECTED_DOM
    assert wrestler_uuid_from_list_item_dom_id(dom) == _SAMPLE


def test_roundtrip_uppercase_uuid_normalized() -> None:
    upper = _SAMPLE.upper()
    dom = wrestler_list_item_dom_id(upper)
    assert dom == _EXPECTED_DOM
    assert wrestler_uuid_from_list_item_dom_id(dom) == _SAMPLE


def test_invalid_uuid_for_dom_id() -> None:
    with pytest.raises(ValueError):
        wrestler_list_item_dom_id("not-a-uuid")


def test_invalid_dom_id_for_uuid() -> None:
    with pytest.raises(ValueError):
        wrestler_uuid_from_list_item_dom_id("38f0dc780af140c4ac26df58ad2d2099")
    with pytest.raises(ValueError):
        wrestler_uuid_from_list_item_dom_id("wshort")
    with pytest.raises(ValueError):
        wrestler_uuid_from_list_item_dom_id("x" + "0" * 32)
    with pytest.raises(ValueError):
        wrestler_uuid_from_list_item_dom_id("w" + "g" * 32)
