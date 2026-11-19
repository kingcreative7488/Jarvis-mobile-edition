#computer_settings.py
import json
import re
import shutil
import sys
import time
import subprocess
import platform
from pathlib import Path

from core.lazyimport import LazyModule, installed

# Imported on first USE, not at launch. This file has eighty-six `pyautogui.`
# call sites; not one of them changes — see core/lazyimport.py.
_PYAUTOGUI = installed("pyautogui")
_PYPERCLIP = installed("pyperclip")


def _configure_pyautogui(module) -> None:
    module.FAILSAFE = True
    module.PAUSE    = 0.05


pyautogui = LazyModule("pyautogui", _configure_pyautogui)
pyperclip = LazyModule("pyperclip")

from core import confirm, outcome
from core.undo import push_undo

_OS = platform.system()  # "Windows" | "Darwin" | "Linux"

if _OS == "Windows":
    _WIN_HIDE: dict = {"creationflags": subprocess.CREATE_NO_WINDOW}
else:
    _WIN_HIDE: dict = {}


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

def _get_api_key() -> str:
    path = _get_base_dir() / "config" / "api_keys.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]

def _get_macos_wifi_interface() -> str:
    try:
        result = subprocess.run(
            ["networksetup", "-listallhardwareports"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5
        )
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if "Wi-Fi" in line or "AirPort" in line:
                for j in range(i, min(i + 4, len(lines))):
                    if lines[j].startswith("Device:"):
                        return lines[j].split(":", 1)[1].strip()
    except Exception:
        pass
    return "en0" 

# ── Volume ───────────────────────────────────────────────────────────────────
# "Turn it up by 30", "set it to 100", "a bit quieter": the level is read and
# written as a NUMBER wherever the OS allows it, so the change is the one asked
# for. The media keys are only the fallback. The old code pressed the volume key
# five times whatever was asked — two points a press on Windows — which is how
# "volume up by 50" and, via volume_up, "volume to 100" both became +10.

def _number(value) -> int | None:
    """The whole number in a value: 40, 40.0, "40", "40%", "%40" -> 40.
    None when there is no number in it."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(round(value))
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(value))
    return int(round(float(m.group(0).replace(",", ".")))) if m else None


def _volume_step(delta: int) -> None:
    now = volume_get()
    if now is not None:
        volume_set(now + delta)
        return
    sign = "+" if delta > 0 else "-"
    if _OS == "Windows":
        key = "volumeup" if delta > 0 else "volumedown"
        for _ in range(max(1, round(abs(delta) / 2))):      # 2 points a press
            pyautogui.press(key)
    elif _OS == "Darwin":
        subprocess.run(["osascript", "-e",
            f"set volume output volume (output volume of (get volume settings) {sign} {abs(delta)})"],
            capture_output=True)
    else:
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{sign}{abs(delta)}%"],
            capture_output=True)


def volume_up(step: int = 10):
    _volume_step(abs(int(step)))


def volume_down(step: int = 10):
    _volume_step(-abs(int(step)))


def mute_get() -> bool | None:
    """Whether the sound is muted, or None where this system will not say."""
    try:
        if _OS == "Windows":
            return bool(_win_endpoint_volume().GetMute())
        if _OS == "Darwin":
            r = subprocess.run(["osascript", "-e", "output muted of (get volume settings)"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5)
            out = r.stdout.strip().lower()
            return True if out == "true" else False if out == "false" else None
        r = subprocess.run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5)
        low = r.stdout.lower()
        return True if "yes" in low else False if "no" in low else None
    except Exception:
        return None


def mute_set(muted: bool) -> None:
    """Muted, or not — as asked, never a toggle.

    'unmute' used to press the mute KEY, which is a toggle: on a machine that was
    not muted, asking to unmute muted it. The same was true of macOS, where both
    words ran "set volume with output muted"."""
    muted = bool(muted)
    if _OS == "Windows":
        try:
            _win_endpoint_volume().SetMute(1 if muted else 0, None)
            return
        except Exception as e:
            print(f"[Settings] pycaw mute failed, using the mute key: {e}")
            pyautogui.press("volumemute")
    elif _OS == "Darwin":
        subprocess.run(["osascript", "-e",
                        f"set volume output muted {'true' if muted else 'false'}"],
                       capture_output=True)
    else:
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1" if muted else "0"],
                       capture_output=True)


def volume_mute():
    mute_set(True)


def volume_unmute():
    mute_set(False)


def volume_toggle_mute():
    state = mute_get()
    if state is not None:
        mute_set(not state)
    elif _OS == "Windows":
        pyautogui.press("volumemute")
    elif _OS == "Darwin":
        subprocess.run(["osascript", "-e",
                        "set volume output muted not (output muted of (get volume settings))"],
                       capture_output=True)
    else:
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
                       capture_output=True)


def _win_endpoint_volume():
    """The Windows master-volume interface, across pycaw versions.

    TWO BUGS LIVED HERE, AND NEITHER ANNOUNCED ITSELF.

    1. `AudioUtilities.GetSpeakers()` used to return the raw COM device, and
       the code called `.Activate(...)` on it. Newer pycaw returns an
       `AudioDevice` WRAPPER instead, which has no `.Activate` — so every call
       raised AttributeError, was swallowed by the `except Exception: return
       None` around it, and `volume_get()` answered "this system does not
       report its volume" on a system that reports it fine. Undo for volume
       silently stopped registering, and so did every verification built on it.

    2. The percentage was computed as `10 ** (db / 20) * 100`, which converts
       decibels to an amplitude RATIO. That is not what the Windows slider
       shows: the slider is the scalar, and the two disagree by a lot —
       measured here, scalar 43% against a formula answering 0%.

    So: prefer the wrapper's own `EndpointVolume`, fall back to activating the
    inner device for older pycaw, and read the scalar rather than deriving a
    number from decibels.
    """
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    speakers = AudioUtilities.GetSpeakers()
    endpoint = getattr(speakers, "EndpointVolume", None)
    if endpoint is not None:
        return endpoint
    dev = getattr(speakers, "_dev", speakers)
    return cast(dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None),
                POINTER(IAudioEndpointVolume))


def volume_get() -> int | None:
    """Current master volume 0-100, or None if this platform will not say.

    Undo needs a "before" value, and reading one is cheap on every OS we
    support. Where it is not readable the action simply is not registered as
    undoable — a wrong undo is worse than no undo."""
    try:
        if _OS == "Windows":
            return max(0, min(100, round(
                _win_endpoint_volume().GetMasterVolumeLevelScalar() * 100)))
        if _OS == "Darwin":
            r = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5)
            return max(0, min(100, int(r.stdout.strip())))
        r = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5)
        m = re.search(r"(\d+)%", r.stdout)
        return max(0, min(100, int(m.group(1)))) if m else None
    except Exception:
        return None


def brightness_get() -> int | None:
    """Current brightness 0-100, or None where it cannot be read."""
    try:
        if _OS == "Windows":
            r = subprocess.run(
                ["powershell", "-Command",
                 "(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness)"
                 ".CurrentBrightness"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5, **_WIN_HIDE
            )
            return max(0, min(100, int(r.stdout.strip())))
        if _OS == "Linux" and shutil.which("brightnessctl"):
            cur = int(subprocess.run(["brightnessctl", "get"],
                                     capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5).stdout.strip())
            mx  = int(subprocess.run(["brightnessctl", "max"],
                                     capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5).stdout.strip())
            return max(0, min(100, round(cur * 100 / mx))) if mx else None
        if _OS == "Linux" and shutil.which("xrandr"):
            out = subprocess.run(["xrandr", "--verbose"], capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=5).stdout
            m = re.search(r"Brightness:\s*([\d.]+)", out)
            return max(0, min(100, round(float(m.group(1)) * 100))) if m else None
    except Exception:
        pass
    return None


def brightness_set(value: int) -> None:
    """Set brightness to an absolute percentage — "brightness to 70" — and the
    way undo puts back a value captured before a change."""
    value = max(0, min(100, int(value)))
    if _OS == "Windows":
        subprocess.run(
            ["powershell", "-Command",
             "(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods)"
             f".WmiSetBrightness(1, {value})"],
            capture_output=True, timeout=5, **_WIN_HIDE
        )
    elif _OS == "Darwin":
        # macOS has no command that takes a level, and its brightness keys move
        # it in sixteenths: to the bottom, then up to the level. Was a no-op.
        ups = round(value / 6.25)
        subprocess.run(["osascript",
                        "-e", 'tell application "System Events"',
                        "-e", "repeat 16 times", "-e", "key code 145", "-e", "end repeat",
                        "-e", f"repeat {ups} times", "-e", "key code 144", "-e", "end repeat",
                        "-e", "end tell"], capture_output=True, timeout=20)
    elif _OS == "Linux":
        if shutil.which("brightnessctl"):
            subprocess.run(["brightnessctl", "set", f"{value}%"], capture_output=True)
        elif shutil.which("xrandr"):
            _xrandr_brightness(target=value / 100)


def volume_set(value: int):
    value = max(0, min(100, int(value)))
    if _OS == "Windows":
        try:
            # Scalar, not decibels: this is the number the Windows slider shows,
            # so "set the volume to 40" lands where the user expects rather than
            # wherever a dB conversion happens to put it.
            endpoint = _win_endpoint_volume()
            endpoint.SetMasterVolumeLevelScalar(value / 100.0, None)
            # A level asked for is a level to be heard — the volume keys unmute
            # too. Setting 60 on a muted machine used to leave it silent.
            if value > 0 and endpoint.GetMute():
                endpoint.SetMute(0, None)
            return
        except Exception as e:
            # The old fallback pressed mute twice, which changes nothing. Each
            # volume key moves the slider two points: to the bottom, then up.
            print(f"[Settings] pycaw failed, using the volume keys: {e}")
            for _ in range(50):
                pyautogui.press("volumedown")
            for _ in range(round(value / 2)):
                pyautogui.press("volumeup")
    elif _OS == "Darwin":
        subprocess.run(["osascript", "-e", f"set volume output volume {value}"],
            capture_output=True)
        if value > 0:
            subprocess.run(["osascript", "-e", "set volume output muted false"],
                capture_output=True)
        return
    else:
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"],
            capture_output=True)
        if value > 0:
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"],
                capture_output=True)
        return

def _xrandr_brightness(target: float | None = None, delta: float = 0.0) -> None:
    """Linux without brightnessctl: xrandr's brightness on the first connected
    output, 0.1-1.0.

    Done in Python rather than the shell one-liner it replaces, which could never
    have worked: the Python it ran was inside double quotes and contained
    unescaped double quotes, so the shell stripped them and Python saw
    `[xrandr,--verbose]` — a NameError, every time."""
    out = subprocess.run(["xrandr", "--verbose"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=5).stdout
    name = next((line.split()[0] for line in out.splitlines() if " connected" in line), None)
    if not name:
        return
    m = re.search(r"Brightness:\s*([\d.]+)", out)
    current = float(m.group(1)) if m else 1.0
    new = target if target is not None else current + delta
    subprocess.run(["xrandr", "--output", name, "--brightness", f"{max(0.1, min(1.0, new)):.2f}"],
                   capture_output=True, timeout=5)


def _brightness_step(delta: int) -> None:
    if _OS == "Darwin":
        code = 144 if delta > 0 else 145
        presses = max(1, round(abs(delta) / 6.25))        # a key press is a sixteenth
        subprocess.run(["osascript", "-e", 'tell application "System Events"',
                        "-e", f"repeat {presses} times", "-e", f"key code {code}",
                        "-e", "end repeat", "-e", "end tell"], capture_output=True, timeout=15)
        return
    now = brightness_get()
    if now is not None:
        brightness_set(now + delta)
        return
    if _OS == "Linux" and shutil.which("xrandr"):
        _xrandr_brightness(delta=delta / 100)
    # Windows with no readable brightness is an external monitor, which WMI
    # cannot drive; the caller reports that it could not be read back.


def brightness_up(step: int = 10):
    _brightness_step(abs(int(step)))


def brightness_down(step: int = 10):
    _brightness_step(-abs(int(step)))

def close_app():
    """Removed. Closing an application now lives in computer_control.

    WHAT THIS USED TO BE, AND WHY IT HAD TO GO

        if _OS == "Darwin": pyautogui.hotkey("command", "q")
        else:               pyautogui.hotkey("alt", "f4")

    Two lines with no target. It sent the quit chord to WHATEVER WINDOW HAD
    FOCUS — and while somebody is talking to the assistant, the window with
    focus is very often the assistant. That is the whole of the bug people
    reported as "I asked it to close an app and it closed itself".

    It could not be fixed by aiming better. "The focused window" is the wrong
    idea: the user names an application, so the application is what has to be
    found. `computer_control` action='close_app' does that — matched against
    what is actually running, never the assistant's own process tree, asked
    politely so unsaved work survives, and checked afterwards.

    The function stays as a named refusal rather than disappearing, because a
    model that learnt the old name from an older prompt will still reach for
    it, and a KeyError here would surface as "computer_settings failed" with
    nothing to act on.
    """
    return outcome.failed(
        "close_app",
        "this action needs to know WHICH application to close - use the "
        "computer_control tool with action='close_app' and the application's "
        "name in 'app_name'",
    )

def close_window():
    if _OS == "Darwin": pyautogui.hotkey("command", "w")
    else:               pyautogui.hotkey("ctrl", "w")

def full_screen():
    if _OS == "Darwin": pyautogui.hotkey("ctrl", "command", "f")
    else:               pyautogui.press("f11")

def minimize_window():
    if _OS == "Darwin": pyautogui.hotkey("command", "m")
    else:               pyautogui.hotkey("win", "down")

def maximize_window():
    if _OS == "Darwin":
        subprocess.run(["osascript", "-e",
            'tell application "System Events" to keystroke "f" '
            'using {control down, command down}'],
            capture_output=True)
    elif _OS == "Windows":
        pyautogui.hotkey("win", "up")
    else:
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,maximized_vert,maximized_horz"],
                capture_output=True)
        except Exception:
            pyautogui.hotkey("super", "up")

def snap_left():
    if _OS == "Windows":
        pyautogui.hotkey("win", "left")
    elif _OS == "Darwin":
        # macOS has no built-in snap; try Rectangle app shortcut if installed
        try:
            subprocess.run(["open", "-a", "Rectangle"], capture_output=True, timeout=1)
        except Exception:
            pass
        pyautogui.hotkey("ctrl", "option", "left")
    else:  # Linux
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-e", "0,0,0,960,1080"],
                capture_output=True)
        except Exception:
            pass

def snap_right():
    if _OS == "Windows":
        pyautogui.hotkey("win", "right")
    elif _OS == "Darwin":
        try:
            subprocess.run(["open", "-a", "Rectangle"], capture_output=True, timeout=1)
        except Exception:
            pass
        pyautogui.hotkey("ctrl", "option", "right")
    else:  # Linux
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-e", "0,960,0,960,1080"],
                capture_output=True)
        except Exception:
            pass

def switch_window():
    if _OS == "Darwin": pyautogui.hotkey("command", "tab")
    else:               pyautogui.hotkey("alt", "tab")

def show_desktop():
    if _OS == "Darwin":   pyautogui.hotkey("fn", "f11")
    elif _OS == "Windows": pyautogui.hotkey("win", "d")
    else:                  pyautogui.hotkey("super", "d")

def open_task_manager():
    if _OS == "Windows":
        pyautogui.hotkey("ctrl", "shift", "esc")
    elif _OS == "Darwin":
        subprocess.Popen(["open", "-a", "Activity Monitor"])
    else:
        for cmd in [["gnome-system-monitor"], ["xfce4-taskmanager"], ["htop"]]:
            if subprocess.run(["which", cmd[0]], capture_output=True).returncode == 0:
                subprocess.Popen(cmd)
                break


def focus_search():
    if _OS == "Darwin": pyautogui.hotkey("command", "l")
    else:               pyautogui.hotkey
