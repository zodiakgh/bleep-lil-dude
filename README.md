# Bleep

A tiny pixel-art blob that lives on your Windows desktop. It follows your mouse, jumps when you click anywhere, naps when you stop moving, and rages if you hold the button. It does absolutely nothing useful.

No dependencies, just Python's standard library.

## Controls
- **Move the mouse**: Bleep follows (eyes included)
- **Click anywhere**: it jumps and says something dumb
- **Double-click**: spin
- **Hold the button**: rage. Release: *yeet*
- **Stop moving for 12 s**: nap
- **Click 20 times**: it begs you to stop
- **Ctrl + Alt + Q**: quit

## Run
```
python bleep.py
```

## Build the .exe
Locally on Windows: double-click `build.bat` (output in `dist/Bleep.exe`).

Or let GitHub do it: push the repo, go to **Actions > build-exe > Run workflow**, then download the artifact. Pushing a tag like `v1.0` also attaches `Bleep.exe` to a Release.

Note: unsigned executables can trigger a Windows SmartScreen warning ("More info" > "Run anyway").

## Make it yours
Edit `QUOTES` for new jokes, or `SHAPE` for a different body. PRs with worse jokes welcome.

## License
MIT
