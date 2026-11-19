"""Bleep - a useless pixel blob that lives on your Windows desktop.

It follows your mouse, jumps when you click anywhere, falls asleep when you
stop moving, and gets angry if you hold the button. Quit: Ctrl+Alt+Q.
Pure standard library (tkinter + ctypes). MIT licensed.
"""
import ctypes
import math
import random
import sys
import time
import tkinter as tk
from datetime import datetime

if sys.platform != "win32":
    sys.exit("Bleep is a Windows desktop pet. Sorry!")

user32 = ctypes.windll.user32
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    user32.SetProcessDPIAware()


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def cursor():
    p = POINT()
    user32.GetCursorPos(ctypes.byref(p))
    return p.x, p.y


def key_down(vk):
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


# ---------------------------------------------------------------- config
S = 6                      # size of one "pixel" on screen
GW, GH = 14, 14            # sprite grid
W, H = 260, 230            # window size
KEY = "#010101"            # transparent color
BODY, DARK, LIGHT, ANGRY = "#3ddcc4", "#12332e", "#a8fff0", "#ff5c5c"

SHAPE = [
    "....oooooo....",
    "..oobbbbbboo..",
    ".obbhhbbbbbbo.",
    ".obhbbbbbbbbo.",
    "obbbbbbbbbbbbo",
    "obbbbbbbbbbbbo",
    "obbbbbbbbbbbbo",
    "obbbbbbbbbbbbo",
    "obbbbbbbbbbbbo",
    "obbbbbbbbbbbbo",
    ".obbbbbbbbbbo.",
    "..oooooooooo..",
]

QUOTES = [
    "boing!", "why did you do that", "I have no purpose", "this changes nothing",
    "ow. jk.", "wheee", "404: brain not found", "pls hire me", "I'm legally a blob",
    "got any snacks?", "I'm doing my best", "again!", "is this a job?",
    "sudo make me a sandwich", "I live in your RAM now", "have you tried turning me off?",
    "I'm not lazy, I'm in power-saving mode", "stop clicking, I'm working",
    "I read your files. they're boring.", "is this the real life?",
]
IDLE_QUOTES = [
    "hello?", "...", "you good?", "I'm bored", "do something", "I can see your tabs",
    "so... how's your day", "*stares*", "this is fine",
]
SLEEPY = ["zzz...", "5 more minutes", "nap time", "wake me never"]
ANNOYED = ["please stop", "I have rights", "that's 20 clicks. seek help", "my pixels hurt"]


class Pet:
    def __init__(self):
        self.root = r = tk.Tk()
        r.overrideredirect(True)
        r.attributes("-topmost", True)
        r.attributes("-transparentcolor", KEY)
        r.config(bg=KEY)
        self.cv = tk.Canvas(r, width=W, height=H, bg=KEY, highlightthickness=0)
        self.cv.pack()

        self.x = r.winfo_screenwidth() / 2
        self.y = r.winfo_screenheight() / 2
        self.face, self.idle, self.t = 1, 0, 0
        self.sq, self.jz, self.vz, self.spin = 0.0, 0.0, 0.0, 0
        self.clicks, self.was_down, self.last_click = 0, False, 0.0
        self.down_since, self.angry = None, False
        self.say_text, self.say_until = "", 0.0
        self.last_cur = cursor()
        self.moving = False
        self.quotes = list(QUOTES)
        if datetime.now().hour < 5:
            self.quotes += ["it's late. go to bed.", "why are we both awake"]

        self.say("hi. I live here now.", 3500)
        self.tick()
        r.mainloop()

    # ------------------------------------------------------------ helpers
    def say(self, text, ms=1500):
        self.say_text = text
        self.say_until = time.time() + ms / 1000

    def sleeping(self):
        return self.idle > 720          # ~12 s of no mouse movement

    def jump(self, power=11):
        if self.jz == 0:
            self.vz = power
            self.sq = -0.25

    # -------------------------------------------------------------- input
    def on_down(self, now):
        self.clicks += 1
        self.idle = 0
        if now - self.last_click < 0.3:
            self.spin = 24
            self.jump(14)
            self.say("wheeeeee!")
        else:
            self.jump(11)
            self.say(random.choice(ANNOYED) if self.clicks % 20 == 0 else random.choice(self.quotes))
        self.last_click = now
        self.down_since = now

    def on_up(self):
        if self.angry:
            self.angry = False
            self.jump(20)
            self.say("FINE. *yeet*", 1800)
        self.down_since = None

    # --------------------------------------------------------------- loop
    def tick(self):
        now = time.time()
        self.t += 1
        cx, cy = cursor()

        if key_down(0x11) and key_down(0x12) and key_down(0x51):   # Ctrl+Alt+Q
            self.root.destroy()
            return

        if abs(cx - self.last_cur[0]) + abs(cy - self.last_cur[1]) > 3:
            if self.sleeping():
                self.say("huh?! I'm up!", 1500)
            self.idle = 0
        else:
            self.idle += 1
        self.last_cur = (cx, cy)

        down = key_down(0x01)
        if down and not self.was_down:
            self.on_down(now)
        if not down and self.was_down:
            self.on_up()
        if down and self.down_since and not self.angry and now - self.down_since > 0.9:
            self.angry = True
            self.say("GRRR", 1500)
        self.was_down = down

        if self.idle == 720:
            self.say(random.choice(SLEEPY), 2500)
        elif self.idle and self.idle % 480 == 0 and not self.sleeping():
            self.say(random.choice(IDLE_QUOTES), 1800)

        # follow the cursor (stay ~120 px away so you can still click stuff)
        tx, ty = cx, cy + 40
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(cx - self.x, cy - self.y)
        self.moving = False
        if dist > 120 and not self.sleeping():
            sp = min((dist - 120) * 0.05 + 1.5, 10)
            n = math.hypot(dx, dy) or 1
            self.x += dx / n * sp
            self.y += dy / n * sp
            self.moving = True
            if abs(dx) > 4:
                self.face = 1 if dx > 0 else -1

        # jump physics
        if self.jz > 0 or self.vz > 0:
            self.jz += self.vz
            self.vz -= 0.9
            if self.jz <= 0:
                self.jz, self.vz, self.sq = 0.0, 0.0, 0.3
        self.sq *= 0.85
        if self.spin:
            self.spin -= 1

        self.draw(cx, cy)
        self.root.geometry(f"{W}x{H}+{int(self.x - W / 2)}+{int(self.y - H + 6 - self.jz)}")
        self.root.after(16, self.tick)

    # ------------------------------------------------------------ drawing
    def rect(self, c, r, w, h, color):
        if self.fe == -1:
            c = GW - c - w
        x0 = W / 2 + (c - GW / 2) * self.pw
        y0 = (H - 6) - (GH - r) * self.ph
        self.cv.create_rectangle(x0, y0, x0 + w * self.pw, y0 + h * self.ph, fill=color, outline="")

    def draw(self, cx, cy):
        cv = self.cv
        cv.delete("all")
        a = 1 + self.sq
        b = 1 - self.sq + (0.1 if self.jz > 0 else 0)
        if self.moving and self.jz == 0:
            b += math.sin(self.t * 0.35) * 0.05
        self.pw, self.ph = S * a, S * b
        self.fe = self.face
        if self.spin:
            self.fe = 1 if (self.spin // 3) % 2 else -1

        body = ANGRY if self.angry else BODY
        colors = {"o": DARK, "b": body, "h": LIGHT}
        for r, row in enumerate(SHAPE):
            c = 0
            while c < GW:
                ch = row[c]
                if ch == ".":
                    c += 1
                    continue
                e = c
                while e < GW and row[e] == ch:
                    e += 1
                self.rect(c, r, e - c, 1, colors[ch])
                c = e

        # feet (alternate while walking)
        lift = (self.t // 6) % 2 if self.moving and self.jz == 0 else 0
        self.rect(3, 12 - (1 if lift else 0), 3, 2, DARK)
        self.rect(8, 12 - (0 if lift else (1 if self.moving and self.jz == 0 else 0)), 3, 2, DARK)

        # eyes & mouth
        if self.sleeping():
            self.rect(2, 6, 4, 1, DARK)
            self.rect(8, 6, 4, 1, DARK)
            self.rect(6, 9, 2, 2, DARK)
        else:
            self.rect(2, 4, 4, 4, "#ffffff")
            self.rect(8, 4, 4, 4, "#ffffff")
            ex = max(-1, min(1, int((cx - self.x) / 40)))
            ey = max(-1, min(1, int((cy - (self.y - 40)) / 40)))
            self.rect(3 + ex, 5 + ey, 2, 2, DARK)
            self.rect(9 + ex, 5 + ey, 2, 2, DARK)
            if self.angry:
                self.rect(2, 3, 4, 1, DARK)
                self.rect(8, 3, 4, 1, DARK)
                self.rect(4, 9, 6, 1, DARK)
            elif self.jz > 0:
                self.rect(6, 9, 2, 2, DARK)           # "O" mouth in mid-air
            else:
                self.rect(4, 8, 1, 1, DARK)
                self.rect(5, 9, 4, 1, DARK)
                self.rect(9, 8, 1, 1, DARK)

        top = (H - 6) - GH * self.ph
        if self.sleeping():
            off = math.sin(self.t * 0.08) * 6
            cv.create_text(W / 2 + 55, top + 10 - off, text="Z", font=("Consolas", 16, "bold"), fill="#cfc8ff")
            cv.create_text(W / 2 + 72, top - 8 - off, text="z", font=("Consolas", 11, "bold"), fill="#cfc8ff")
        self.bubble(top)

    def bubble(self, top):
        if time.time() > self.say_until:
            return
        cv = self.cv
        t = cv.create_text(W / 2, max(40, top - 28), text=self.say_text,
                           font=("Consolas", 10, "bold"), fill=DARK, width=220)
        x0, y0, x1, y1 = cv.bbox(t)
        p = 7
        box = cv.create_rectangle(x0 - p, y0 - p, x1 + p, y1 + p, fill="white", outline=DARK, width=2)
        tail = cv.create_polygon(W / 2 - 6, y1 + p, W / 2 + 6, y1 + p, W / 2, y1 + p + 9,
                                 fill="white", outline="")
        l1 = cv.create_line(W / 2 - 6, y1 + p, W / 2, y1 + p + 9, fill=DARK, width=2)
        l2 = cv.create_line(W / 2 + 6, y1 + p, W / 2, y1 + p + 9, fill=DARK, width=2)
        for item in (box, tail, l1, l2, t):
            cv.tag_raise(item)


if __name__ == "__main__":
    Pet()
