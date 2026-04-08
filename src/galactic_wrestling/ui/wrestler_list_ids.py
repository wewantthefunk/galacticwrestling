"""Encode wrestler UUIDs as valid Textual DOM ids.

Textual requires ids to match ``[A-Za-z_][A-Za-z0-9_-]*`` (no leading digit). Raw UUID
strings can start with a hex digit, so they cannot be used as-is on ``ListItem``.
"""

from __future__ import annotations


def wrestler_list_item_dom_id(wrestler_uuid: str) -> str:
    """Return a DOM id that is unique per wrestler and Textual-valid."""
    compact = wrestler_uuid.replace("-", "")
    if len(compact) != 32 or any(c not in "0123456789abcdefABCDEF" for c in compact):
        raise ValueError("Expected a canonical UUID string")
    return "w" + compact.lower()


def wrestler_uuid_from_list_item_dom_id(dom_id: str) -> str:
    """Inverse of :func:`wrestler_list_item_dom_id`."""
    if not dom_id.startswith("w") or len(dom_id) != 33:
        raise ValueError(f"Not a wrestler list item id: {dom_id!r}")
    h = dom_id[1:]
    if len(h) != 32 or any(c not in "0123456789abcdef" for c in h):
        raise ValueError(f"Not a wrestler list item id: {dom_id!r}")
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
