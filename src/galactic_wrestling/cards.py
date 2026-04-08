from __future__ import annotations

from dataclasses import dataclass

from galactic_wrestling.models import Archetype


@dataclass(frozen=True)
class CardDef:
    id: str
    name: str


# Shared starter package for every new wrestler (same for all archetypes).
BASIC_CARDS: tuple[CardDef, ...] = (
    CardDef("basic_punch", "Punch"),
    CardDef("basic_kick", "Kick"),
    CardDef("basic_body_slam", "Body Slam"),
    CardDef("basic_clothesline", "Clothesline"),
    CardDef("basic_suplex", "Suplex"),
    CardDef("basic_elbow_drop", "Elbow Drop"),
    CardDef("basic_headlock", "Headlock"),
    CardDef("basic_irish_whip", "Irish Whip"),
)

# Archetype-specific cards (5–7 each).
ARCHETYPE_CARDS: dict[Archetype, tuple[CardDef, ...]] = {
    Archetype.GIANT: (
        CardDef("giant_chokeslam", "Chokeslam"),
        CardDef("giant_splash", "Splash"),
        CardDef("giant_bear_hug", "Bear Hug"),
        CardDef("giant_stomp", "Stomp"),
        CardDef("giant_press_slam", "Press Slam"),
        CardDef("giant_corner_splash", "Corner Splash"),
    ),
    Archetype.FLYER: (
        CardDef("flyer_diving_crossbody", "Diving Crossbody"),
        CardDef("flyer_springboard", "Springboard Attack"),
        CardDef("flyer_dropkick", "Dropkick"),
        CardDef("flyer_hurricanrana", "Hurricanrana"),
        CardDef("flyer_tope", "Tope Suicida"),
        CardDef("flyer_moonsault", "Moonsault"),
        CardDef("flyer_enzuigiri", "Enzuigiri"),
    ),
    Archetype.JOBBER: (
        CardDef("jobber_quick_pin", "Quick Pin Attempt"),
        CardDef("jobber_roll_up", "Roll-Up"),
        CardDef("jobber_steam", "Hope Spot"),
        CardDef("jobber_nearfall", "Near Fall"),
        CardDef("jobber_underdog", "Underdog Strike"),
    ),
    Archetype.FLASHY: (
        CardDef("flashy_superkick", "Superkick"),
        CardDef("flashy_spinarooni", "Showboat"),
        CardDef("flashy_strut", "Strut"),
        CardDef("flashy_chain", "Chain Wrestling"),
        CardDef("flashy_ddt", "DDT"),
        CardDef("flashy_frog_splash", "Frog Splash"),
    ),
    Archetype.COMEDY: (
        CardDef("comedy_bananapeel", "Pratfall"),
        CardDef("comedy_distraction", "Distraction"),
        CardDef("comedy_cartwheel", "Cartwheel Escape"),
        CardDef("comedy_tickle", "Comedy Spot"),
        CardDef("comedy_prop", "Prop Strike"),
        CardDef("comedy_dance", "Taunt Dance"),
    ),
    Archetype.REGULAR: (
        CardDef("regular_slam", "Slam"),
        CardDef("regular_backbreaker", "Backbreaker"),
        CardDef("regular_hip_toss", "Hip Toss"),
        CardDef("regular_arm_drag", "Arm Drag"),
        CardDef("regular_sleeper", "Sleeper"),
        CardDef("regular_spinebuster", "Spinebuster"),
    ),
}


def starter_deck(archetype: Archetype) -> tuple[CardDef, ...]:
    extra = ARCHETYPE_CARDS.get(archetype)
    if extra is None:
        raise ValueError(f"Unknown archetype: {archetype!r}")
    return BASIC_CARDS + extra


def format_starter_deck_preview(archetype: Archetype) -> str:
    deck = starter_deck(archetype)
    lines = [f"{i + 1:>2}. {c.name}  ({c.id})" for i, c in enumerate(deck)]
    return "\n".join(lines)
