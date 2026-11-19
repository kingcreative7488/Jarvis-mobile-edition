#desktop.py
import os
import sys
import json
import shutil
import subprocess
import time
import platform
from pathlib import Path
from datetime import datetime

from core import outcome
from core.undo import push_undo

# pyautogui is gone from this file along with the generated-code sandbox that
# was the only thing using it — see the note below. Nothing here drives the
# mouse or the keyboard any more; that is computer_control's job.

_OS = platform.system()  # "Windows" | "Darwin" | "Linux"


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

def _get_api_key() -> str:
    path = _get_base_dir() / "config" / "api_keys.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]
    
def _get_desktop() -> Path:
    if _OS == "Linux":
        xdg = os.environ.get("XDG_DESKTOP_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Desktop"

# ─────────────────────────────────────────────────────────────────────────────
#  REMOVED IN MARK LVI: the generated-code path
# ─────────────────────────────────────────────────────────────────────────────
# This file used to carry three functions the rest of the project has no
# equivalent of: `_ask_gemini_for_desktop_action` asked Gemini to write Python
# for whatever the user described, `_build_sandbox` assembled a namespace, and
# `_execute_generated_code` ran the result with exec().
#
# WHY IT WENT
#     The sandbox was not one. Its rules — "NO subprocess", "NO file deletion",
#     "NO import statements" — were sentences in a PROMPT, with nothing in the
#     code enforcing any of them, and the namespace handed the generated code
#     `getattr`, the real `pathlib.Path`, `pyautogui` and, on Windows, `ctypes`.
#     Verified rather than assumed: from inside that namespace,
#     `getattr(getattr(().__class__, "__bases__")[0], "__subclasses__")()`
#     reaches `subprocess.Popen` in one line, and `Path.unlink` was never
#     hidden at all. The only thing standing between a stray instruction and
#     arbitrary code on the user's machine was the model choosing to behave.
#
#     It was also the one tool in this project that broke its own architecture.
#     Every other one of the thirty-eight declares typed parameters and lets the
#     model FILL THEM IN; this one asked the model to emit a program. The rest
#     of the file — wallpaper, organize, clean, list, stats — was already doing
#     it the right way, and those are what remain.
#
# WHAT REPLACED IT
#     Nothing new, because nothing was missing. Typing, clicking, hotkeys,
#     scrolling, screenshots and find-on-screen are `computer_control`; a
#     multi-step job on the screen is the `screen_agent` plugin; files are
#     `file_controller`. All of them are typed, checked and reversible in a way
#     generated code never was.
#
#     An action this file does not recognise is now a failure that names the
#     ones it does — the shape computer_settings has used since Mark LII —
#     rather than a prompt asking a model to invent something.


_ACTIONS = ("wallpaper", "wallpaper_url", "current_wallpaper",
            "organize", "clean", "list", "stats")


def _unknown(said: str) -> str:
    """An action this file does not have, answered with the ones it does.

    Spelling tolerance rather than a second model call: `difflib` matches
    "organise" to "organize" and "wallpapers" to "wallpaper" in microseconds,
    which is the same trick computer_settings uses for its fifty-six actions.
    Where the old code sent an unrecognised string to Gemini to have Python
    written for it, this says what is available and stops.
    """
    import difflib
    guess = difflib.get_close_matches(said.lower().strip(), _ACTIONS, n=1, cutoff=0.6)
    if guess:
        return outcome.ask(
            "desktop_control",
            f"'{said}' is not a desktop action - did you mean '{guess[0]}'?",
            said=said,
        )
    return outcome.failed(
        "desktop_control",
        f"'{said}' is not something this tool does. It handles only: "
        f"{', '.join(_ACTIONS)}. For typing, clicking or keyboard shortcuts "
        f"use computer_control; for files use file_controller",
        said=said,
    ) if said else outcome.failed(
        "desktop_control",
        f"no action was given - choose one of: {', '.join(_ACTIONS)}",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Wallpaper
# ─────────────────────────────────────────────────────────────────────────────
#  WHY IT FAILED NOW AND THEN
#      Not one bug but four, each intermittent on its own. Windows writes the
#      wallpaper to the registry after the call has returned, so reading it
#      back at once often saw the OLD value, and a change that had worked was
#      reported as unconfirmed. PNG and WEBP went through a temp BMP, so the
#      name read back never matched the name that was set. A downloaded
#      picture was deleted right after being set, which on macOS and Linux
#      takes the wallpaper away at the next login. And the macOS and Linux
#      branches threw away every exit code, so a refusal looked like success.
_WIN_NATIVE = {".bmp", ".dib", ".jpg", ".jpeg", ".jfif",
               ".png", ".gif", ".tif", ".tiff"}

_MAX_DOWNLOAD = 40 * 1024 * 1024        # a wallpaper, not a film


def _keep_dir() -> Path:
    """Where a downloaded or converted wallpaper is kept — permanently.

    This used to be `tempfile.mktemp()`, and the file was deleted the moment
    the wallpaper had been set. On Windows that survives by accident, because
    the shell transcodes the picture into a cache of its own; on macOS and
    Linux the desktop holds the path itself, so deleting the file takes the
    wallpaper away with it at the next login. A wallpaper is a file the system
    needs for as long as it remains the wallpaper.

    It lands beside the user's pictures rather than in the project, so it is
    somewhere they would look.
    """
    pictures = Path.home() / "Pictures"
    if _OS == "Linux":
        xdg = os.environ.get("XDG_PICTURES_DIR", "")
        if xdg and Path(xdg).is_dir():
            pictures = Path(xdg)
    base = pictures if pictures.is_dir() else _get_base_dir() / "config"
    keep = base / "Jarvis Wallpapers"
    keep.mkdir(parents=True, exist_ok=True)
    return keep


def _transcoded() -> Path:
    """Windows' own copy of the current wallpaper. Its timestamp is evidence."""
    return (Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
            / "Microsoft" / "Windows" / "Themes" / "TranscodedWallpaper")


def _prepare(path: Path) -> tuple[Path | None, str]:
    """The same picture in a format this platform's wallpaper setter accepts.

    Only the formats Windows genuinely cannot read are converted. The old code
    converted every PNG as well, which was unnecessary — Windows has taken PNG
    since 7 — and actively harmful: the converted copy went to a temp file, so
    the registry ended up pointing at a name the user had never heard of, and
    the read-back check then compared two unrelated file names and reported a
    successful change as unverified.
    """
    if _OS != "Windows" or path.suffix.lower() in _WIN_NATIVE:
        return path, ""
    try:
        from PIL import Image
    except ImportError:
        return None, (f"Windows cannot use a {path.suffix} image as a wallpaper "
                      f"and Pillow is not installed to convert it - "
                      f"run: pip install pillow")
    try:
        target = _keep_dir() / f"{path.stem}.jpg"
        with Image.open(path) as img:
            img.convert("RGB").save(target, "JPEG", quality=95)
        return target, ""
    except Exception as e:                                  # noqa: BLE001
        return None, f"the {path.suffix} image could not be converted: {e}"


def _read_current() -> str:
    """The wallpaper this desktop reports, as a bare path, or ''.

    Separate from `get_current_wallpaper()` on purpose. That one writes a
    sentence for the user and this one is read by code; the verification below
    used to pull the path back out of the sentence with `split(":", 1)`, which
    is a string parse standing between the tool and the truth.
    """
    try:
        if _OS == "Windows":
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Control Panel\Desktop") as key:
                val, _ = winreg.QueryValueEx(key, "Wallpaper")
            return str(val or "").strip()

        if _OS == "Darwin":
            result = subprocess.run(
                ["osascript", "-e",
                 'tell application "System Events" to get picture of desktop 1'],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=10,
            )
            return result.stdout.strip() if result.returncode == 0 else ""

        env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        if "gnome" in env or "unity" in env or "cinnamon" in env:
            schema = ("org.cinnamon.desktop.background" if "cinnamon" in env
                      else "org.gnome.desktop.background")
            result = subprocess.run(
                ["gsettings", "get", schema, "picture-uri"],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=10,
            )
            if result.returncode != 0:
                return ""
            raw = result.stdout.strip().strip("'\"")
            return _clean_path(raw)
        if "xfce" in env:
            result = subprocess.run(
                ["xfconf-query", "-c", "xfce4-desktop", "-p",
                 "/backdrop/screen0/monitor0/workspace0/last-image"],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=10,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        return ""
    except Exception:                                       # noqa: BLE001
        return ""


def _apply(path: Path) -> str:
    """Hand the picture to the platform. '' means it was accepted.

    Every branch used to throw its result away — `capture_output=True` with
    nothing reading it — so a refusal looked exactly like a success. macOS is
    the case that matters most: System Events needs Automation permission, and
    without it osascript fails with a message that was being discarded.
    """
    try:
        if _OS == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            user32.SystemParametersInfoW.restype = ctypes.c_bool
            user32.SystemParametersInfoW.argtypes = [
                ctypes.c_uint, ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_uint
            ]
            # SPI_SETDESKWALLPAPER, then write it to the profile and broadcast.
            ok = user32.SystemParametersInfoW(20, 0, str(path), 0x01 | 0x02)
            if not ok:
                code = ctypes.GetLastError()
                return f"Windows refused the image ({ctypes.WinError(code).strerror})"
            return ""

        if _OS == "Darwin":
            script = ('tell application "System Events" to tell every desktop '
                      f'to set picture to POSIX file "{path}"')
            result = subprocess.run(["osascript", "-e", script],
                                    capture_output=True, text=True,
                                    encoding="utf-8", errors="replace",
                                    timeout=20)
            if result.returncode != 0:
                detail = (result.stderr or "").strip().splitlines()
                hint = detail[-1] if detail else "osascript refused the request"
                if "not allowed" in hint.lower() or "-1743" in hint:
                    hint = ("macOS has not granted this app permission to "
                            "control System Events - System Settings, Privacy "
                            "& Security, Automation")
                return hint
            return ""

        env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        uri = f"file://{path}"

        def _run(cmd: list[str]) -> str:
            done = subprocess.run(cmd, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=20)
            if done.returncode != 0:
                return ((done.stderr or done.stdout or "").strip()
                        or f"{cmd[0]} exited {done.returncode}")
            return ""

        if "gnome" in env or "unity" in env or "cinnamon" in env:
            schema = ("org.cinnamon.desktop.background" if "cinnamon" in env
                      else "org.gnome.desktop.background")
            err = _run(["gsettings", "set", schema, "picture-uri", uri])
            if err:
                return err
            # Dark mode has its own key since GNOME 42 and a desktop that only
            # gets the light one changes back the moment the theme flips.
            _run(["gsettings", "set", schema, "picture-uri-dark", uri])
            return ""

        if "kde" in env:
            script = f"""
var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {{
    d = allDesktops[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file://{path}");
}}
"""
            for tool in ("qdbus", "qdbus6", "qdbus-qt6"):
                if not shutil.which(tool):
                    continue
                err = _run([tool, "org.kde.plasmashell", "/PlasmaShell",
                            "org.kde.PlasmaShell.evaluateScript", script])
                if not err:
                    return ""
            return "Plasma would not accept the wallpaper through qdbus"

        if "xfce" in env:
            return _run(["xfconf-query", "-c", "xfce4-desktop", "-p",
                         "/backdrop/screen0/monitor0/workspace0/last-image",
                         "-s", str(path)])

        if shutil.which("feh"):
            return _run(["feh", "--bg-scale", str(path)])
        return (f"this desktop ({env or 'unknown'}) has no wallpaper setter I "
                f"can drive - installing 'feh' would give me one")

    except FileNotFoundError as e:
        return f"the tool needed to set the wallpaper is not installed: {e}"
    except subprocess.TimeoutExpired:
        return "the desktop did not answer within 20 seconds"
    except Exception as e:                                  # noqa: BLE001
        return f"{type(e).__name__}: {e}"


def _verify(expected: Path, since: float) -> bool | None:
    """Did the wallpaper actually change? True, False, or None for unknowable.

    THE RACE THIS EXISTS FOR
        The old check read the wallpaper back the instant after setting it and
        compared names. Windows writes that registry value on its own schedule
        — the broadcast returns before the write lands — so a change that had
        worked perfectly was frequently reported as `unverified`, which the
        model then relays as "I asked and cannot confirm it". The user is
        looking straight at the new wallpaper while being told that.

        So it polls instead of sampling once. And where Windows reports its own
        transcoded cache rather than the path it was given, the timestamp on
        that cache answers the question just as well: it is rewritten every
        time the wallpaper changes.
    """
    deadline = time.monotonic() + 2.5
    reported = ""
    while True:
        reported = _read_current()
        if reported:
            try:
                if Path(reported).resolve() == expected.resolve():
                    return True
            except Exception:                               # noqa: BLE001
                pass
            if Path(reported).name.lower() == expected.name.lower():
                return True
        if _OS == "Windows":
            try:
                cache = _transcoded()
                if cache.exists() and cache.stat().st_mtime >= since - 1.0:
                    return True
            except OSError:
                pass
        if time.monotonic() >= deadline:
            break
        time.sleep(0.15)
    return False if reported else None


def _clean_path(text: str) -> str:
    """A path as the model or a desktop setting hands it over, made usable.

    Quotes around it, `~`, and a `file://` URI - GNOME reports its wallpaper as
    one, and on Windows `file:///C:/x.jpg` has to lose its leading slash.
    """
    from urllib.parse import unquote, urlparse
    raw = str(text or "").strip().strip('"').strip("'").strip()
    if raw.lower().startswith("file://"):
        raw = unquote(urlparse(raw).path)
        if _OS == "Windows" and len(raw) > 2 and raw[0] == "/" and raw[2] == ":":
            raw = raw[1:]
    return os.path.expanduser(raw)


def set_wallpaper(image_path: str) -> str:
    """Set the wallpaper, then READ IT BACK before saying it worked.

    Nothing underneath reports more than "your request was accepted": Windows
    returns a bool, osascript exits 0 whether or not the picture changed, and
    `feh` succeeds on a file the compositor then ignores. A wallpaper that did
    not change is also the one failure the user can see from across the room,
    so this is checked rather than claimed.
    """
    raw = _clean_path(image_path)
    if not raw:
        return outcome.ask("set_wallpaper", "which picture should I use?")
    path = Path(raw)
    if not path.is_file():
        return outcome.failed(
            "set_wallpaper",
            f"there is no file at '{raw}'. If the exact path is not known, "
            f"find the picture with file_controller (action='find') and call "
            f"again with the path it returns", path=raw)
    if path.suffix.lower() not in _IMAGE_EXTS:
        return outcome.failed("set_wallpaper",
                              f"'{path.name}' is not an image file", path=raw)
    path = path.resolve()

    prepared, problem = _prepare(path)
    if prepared is None:
        return outcome.failed("set_wallpaper", problem, image=path.name)

    previous = _read_current()
    since = time.time()
    err = _apply(prepared)
    if err:
        return outcome.failed("set_wallpaper", err, image=path.name)

    # Registered whether or not the change can be confirmed: if it DID happen,
    # the user must be able to take it back, and an undo that restores the
    # wallpaper that is already showing costs nothing.
    if previous and Path(previous).exists():
        old = Path(previous)
        push_undo(
            f"wallpaper → {path.name}",
            lambda: (f"Put {old.name} back." if not _apply(old)
                     else f"Could not put {old.name} back."),
        )

    verdict = _verify(prepared, since)
    if verdict is True:
        return outcome.done("set_wallpaper", image=path.name, verified=True)
    if verdict is None:
        return outcome.unverified(
            "set_wallpaper",
            "this desktop does not report which wallpaper it is using, so the "
            "change could not be read back",
            image=path.name)
    return outcome.unverified(
        "set_wallpaper",
        f"the desktop still reports '{Path(_read_current()).name}
