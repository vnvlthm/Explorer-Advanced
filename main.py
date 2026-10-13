"""
Explorer Advance

One local NiceGUI app for the three Windows helpers: Cipher / EFS,
Robocopy, and PnPUtil. The home page is a picker; each tool is the
same UI as the standalone sibling.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import socket
import sys
from pathlib import Path
from types import ModuleType

from nicegui import ui

APP_DIR = Path(__file__).resolve().parent
APP_HOST = "127.0.0.1"
APP_PORT = 8768
APP_TITLE = "Explorer Advance"

os.environ["EXPLORER_SUITE"] = "1"
os.environ.setdefault("EXPLORER_SUITE_HOST", APP_HOST)
os.environ.setdefault("EXPLORER_SUITE_PORT", str(APP_PORT))


def load_tool(name: str, folder: Path) -> ModuleType:
    """Load apps/<name>/main.py so sibling imports (cipher_ops, …) still work."""
    folder_s = str(folder.resolve())
    if folder_s not in sys.path:
        sys.path.insert(0, folder_s)
    spec = importlib.util.spec_from_file_location(f"ea_{name}", folder / "main.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {name} from {folder}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


cipher_ui = load_tool("cipher", APP_DIR / "apps" / "cipher")
robocopy_ui = load_tool("robocopy", APP_DIR / "apps" / "robocopy")
pnp_ui = load_tool("pnputil", APP_DIR / "apps" / "pnputil")

TOOLS = (
    {
        "path": "/cipher",
        "icon": "lock",
        "badge": "Cipher / EFS",
        "title": "Find and encrypt files",
        "body": (
            "Scan a folder or every local NTFS drive for Encrypting File "
            "System items. Decrypt a selection, encrypt folders, and learn "
            "every cipher.exe switch. Wipe is documented and not wired."
        ),
        "tabs": "Find encrypted · Encrypt · Manual · Command map",
    },
    {
        "path": "/robocopy",
        "icon": "folder_copy",
        "badge": "Robocopy",
        "title": "Copy and compare folders",
        "body": (
            "Fill source → destination pairs, preview the exact robocopy "
            "command, confirm, and run. Mirror, Purge, and drive roots need "
            "an extra acknowledgement."
        ),
        "tabs": "Copy / Compare · Manual · Options guide · Command map",
    },
    {
        "path": "/pnputil",
        "icon": "developer_board",
        "badge": "PnPUtil",
        "title": "Inspect OEM drivers",
        "body": (
            "List third-party packages in the Windows driver store. Search, "
            "sort, inspect files and store IDs, export a selection. Delete, "
            "disable, and remove stay documented and not wired."
        ),
        "tabs": "Installed drivers · Manual · Command map",
    },
)


def _listen_label() -> str:
    host = os.environ.get("EXPLORER_SUITE_HOST", APP_HOST)
    port = os.environ.get("EXPLORER_SUITE_PORT", str(APP_PORT))
    return f"Local only · http://{host}:{port}"


def _open(path: str):
    def _go() -> None:
        ui.navigate.to(path)

    return _go


@ui.page("/")
def hub() -> None:
    ui.colors(primary="#1565C0", secondary="#00897B", accent="#FF8F00")
    ui.add_css(
        """
        .ea-hub { max-width: 80rem; }
        .ea-tool-card {
            min-height: 22rem;
            transition: box-shadow 0.15s ease, transform 0.15s ease;
            cursor: pointer;
        }
        .ea-tool-card:hover {
            box-shadow: 0 12px 28px rgba(21, 101, 192, 0.16);
            transform: translateY(-2px);
        }
        """
    )

    with ui.header().classes("items-center justify-between px-4"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("apps", size="md")
            ui.label("Explorer Advance").classes("text-h6")
            ui.badge("Cipher · Robocopy · PnPUtil").props("outline color=white")
        ui.label("Three Windows tools · one local app").classes(
            "text-caption opacity-80"
        )
        ui.label(_listen_label()).classes("text-caption opacity-70")

    with ui.column().classes("ea-hub w-full mx-auto px-6 py-8 gap-6"):
        with ui.column().classes("gap-1"):
            ui.label("Choose a tool").classes("text-h5")
            ui.label(
                "Each card opens the same app as the standalone GitHub sibling. "
                "Use the grid button in the header to come back here."
            ).classes("text-body1 text-grey-8")

        with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-3"):
            for tool in TOOLS:
                with ui.card().classes("ea-tool-card w-full p-6 flex flex-col").on(
                    "click", _open(tool["path"])
                ):
                    with ui.row().classes("items-center gap-3 w-full"):
                        ui.icon(tool["icon"], size="lg").classes("text-primary")
                        ui.badge(tool["badge"]).props("outline color=primary")
                    ui.label(tool["title"]).classes("text-h6 mt-4")
                    ui.label(tool["body"]).classes("text-body2 text-grey-8")
                    ui.label(tool["tabs"]).classes("text-caption text-grey-7 mt-2")
                    ui.space()
                    ui.button("Open", icon="arrow_forward", on_click=_open(tool["path"])).props(
                        "unelevated"
                    )

        ui.label(
            "Listens on this PC only (127.0.0.1). Settings for each tool stay "
            "in that tool’s own user_config.json, which is gitignored."
        ).classes("text-caption text-grey-7")


@ui.page("/cipher", title="Explorer Advance — Cipher")
def cipher_page() -> None:
    cipher_ui.index()


@ui.page("/robocopy", title="Explorer Advance — Robocopy")
def robocopy_page() -> None:
    robocopy_ui.index()


@ui.page("/pnputil", title="Explorer Advance — PnPUtil")
def pnp_page() -> None:
    pnp_ui.index()


def parse_server_args() -> argparse.Namespace:
    """Bind address: --host / --port, or EXPLORER_HOST / EXPLORER_PORT."""
    parser = argparse.ArgumentParser(description="Explorer Advance")
    parser.add_argument(
        "--host",
        default=os.environ.get("EXPLORER_HOST", APP_HOST),
        help="Listen address (default: 127.0.0.1). Use 127.0.0.2 if another "
        "app or Chrome extension already owns localhost.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("EXPLORER_PORT", str(APP_PORT))),
        help=f"HTTP port (default: {APP_PORT}).",
    )
    args, _ = parser.parse_known_args()
    return args


def port_in_use(host: str, port: int) -> bool:
    probe = "127.0.0.1" if host in {"0.0.0.0", "::", ""} else host
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((probe, port)) == 0


def pick_listen_port(host: str, preferred: int, *, span: int = 20) -> int:
    """Use `preferred` when free; otherwise the next free port in the span."""
    for port in range(preferred, preferred + span):
        if not port_in_use(host, port):
            return port
    return preferred


if __name__ in {"__main__", "__mp_main__"}:
    server = parse_server_args()
    port = pick_listen_port(server.host, server.port)
    os.environ["EXPLORER_SUITE_HOST"] = server.host
    os.environ["EXPLORER_SUITE_PORT"] = str(port)
    if port != server.port:
        print(
            f"Port {server.port} is already in use "
            f"(another copy of this app is probably still running).\n"
            f"Starting on http://{server.host}:{port} instead.\n"
            f"To keep a chosen port: close the other window, or start with "
            f"`py -3 main.py --port {port + 1}`.",
            file=sys.stderr,
        )
    ui.run(
        title=APP_TITLE,
        reload=False,
        host=server.host,
        port=port,
        show=True,
        favicon="🧰",
    )
