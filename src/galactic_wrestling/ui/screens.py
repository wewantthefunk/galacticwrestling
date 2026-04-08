from __future__ import annotations

import random

from textual import events, on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Log, Select, Static

from galactic_wrestling import auth, storage
from galactic_wrestling.ai_opponents import list_ai_wrestlers
from galactic_wrestling.auth import Account
from galactic_wrestling.cards import format_starter_deck_preview
from galactic_wrestling.gimmicks import GIMMICKS, gimmick_by_id
from galactic_wrestling.match.ai_policy import choose_ai_hand_index
from galactic_wrestling.match.deck_builder import build_match_decks
from galactic_wrestling.match.engine import MatchState
from galactic_wrestling.match.model import MatchOutcome
from galactic_wrestling.models import Alignment, Archetype, MatchLocation, MatchStipulation, Wrestler
from galactic_wrestling.ui.wrestler_list_ids import (
    wrestler_list_item_dom_id,
    wrestler_uuid_from_list_item_dom_id,
)


class LoginScreen(Screen):
    """Strict password login."""

    BINDINGS = [("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="login_box"):
            yield Label("Galactic Wrestling — Login", id="login_title")
            yield Label("Login name")
            yield Input(placeholder="Your name", id="login_name")
            yield Label("Password")
            yield Input(placeholder="Password", password=True, id="login_password")
            with Horizontal(id="login_buttons"):
                yield Button("Log in", variant="primary", id="btn_login")
                yield Button("Sign up", id="btn_signup")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#login_name", Input).focus()

    def action_back(self) -> None:
        self.app.exit()

    @on(Button.Pressed, "#btn_login")
    def login_pressed(self) -> None:
        name = self.query_one("#login_name", Input).value
        pw = self.query_one("#login_password", Input).value
        try:
            account = auth.login(name, pw)
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return
        self.app.player_id = account.player_id
        self.app.login_name = account.login_name
        self.app.pop_screen()
        self.app.push_screen(MainMenuScreen())

    @on(Button.Pressed, "#btn_signup")
    def signup_pressed(self) -> None:
        self.app.push_screen(SignupScreen())


class SignupScreen(Screen[None]):
    BINDINGS = [("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="signup_box"):
            yield Label("Create account", id="signup_title")
            yield Label("Login name (also your display name)")
            yield Input(placeholder="Choose a name", id="su_name")
            yield Label("Password")
            yield Input(placeholder="Password", password=True, id="su_pw")
            yield Label("Confirm password")
            yield Input(placeholder="Again", password=True, id="su_pw2")
            with Horizontal():
                yield Button("Create account", variant="primary", id="su_create")
                yield Button("Back", id="su_back")
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#su_back")
    def back_btn(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#su_create")
    def create(self) -> None:
        name = self.query_one("#su_name", Input).value
        pw = self.query_one("#su_pw", Input).value
        pw2 = self.query_one("#su_pw2", Input).value
        if pw != pw2:
            self.app.notify("Passwords do not match.", severity="error")
            return
        try:
            auth.signup(name, pw)
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return
        self.app.notify("Account created. You can log in now.", severity="information")
        self.app.pop_screen()


class MainMenuScreen(Screen[None]):
    BINDINGS = [("escape", "logout", "Log out")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        ln = getattr(self.app, "login_name", "?")
        with Container(id="main_menu_box"):
            yield Label(f"Welcome, {ln}", id="welcome")
            yield Button("Manage wrestlers", variant="primary", id="mm_roster")
            yield Button("Head-to-head (local PVP)", id="mm_pvp")
            yield Button("Single player", id="mm_sp")
            yield Button("Log out", id="mm_logout")
        yield Footer()

    def action_logout(self) -> None:
        self._logout()

    def _logout(self) -> None:
        self.app.player_id = None
        self.app.login_name = None
        self.app.pop_screen()
        self.app.push_screen(LoginScreen())

    @on(Button.Pressed, "#mm_roster")
    def open_roster(self) -> None:
        self.app.push_screen(RosterScreen())

    @on(Button.Pressed, "#mm_pvp")
    def open_pvp(self) -> None:
        self.app.push_screen(PvpScreen())

    @on(Button.Pressed, "#mm_sp")
    def open_single_player(self) -> None:
        pid = self.app.player_id
        assert pid is not None
        if storage.count_wrestlers(pid) < 1:
            self.app.notify(
                "Create at least one wrestler first (Manage wrestlers).",
                severity="warning",
            )
            return
        self.app.push_screen(SinglePlayerPickWrestlerScreen())

    @on(Button.Pressed, "#mm_logout")
    def logout_btn(self) -> None:
        self._logout()


class SinglePlayerPickWrestlerScreen(Screen[None]):
    """Choose your wrestler for single-player."""

    BINDINGS = [("escape", "back", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self._selected_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sp_pw_root"):
            yield Label("Single player — pick your wrestler", id="sp_pw_title")
            yield ListView(id="sp_pw_list")
            with Horizontal():
                yield Button("Next", variant="primary", id="sp_pw_next")
                yield Button("Back", id="sp_pw_back")
        yield Footer()

    async def on_mount(self) -> None:
        await self._reload()

    async def _reload(self) -> None:
        lv = self.query_one("#sp_pw_list", ListView)
        await lv.clear()
        pid = self.app.player_id
        assert pid is not None
        items = [
            ListItem(Label(w.name), id=wrestler_list_item_dom_id(w.id))
            for w in storage.list_wrestlers(pid)
        ]
        if items:
            await lv.extend(items)
        self._selected_id = None

    def action_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#sp_pw_back")
    def back_btn(self) -> None:
        self.app.pop_screen()

    @on(ListView.Selected, "#sp_pw_list")
    def on_pick(self, event: ListView.Selected) -> None:
        item = event.item
        dom_id = item.id or ""
        try:
            self._selected_id = wrestler_uuid_from_list_item_dom_id(dom_id)
        except ValueError:
            self._selected_id = None

    @on(Button.Pressed, "#sp_pw_next")
    def next_step(self) -> None:
        if not self._selected_id:
            self.app.notify("Select a wrestler first.", severity="error")
            return
        pid = self.app.player_id
        assert pid is not None
        wrestler = next(
            (w for w in storage.list_wrestlers(pid) if w.id == self._selected_id),
            None,
        )
        if wrestler is None:
            self.app.notify("Wrestler not found.", severity="error")
            return
        self.app.push_screen(SinglePlayerPickAiScreen(wrestler))


class SinglePlayerPickAiScreen(Screen[None]):
    """Random or specific AI opponent."""

    BINDINGS = [("escape", "back", "Back")]

    def __init__(self, player_wrestler: Wrestler) -> None:
        super().__init__()
        self._player_wrestler = player_wrestler

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sp_ai_root"):
            yield Label(
                f"Opponent for {self._player_wrestler.name}",
                id="sp_ai_title",
            )
            yield Label("AI opponent")
            opts: list[tuple[str, str]] = [("Random AI opponent", "__random__")]
            for w in list_ai_wrestlers():
                opts.append((f"{w.name} ({w.archetype.value})", w.id))
            yield Select(opts, id="sp_ai_select", allow_blank=False)
            with Horizontal():
                yield Button("Next", variant="primary", id="sp_ai_next")
                yield Button("Back", id="sp_ai_back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#sp_ai_select", Select).focus()

    def action_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#sp_ai_back")
    def back_btn(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#sp_ai_next")
    def next_step(self) -> None:
        sel = self.query_one("#sp_ai_select", Select)
        v = sel.value
        if v is None:
            self.app.notify("Pick an AI opponent.", severity="error")
            return
        rng = random.Random()
        opponents = list_ai_wrestlers()
        if not opponents:
            self.app.notify(
                "No AI opponents on disk. Run: python -m galactic_wrestling.ai_opponents",
                severity="error",
            )
            return
        if v == "__random__":
            ai = rng.choice(opponents)
        else:
            ai = next((w for w in opponents if w.id == str(v)), None)
            if ai is None:
                self.app.notify("AI opponent not found.", severity="error")
                return
        self.app.push_screen(SinglePlayerLocationScreen(self._player_wrestler, ai))


class SinglePlayerLocationScreen(Screen[None]):
    """Match location (modifiers cosmetic until rules expand)."""

    BINDINGS = [("escape", "back", "Back")]

    def __init__(self, player_wrestler: Wrestler, ai_wrestler: Wrestler) -> None:
        super().__init__()
        self._player_wrestler = player_wrestler
        self._ai_wrestler = ai_wrestler

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sp_loc_root"):
            yield Label("Match location", id="sp_loc_title")
            yield Select(
                [(loc.value, loc.value) for loc in MatchLocation],
                id="sp_loc_select",
                allow_blank=False,
            )
            with Horizontal():
                yield Button("Next", variant="primary", id="sp_loc_next")
                yield Button("Back", id="sp_loc_back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#sp_loc_select", Select).focus()

    def action_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#sp_loc_back")
    def back_btn(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#sp_loc_next")
    def next_step(self) -> None:
        sel = self.query_one("#sp_loc_select", Select)
        v = sel.value
        if v is None:
            self.app.notify("Pick a location.", severity="error")
            return
        loc = MatchLocation(str(v))
        self.app.push_screen(
            SinglePlayerStipulationScreen(self._player_wrestler, self._ai_wrestler, loc)
        )


class SinglePlayerStipulationScreen(Screen[None]):
    """Match stipulation then start."""

    BINDINGS = [("escape", "back", "Back")]

    def __init__(
        self, player_wrestler: Wrestler, ai_wrestler: Wrestler, location: MatchLocation
    ) -> None:
        super().__init__()
        self._player_wrestler = player_wrestler
        self._ai_wrestler = ai_wrestler
        self._location = location

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sp_stip_root"):
            yield Label("Match stipulation", id="sp_stip_title")
            yield Select(
                [(st.value, st.value) for st in MatchStipulation],
                id="sp_stip_select",
                allow_blank=False,
            )
            with Horizontal():
                yield Button("Start match", variant="primary", id="sp_stip_start")
                yield Button("Back", id="sp_stip_back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#sp_stip_select", Select).focus()

    def action_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#sp_stip_back")
    def back_btn(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#sp_stip_start")
    def start(self) -> None:
        sel = self.query_one("#sp_stip_select", Select)
        v = sel.value
        if v is None:
            self.app.notify("Pick a stipulation.", severity="error")
            return
        stip = MatchStipulation(str(v))
        self.app.push_screen(
            MatchScreen(
                self._player_wrestler,
                self._ai_wrestler,
                self._location,
                stip,
            )
        )


class MatchScreen(Screen[None]):
    """Play a single-player match vs AI (two-lane clash, deck combat)."""

    def __init__(
        self,
        player_wrestler: Wrestler,
        ai_wrestler: Wrestler,
        location: MatchLocation,
        stipulation: MatchStipulation,
    ) -> None:
        super().__init__()
        self._player_wrestler = player_wrestler
        self._ai_wrestler = ai_wrestler
        self._location = location
        self._stipulation = stipulation
        self._rng = random.Random(random.randrange(2**63))
        deck_rng = random.Random(self._rng.random())
        pd, ad = build_match_decks(player_wrestler, ai_wrestler, deck_rng)
        self._state = MatchState.from_decks(pd, ad, rng=self._rng)
        self._ai_rng = random.Random(self._rng.random())
        self._hand_index = 0
        self._over = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="match_root"):
            pid = self.app.player_id
            wins, losses = (0, 0)
            if pid is not None:
                wins, losses = storage.load_match_stats(pid)
            yield Label(
                f"{self._location.value} · {self._stipulation.value} · Record W{wins}-L{losses}",
                id="match_meta",
            )
            with Horizontal(id="match_columns"):
                with Vertical(id="match_p_col"):
                    yield Label(
                        f"You: {self._player_wrestler.name} ({self._player_wrestler.archetype.value})",
                        id="match_p_title",
                    )
                    yield Label("", id="match_p_hp")
                with Vertical(id="match_ai_col"):
                    yield Label(
                        f"AI: {self._ai_wrestler.name} ({self._ai_wrestler.archetype.value})",
                        id="match_ai_title",
                    )
                    yield Label("", id="match_ai_hp")
            yield Log(id="match_log", max_lines=200, highlight=True)
            yield Label("Your hand (select a card, then Play)", id="match_hand_hint")
            yield ListView(id="match_hand")
            with Horizontal(id="match_actions"):
                yield Button("Play selected card", variant="primary", id="match_play")
                yield Button("Forfeit", variant="error", id="match_forfeit")
                yield Button("Back to menu", id="match_done", disabled=True)
        yield Footer()

    def on_mount(self) -> None:
        self._sync_hp()
        log = self.query_one("#match_log", Log)
        log.write_line(
            f"Fight! {self._player_wrestler.name} vs {self._ai_wrestler.name}."
        )
        self.call_later(self._reload_hand)

    def _sync_hp(self) -> None:
        self.query_one("#match_p_hp", Label).update(
            f"Health: {self._state.player_health}  ·  Hand: {len(self._state.player_hand)}"
        )
        self.query_one("#match_ai_hp", Label).update(
            f"Health: {self._state.ai_health}  ·  Hand: {len(self._state.ai_hand)}"
        )

    async def _reload_hand(self) -> None:
        lv = self.query_one("#match_hand", ListView)
        await lv.clear()
        for i, c in enumerate(self._state.player_hand):
            await lv.extend(
                [
                    ListItem(
                        Label(f"{c.name}  O{c.offense} D{c.defense}  ${c.cost}"),
                        id=f"mh{i}",
                    )
                ]
            )
        if self._state.player_hand:
            lv.index = 0
            self._hand_index = 0

    @on(ListView.Selected, "#match_hand")
    def hand_selected(self, event: ListView.Selected) -> None:
        self._hand_index = int(event.index)

    @on(Button.Pressed, "#match_play")
    async def play_round_btn(self) -> None:
        if self._over:
            return
        if not self._state.player_hand or not self._state.ai_hand:
            await self._stalemate()
            return
        if self._hand_index < 0 or self._hand_index >= len(self._state.player_hand):
            self.app.notify("Select a card in your hand.", severity="error")
            return
        ai_i = choose_ai_hand_index(self._state, self._ai_rng)
        r = self._state.play_round(self._hand_index, ai_i)
        log = self.query_one("#match_log", Log)
        log.write_line(
            f"You: {r.player_card.name}  |  AI: {r.ai_card.name}  |  "
            f"dmg to you {r.damage_to_player}, dmg to AI {r.damage_to_ai}"
        )
        self._sync_hp()
        await self._reload_hand()
        outcome = self._state.outcome()
        if outcome != MatchOutcome.ONGOING:
            await self._finish(outcome)

    async def _stalemate(self) -> None:
        self._over = True
        log = self.query_one("#match_log", Log)
        log.write_line("Neither side can play — match ends in a draw.")
        self.query_one("#match_play", Button).disabled = True
        self.query_one("#match_forfeit", Button).disabled = True
        self.query_one("#match_done", Button).disabled = False

    async def _finish(self, outcome: MatchOutcome) -> None:
        self._over = True
        pid = self.app.player_id
        if pid is not None:
            storage.record_match_outcome(pid, outcome)
        log = self.query_one("#match_log", Log)
        if outcome == MatchOutcome.PLAYER_WINS:
            log.write_line("You win!")
        elif outcome == MatchOutcome.AI_WINS:
            log.write_line("You lose.")
        else:
            log.write_line("Draw.")
        meta = self.query_one("#match_meta", Label)
        if pid is not None:
            w, l = storage.load_match_stats(pid)
            meta.update(
                f"{self._location.value} · {self._stipulation.value} · Record W{w}-L{l}"
            )
        self.query_one("#match_play", Button).disabled = True
        self.query_one("#match_forfeit", Button).disabled = True
        self.query_one("#match_done", Button).disabled = False

    @on(Button.Pressed, "#match_forfeit")
    async def forfeit(self) -> None:
        if self._over:
            return
        self._state.player_health = 0
        self._sync_hp()
        await self._finish(MatchOutcome.AI_WINS)

    @on(Button.Pressed, "#match_done")
    def done(self) -> None:
        self.app.pop_screen()

class RosterScreen(Screen[None]):
    BINDINGS = [("escape", "back", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self._selected_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="roster_root"):
            yield Label("Your wrestlers (max 5)", id="roster_heading")
            yield ListView(id="roster_list")
            with Horizontal(id="roster_actions"):
                yield Button("New wrestler", variant="primary", id="rw_new")
                yield Button("Rename", id="rw_rename")
                yield Button("Delete", variant="error", id="rw_delete")
                yield Button("Back", id="rw_back")
            yield Label("", id="rename_hint")
            yield Input(placeholder="New name", id="rename_input")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#rename_input", Input).display = False
        self.query_one("#rename_hint", Label).display = False
        await self._reload_list()

    async def _reload_list(self) -> None:
        """ListView.clear/extend return awaitables; must await or removals race appends."""
        lv = self.query_one("#roster_list", ListView)
        await lv.clear()
        pid = self.app.player_id
        assert pid is not None
        wrestlers = storage.list_wrestlers(pid)
        items = [
            ListItem(Label(w.name), id=wrestler_list_item_dom_id(w.id)) for w in wrestlers
        ]
        if items:
            await lv.extend(items)
        self._selected_id = None

    def action_back(self) -> None:
        if self.query_one("#rename_input", Input).display:
            self._cancel_rename_ui()
            return
        self.app.pop_screen()

    @on(Button.Pressed, "#rw_back")
    def back_btn(self) -> None:
        if self.query_one("#rename_input", Input).display:
            self._cancel_rename_ui()
            return
        self.app.pop_screen()

    @on(ListView.Selected, "#roster_list")
    def on_pick(self, event: ListView.Selected) -> None:
        item = event.item
        dom_id = item.id or ""
        try:
            self._selected_id = wrestler_uuid_from_list_item_dom_id(dom_id)
        except ValueError:
            self._selected_id = None

    @on(Button.Pressed, "#rw_new")
    def new_wrestler(self) -> None:
        pid = self.app.player_id
        assert pid is not None
        if storage.count_wrestlers(pid) >= storage.MAX_WRESTLERS:
            self.app.notify(f"You already have {storage.MAX_WRESTLERS} wrestlers.", severity="error")
            return
        self.app.push_screen(WrestlerCreateScreen())

    @on(Button.Pressed, "#rw_rename")
    def rename_wrestler(self) -> None:
        if not self._selected_id:
            self.app.notify("Select a wrestler first.", severity="error")
            return
        self.query_one("#rename_hint", Label).update("New name (Enter to save, Esc to cancel):")
        self.query_one("#rename_hint", Label).display = True
        inp = self.query_one("#rename_input", Input)
        inp.display = True
        pid = self.app.player_id
        assert pid is not None
        for w in storage.list_wrestlers(pid):
            if w.id == self._selected_id:
                inp.value = w.name
                break
        inp.focus()

    @on(Button.Pressed, "#rw_delete")
    async def delete_wrestler(self) -> None:
        if not self._selected_id:
            self.app.notify("Select a wrestler first.", severity="error")
            return
        pid = self.app.player_id
        assert pid is not None
        storage.delete_wrestler(pid, self._selected_id)
        self.app.notify("Wrestler deleted.", severity="information")
        self._cancel_rename_ui()
        await self._reload_list()

    def _cancel_rename_ui(self) -> None:
        self.query_one("#rename_input", Input).display = False
        self.query_one("#rename_hint", Label).display = False

    @on(Input.Submitted, "#rename_input")
    async def rename_submit(self, event: Input.Submitted) -> None:
        if not self._selected_id:
            return
        pid = self.app.player_id
        assert pid is not None
        try:
            storage.rename_wrestler(pid, self._selected_id, event.value)
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return
        self.app.notify("Renamed.", severity="information")
        self._cancel_rename_ui()
        await self._reload_list()

    @on(events.ScreenResume)
    async def roster_resumed(self) -> None:
        await self._reload_list()


class WrestlerCreateScreen(Screen[None]):
    """Single-screen creation with tab navigation and live starter-deck preview."""

    BINDINGS = [("escape", "back", "Back")]

    CSS = """
    #create_split {
        layout: horizontal;
        height: 100%;
    }
    #create_form {
        width: 45%;
        min-width: 36;
    }
    #create_preview_col {
        width: 1fr;
        border-left: solid $primary;
        padding-left: 1;
    }
    #deck_preview {
        text-style: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="create_split"):
            with Vertical(id="create_form", classes="panel"):
                yield Label("Create wrestler", id="create_title")
                yield Label("Name")
                yield Input(placeholder="Ring name", id="w_name")
                yield Label("Archetype (locked after creation)")
                yield Select(
                    [(a.value, a.value) for a in Archetype],
                    id="w_archetype",
                    allow_blank=False,
                )
                yield Label("Starting alignment (can change later in-game)")
                yield Select(
                    [(a.value, a.value) for a in Alignment],
                    id="w_alignment",
                    allow_blank=False,
                )
                yield Label("Gimmick")
                yield Select(
                    [(g.name, g.id) for g in GIMMICKS],
                    id="w_gimmick",
                    allow_blank=False,
                )
                with Horizontal():
                    yield Button("Save", variant="primary", id="w_save")
                    yield Button("Cancel", id="w_cancel")
            with VerticalScroll(id="create_preview_col", classes="panel"):
                yield Label("Starter deck (basic + archetype)", id="preview_title")
                yield Static("", id="deck_preview")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#w_name", Input).focus()
        # Child Select widgets initialize in their own mount; reading .value here can
        # still be Select.NULL and break Archetype(...). Defer the first preview.
        self.call_later(self._refresh_preview)

    def _archetype_from_ui(self) -> Archetype:
        sel = self.query_one("#w_archetype", Select)
        v = sel.selection
        if v is None:
            return Archetype.REGULAR
        return Archetype(str(v))

    def _alignment_from_ui(self) -> Alignment:
        sel = self.query_one("#w_alignment", Select)
        v = sel.selection
        if v is None:
            return Alignment.BABYFACE
        return Alignment(str(v))

    def _gimmick_id_from_ui(self) -> str:
        sel = self.query_one("#w_gimmick", Select)
        v = sel.selection
        if v is None:
            return GIMMICKS[0].id
        return str(v)

    def _refresh_preview(self) -> None:
        arch = self._archetype_from_ui()
        gimmick_sel = self.query_one("#w_gimmick", Select)
        gid = self._gimmick_id_from_ui()
        g = gimmick_by_id(gid)
        gline = f"Gimmick: {g.name} — {g.description}" if g else ""
        body = format_starter_deck_preview(arch)
        text = f"{gline}\n\n{body}" if gline else body
        self.query_one("#deck_preview", Static).update(text)

    @on(Select.Changed, "#w_archetype")
    @on(Select.Changed, "#w_gimmick")
    def preview_triggers(self) -> None:
        self._refresh_preview()

    def action_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#w_cancel")
    def cancel(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#w_save")
    def save(self) -> None:
        name = self.query_one("#w_name", Input).value
        arch = self._archetype_from_ui()
        align = self._alignment_from_ui()
        gid = self._gimmick_id_from_ui()
        pid = self.app.player_id
        assert pid is not None
        try:
            storage.save_new_wrestler(pid, name, arch, align, gid)
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return
        self.app.notify("Wrestler created.", severity="information")
        self.app.pop_screen()


class PvpScreen(Screen[None]):
    """Local head-to-head: two logins, then pick wrestlers; match is a stub."""

    BINDINGS = [("escape", "back", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self._step = 1
        self._p1: Account | None = None
        self._p2: Account | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="pvp_root"):
            yield Label("Head-to-head (local PVP)", id="pvp_title")
            with Container(id="pvp_step1"):
                yield Label("Player 1 — log in")
                yield Input(placeholder="Login name", id="p1_name")
                yield Input(placeholder="Password", password=True, id="p1_pw")
                yield Button("Continue", variant="primary", id="p1_go")
            with Container(id="pvp_step2"):
                yield Label("Player 2 — log in (must be a different account)")
                yield Input(placeholder="Login name", id="p2_name")
                yield Input(placeholder="Password", password=True, id="p2_pw")
                yield Button("Continue", variant="primary", id="p2_go")
            with Container(id="pvp_step3"):
                yield Label("Pick wrestlers")
                yield Select([], id="pvp_w1", prompt="Player 1 wrestler")
                yield Select([], id="pvp_w2", prompt="Player 2 wrestler")
                yield Button("Start match (stub)", variant="primary", id="pvp_start")
            with Container(id="pvp_step4"):
                yield Static("", id="pvp_stub_msg")
                yield Button("Back to menu", id="pvp_done")
            yield Button("Cancel", id="pvp_cancel")
        yield Footer()

    def on_mount(self) -> None:
        self._show_step(1)

    def _show_step(self, n: int) -> None:
        self._step = n
        for sid, step in (("pvp_step1", 1), ("pvp_step2", 2), ("pvp_step3", 3), ("pvp_step4", 4)):
            self.query_one(f"#{sid}", Container).display = step == n
        self.query_one("#pvp_cancel", Button).display = n < 4

    def action_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#pvp_cancel")
    def cancel_pvp(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#p1_go")
    def p1_go(self) -> None:
        name = self.query_one("#p1_name", Input).value
        pw = self.query_one("#p1_pw", Input).value
        try:
            self._p1 = auth.login(name, pw)
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return
        self._show_step(2)
        self.query_one("#p2_name", Input).focus()

    @on(Button.Pressed, "#p2_go")
    def p2_go(self) -> None:
        assert self._p1 is not None
        name = self.query_one("#p2_name", Input).value
        pw = self.query_one("#p2_pw", Input).value
        try:
            acc = auth.login(name, pw)
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return
        if acc.player_id == self._p1.player_id:
            self.app.notify("Player 2 must use a different account than Player 1.", severity="error")
            return
        self._p2 = acc
        w1 = storage.list_wrestlers(self._p1.player_id)
        w2 = storage.list_wrestlers(self._p2.player_id)
        if not w1:
            self.app.notify(f"{self._p1.login_name} has no wrestlers. Create one first.", severity="error")
            return
        if not w2:
            self.app.notify(f"{self._p2.login_name} has no wrestlers. Create one first.", severity="error")
            return
        s1 = self.query_one("#pvp_w1", Select)
        s2 = self.query_one("#pvp_w2", Select)
        opts1 = [(w.name, w.id) for w in w1]
        opts2 = [(w.name, w.id) for w in w2]
        s1.set_options(opts1)
        s2.set_options(opts2)
        if opts1:
            s1.value = opts1[0][1]
        if opts2:
            s2.value = opts2[0][1]
        self._show_step(3)

    @on(Button.Pressed, "#pvp_start")
    def start_stub(self) -> None:
        assert self._p1 is not None and self._p2 is not None
        s1 = self.query_one("#pvp_w1", Select)
        s2 = self.query_one("#pvp_w2", Select)
        v1, v2 = s1.value, s2.value
        if v1 is Select.BLANK or v2 is Select.BLANK or v1 is None or v2 is None:
            self.app.notify("Both players must pick a wrestler.", severity="error")
            return
        id1 = str(v1)
        id2 = str(v2)
        n1 = next(w.name for w in storage.list_wrestlers(self._p1.player_id) if w.id == id1)
        n2 = next(w.name for w in storage.list_wrestlers(self._p2.player_id) if w.id == id2)
        msg = (
            f"Match stub — deck combat not implemented yet.\n\n"
            f"{self._p1.login_name} → {n1}\n"
            f"{self._p2.login_name} → {n2}\n"
        )
        self.query_one("#pvp_stub_msg", Static).update(msg)
        self._show_step(4)

    @on(Button.Pressed, "#pvp_done")
    def pvp_done(self) -> None:
        self.app.pop_screen()
