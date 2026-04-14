# Pathologic Classic HD - Auto-Walk Mod

Toggles holding the W key so you don't have to manually hold it down while exploring.

**The W key is only simulated when `Game.exe` is the focused window** — alt-tabbing out automatically pauses the auto-walk, and it resumes when you go back to the game.

## Why not a "real" mod?

Pathologic Classic HD's engine (LifeStudio:HEAD) only supports modding textures, audio, text, and remapping keys to **existing** functions. There is no built-in "toggle walk" function — `forward` only works while held. The engine has no plugin/DLL mod support, so new input behavior can't be injected into the game files.

This external script is the standard community approach for this kind of feature.

## Option A: Run the pre-built .exe

1. Download `PathologicAutoWalk.exe` from Releases
2. Double-click it — no Python needed
3. Launch Pathologic Classic HD

## Option B: Run from source

```
pip install pynput pywin32
python autowalk.py
```

## Building the .exe yourself

```
pip install pyinstaller pynput pywin32
python build.py
```

The `.exe` will be in the `dist/` folder.

## Usage

1. Run `PathologicAutoWalk.exe` (or `python autowalk.py`)
2. Launch Pathologic Classic HD
3. A small settings window will appear where you can change keybinds
4. Press **F9** to toggle auto-walk on/off (default)
5. Press **F10** to quit the script (default)

## Settings Window

You can change these keys in the GUI at any time:

| Setting    | Default | Description                        |
|------------|---------|------------------------------------|
| Toggle key | F9      | Turns auto-walk on/off             |
| Quit key   | F10     | Exits the script                   |
| Walk key   | W       | The key that gets held for walking |

Accepts single letters (a-z, 0-9) or function keys (f1-f12).

## How It Works

- Uses `win32` APIs to check which `.exe` owns the foreground window
- Only sends the walk key when `Game.exe` (Pathologic) is focused
- Automatically releases the key when you alt-tab away
- Automatically re-presses the key when you return to the game

## Notes

- Works with both Steam and GOG versions
- If the game executable has a different name, edit `GAME_EXE` at the top of the script
