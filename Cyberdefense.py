# -*- coding: utf-8 -*-
"""
================================================================================
  CYBER DEFENSE  -  Tower Defense inverse en Pyxel
--------------------------------------------------------------------------------
  Theme : tu es un VIRUS qui attaque un ordinateur.
  Tu envoies des virus sur les pistes du circuit imprime pour atteindre le CPU
  et faire grimper son taux de CHIFFREMENT jusqu'a 100% (= victoire).
  L'ordinateur se defend avec des tours (Antivirus, Firewall, Scanner, IA).

  Tout est dans ce seul fichier .py. Optimise pour tourner a 60 FPS.

  CONTROLES
    Souris        : cliquer les boutons (virus / upgrades / play-pause / vitesse)
    Touches 1..5  : envoyer Virus / Worm / Trojan / Ransomware / Bot
    Q / W / E     : ameliorer Vitesse / Vie / Degats
    ESPACE        : pause / reprise
    TAB           : changer la vitesse du jeu (x1 / x2 / x3)
    R             : recommencer (sur ecran de fin)
================================================================================
"""

import math
import random
import pyxel

# =============================================================================
#  CONSTANTES GLOBALES
# =============================================================================

WIDTH, HEIGHT = 256, 200      # taille de la fenetre (proche du classique Pyxel)
TOPH = 15                     # hauteur de la barre d'info du haut
PANELY = 164                  # ordonnee du panneau du bas
FIELD_BOTTOM = PANELY         # bas de la zone de jeu

MAX_WAVE = 20                 # nombre total de vagues (defenses de + en + dures)
WAVE_TIME = 900               # duree d'une vague en "pas de simulation" (~15 s)
START_BITS = 350              # BITS de depart
START_RESERVE = 30            # reserve de virus de depart (VIRUS LIFE)

# --- Indices de couleurs (palette neon redefinie plus bas) -------------------
C_BG      = 0    # quasi noir
C_BOARD1  = 1    # vert tres sombre
C_BOARD2  = 2    # vert sombre (grille PCB)
C_TRACE   = 3    # vert moyen (pistes)
C_GREEN   = 4    # vert neon
C_CYAN    = 5    # cyan neon
C_TEAL    = 6    # cyan sombre
C_WHITE   = 7    # blanc / clair
C_RED     = 8    # rouge neon
C_DRED    = 9    # rouge sombre
C_YELLOW  = 10   # jaune (pins / or)
C_VIOLET  = 11   # violet neon
C_DVIOLET = 12   # violet sombre
C_SLATE   = 13   # bleu ardoise (puces)
C_LSLATE  = 14   # ardoise clair
C_ORANGE  = 15   # orange accent

# Palette neon "cyber" appliquee a l'init de Pyxel.
PALETTE = [
    0x0a0e14, 0x0d1f17, 0x123524, 0x1a5c3a,
    0x2ecc71, 0x00ffc8, 0x0fa3a3, 0xe6f7ff,
    0xff2e63, 0xb01030, 0xffd23f, 0x9b5de5,
    0x5a2a8a, 0x2b3a55, 0x4a5d7e, 0xff8c42,
]

# --- Le chemin des virus (coordonnees ecran, segments axe-alignes) -----------
# Depart a gauche (INFECTION ENTRY), arrivee en haut a droite (CPU).
PATH_POINTS = [
    (-10, 48), (46, 48), (46, 102), (106, 102), (106, 54),
    (164, 54), (164, 128), (214, 128), (214, 40),
]

# --- Emplacements (fixes) des defenses de l'ordinateur -----------------------
# (x, y, type). Elles s'activent progressivement au fil des vagues.
SLOTS = [
    (22,  66,  "ANTIVIRUS"),
    (68,  72,  "FIREWALL"),
    (78,  84,  "SCANNER"),
    (130, 74,  "ANTIVIRUS"),
    (134, 32,  "AI"),
    (192, 86,  "ANTIVIRUS"),
    (186, 146, "FIREWALL"),
    (242, 96,  "SCANNER"),
]

# --- Caracteristiques des virus (unites du joueur) ---------------------------
# cost  : prix en BITS         hp     : points de vie
# speed : pixels / pas         dmg    : degats infliges aux tours (par contact)
# enc   : % de chiffrement ajoute si le virus atteint le CPU
# col   : couleur              stealth: invisible (sauf si revele par un Scanner)
VIRUS_TYPES = {
    "VIRUS":      dict(cost=50,  hp=22, speed=0.50, dmg=2.0, enc=2,  col=C_GREEN,  stealth=False),
    "WORM":       dict(cost=75,  hp=15, speed=1.05, dmg=1.5, enc=2,  col=C_CYAN,   stealth=False),
    "TROJAN":     dict(cost=100, hp=48, speed=0.45, dmg=3.0, enc=4,  col=C_VIOLET, stealth=True),
    "RANSOMWARE": dict(cost=150, hp=75, speed=0.35, dmg=4.0, enc=10, col=C_RED,    stealth=False),
    "BOT":        dict(cost=80,  hp=32, speed=0.62, dmg=5.0, enc=3,  col=C_YELLOW, stealth=False),
}
VIRUS_ORDER = ["VIRUS", "WORM", "TROJAN", "RANSOMWARE", "BOT"]
VIRUS_NAMES = {"VIRUS": "VIRUS", "WORM": "WORM", "TROJAN": "TROJAN",
               "RANSOMWARE": "RANSOM", "BOT": "BOT"}

# --- Caracteristiques des tours (defenses de l'ordinateur) -------------------
# range   : portee        dmg  : degats par tir       cooldown : pas entre 2 tirs
# slow    : ralentissement (firewall)   reveal : revele les virus furtifs
TOWER_TYPES = {
    "ANTIVIRUS": dict(range=34, dmg=6,  cooldown=22, hp=40, col=C_CYAN,   slow=0,    reveal=False),
    "FIREWALL":  dict(range=28, dmg=0,  cooldown=0,  hp=55, col=C_ORANGE, slow=0.45, reveal=False),
    "SCANNER":   dict(range=40, dmg=2,  cooldown=10, hp=30, col=C_RED,    slow=0,    reveal=True),
    "AI":        dict(range=46, dmg=14, cooldown=14, hp=70, col=C_VIOLET, slow=0,    reveal=False),
}

# =============================================================================
#  OUTILS GEOMETRIE (chemin)
# =============================================================================

def build_path(points):
    """Pre-calcule les segments du chemin et la longueur totale."""
    segs, total = [], 0.0
    for i in range(len(points) - 1):
        (x1, y1), (x2, y2) = points[i], points[i + 1]
        length = math.hypot(x2 - x1, y2 - y1)
        segs.append((x1, y1, x2, y2, length, total))
        total += length
    return segs, total

PATH_SEGS, PATH_TOTAL = build_path(PATH_POINTS)

def pos_at(dist):
    """Renvoie la position (x, y) a la distance 'dist' le long du chemin."""
    if dist <= 0:
        return PATH_POINTS[0]
    for (x1, y1, x2, y2, length, start) in PATH_SEGS:
        if dist <= start + length or (start + length) >= PATH_TOTAL:
            t = 0 if length == 0 else (dist - start) / length
            t = max(0.0, min(1.0, t))
            return (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
    return PATH_POINTS[-1]

def dist2(ax, ay, bx, by):
    """Distance au carre (evite la racine quand on compare a une portee)."""
    dx, dy = ax - bx, ay - by
    return dx * dx + dy * dy

# =============================================================================
#  ENTITES
# =============================================================================

class Virus:
    """Une unite envoyee par le joueur. Avance le long du chemin vers le CPU."""
    def __init__(self, kind, stats):
        self.kind = kind
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.speed = stats["speed"]
        self.dmg = stats["dmg"]
        self.enc = stats["enc"]
        self.col = stats["col"]
        self.stealth = stats["stealth"]
        self.dist = 0.0
        self.x, self.y = pos_at(0.0)
        self.slow_timer = 0      # ralenti par un firewall tant que > 0
        self.reveal_timer = 0    # revele par un scanner tant que > 0
        self.hit_flash = 0       # clignote en blanc quand touche
        self.dead = False
        self.reached = False     # a atteint le CPU

    def targetable_by_shooter(self):
        """Les tours offensives ne ciblent pas un furtif non revele."""
        return (not self.stealth) or (self.reveal_timer > 0)


class Tower:
    """Une defense de l'ordinateur, posee sur un emplacement (slot)."""
    def __init__(self, x, y, kind, scale):
        t = TOWER_TYPES[kind]
        self.x, self.y = x, y
        self.kind = kind
        self.range = t["range"]
        self.range2 = t["range"] * t["range"]
        self.dmg = t["dmg"] * scale
        self.cooldown = t["cooldown"]
        self.slow = t["slow"]
        self.reveal = t["reveal"]
        self.col = t["col"]
        self.max_hp = t["hp"] * scale
        self.hp = self.max_hp
        self.cd = random.randint(0, max(1, t["cooldown"]))
        self.fire_anim = 0
        self.beam = None         # (tx, ty, timer) pour dessiner le tir
        self.alive = True


class Particle:
    """Petite particule d'effet visuel (explosion, etincelle)."""
    __slots__ = ("x", "y", "vx", "vy", "life", "col")
    def __init__(self, x, y, vx, vy, life, col):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.col = col

# =============================================================================
#  JEU
# =============================================================================

class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="CYBER DEFENSE", fps=60)
        pyxel.mouse(True)
        # Palette neon personnalisee
        for i, c in enumerate(PALETTE):
            pyxel.colors[i] = c
        self._init_sounds()
        self._build_decor()
        self.reset()
        pyxel.run(self.update, self.draw)

    # ----------------------------------------------------------------- sons
    def _init_sounds(self):
        # 0: bip (envoi de virus) / 1: tir / 2: explosion / 3: alerte CPU
        pyxel.sounds[0].set("c3", "s", "5", "n", 8)
        pyxel.sounds[1].set("a2c2", "p", "4", "n", 6)
        pyxel.sounds[2].set("f1c1", "n", "6", "f", 14)
        pyxel.sounds[3].set("c3e3g3", "t", "5", "n", 12)
        pyxel.sounds[4].set("c4g3e3c3", "s", "6", "f", 18)   # defaite
        pyxel.sounds[5].set("c3e3g3c4e4", "t", "6", "n", 16) # victoire

    def _play(self, ch, snd):
        try:
            pyxel.play(ch, snd)
        except Exception:
            pass

    # --------------------------------------------------------------- decor
    def _build_decor(self):
        """Genere (une seule fois) les elements decoratifs du circuit."""
        rng = random.Random(7)
        self.chips = []   # petites puces : (x, y, w, h)
        self.caps = []    # condensateurs : (x, y, r)
        self.pads = []    # plots de soudure : (x, y)
        for _ in range(22):
            w = rng.choice([8, 10, 12, 14])
            h = rng.choice([6, 8, 10])
            x = rng.randint(4, WIDTH - w - 4)
            y = rng.randint(TOPH + 4, FIELD_BOTTOM - h - 4)
            self.chips.append((x, y, w, h))
        for _ in range(14):
            x = rng.randint(8, WIDTH - 8)
            y = rng.randint(TOPH + 6, FIELD_BOTTOM - 6)
            self.caps.append((x, y, rng.choice([2, 3, 4])))
        for _ in range(60):
            self.pads.append((rng.randint(2, WIDTH - 2),
                              rng.randint(TOPH + 2, FIELD_BOTTOM - 2)))

    # --------------------------------------------------------------- reset
    def reset(self):
        self.state = "PLAY"           # PLAY / WIN / LOSE
        self.bits = START_BITS
        self.reserve = START_RESERVE
        self.encryption = 0.0
        self.wave = 1
        self.wave_timer = 0
        self.bit_timer = 0
        self.speed = 1                # x1 / x2 / x3
        self.paused = False
        self.viruses = []
        self.particles = []
        # multiplicateurs d'amelioration (appliques a l'envoi)
        self.upg = {"speed": 1.0, "hp": 1.0, "dmg": 1.0}
        self.upg_lvl = {"speed": 0, "hp": 0, "dmg": 0}
        self.active_count = 2
        self.build_towers()
        # zones cliquables (calculees une fois)
        self._make_buttons()

    # ----------------------------------------------------- boutons (rects)
    def _make_buttons(self):
        self.virus_btns = []          # (kind, x, y, w, h)
        bx, by, bw, bh, gap = 3, 167, 33, 30, 1
        for i, k in enumerate(VIRUS_ORDER):
            self.virus_btns.append((k, bx + i * (bw + gap), by, bw, bh))
        self.upg_btns = {              # key -> (x, y, w, h)
            "speed": (175, 166, 36, 9),
            "hp":    (175, 177, 36, 9),
            "dmg":   (175, 188, 36, 9),
        }
        self.pause_btn = (214, 166, 38, 10)
        self.speed_btns = [            # (mult, x, y, w, h)
            (1, 214, 181, 12, 14),
            (2, 227, 181, 12, 14),
            (3, 240, 181, 12, 14),
        ]

    # --------------------------------------------------------- gestion tours
    def build_towers(self):
        """(Re)construit les defenses actives pour la vague courante."""
        scale = 1.0 + 0.12 * (self.wave - 1)
        self.towers = []
        for i in range(min(self.active_count, len(SLOTS))):
            x, y, kind = SLOTS[i]
            self.towers.append(Tower(x, y, kind, scale))

    def advance_wave(self):
        if self.wave >= MAX_WAVE:
            return
        self.wave += 1
        # plus de tours activees, + renforcement (reconstruction complete)
        self.active_count = min(len(SLOTS), 2 + self.wave // 2)
        self.build_towers()
        self._play(3, 3)

    # ============================================================== UPDATE
    def update(self):
        # Ecrans de fin : on attend R (ou clic) pour relancer
        if self.state in ("WIN", "LOSE"):
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset()
            return

        self.handle_input()

        if not self.paused:
            for _ in range(self.speed):
                self.step()
                if self.state != "PLAY":
                    break
            self.check_end()

    # ------------------------------------------------------- entrees joueur
    def handle_input(self):
        # --- clavier : envoi de virus
        keys = [pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3, pyxel.KEY_4, pyxel.KEY_5]
        for i, k in enumerate(keys):
            if pyxel.btnp(k):
                self.spawn(VIRUS_ORDER[i])
        # --- clavier : ameliorations
        if pyxel.btnp(pyxel.KEY_Q):
            self.upgrade("speed")
        if pyxel.btnp(pyxel.KEY_W):
            self.upgrade("hp")
        if pyxel.btnp(pyxel.KEY_E):
            self.upgrade("dmg")
        # --- clavier : pause / vitesse
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.paused = not self.paused
        if pyxel.btnp(pyxel.KEY_TAB):
            self.speed = self.speed % 3 + 1

        # --- souris
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            for (k, x, y, w, h) in self.virus_btns:
                if x <= mx < x + w and y <= my < y + h:
                    self.spawn(k)
            for key, (x, y, w, h) in self.upg_btns.items():
                if x <= mx < x + w and y <= my < y + h:
                    self.upgrade(key)
            px, py, pw, ph = self.pause_btn
            if px <= mx < px + pw and py <= my < py + ph:
                self.paused = not self.paused
            for (mult, x, y, w, h) in self.speed_btns:
                if x <= mx < x + w and y <= my < y + h:
                    self.speed = mult

    def spawn(self, kind):
        """Envoie un virus si le joueur a assez de BITS et de reserve."""
        st = VIRUS_TYPES[kind]
        if self.bits < st["cost"] or self.reserve <= 0:
            return
        self.bits -= st["cost"]
        self.reserve -= 1
        stats = dict(st)
        stats["hp"] = st["hp"] * self.upg["hp"]
        stats["speed"] = st["speed"] * self.upg["speed"]
        stats["dmg"] = st["dmg"] * self.upg["dmg"]
        self.viruses.append(Virus(kind, stats))
        self._play(0, 0)

    def upgrade(self, key):
        """Ameliore globalement les futurs virus (vitesse / vie / degats)."""
        lvl = self.upg_lvl[key]
        if lvl >= 5:
            return
        cost = 60 * (lvl + 1)
        if self.bits < cost:
            return
        self.bits -= cost
        self.upg_lvl[key] += 1
        if key == "speed":
            self.upg["speed"] += 0.15
        elif key == "hp":
            self.upg["hp"] += 0.20
        elif key == "dmg":
            self.upg["dmg"] += 0.25
        self._play(0, 0)

    # ----------------------------------------------- un pas de simulation
    def step(self):
        # --- BITS passifs
        self.bit_timer += 1
        if self.bit_timer >= 25:
            self.bit_timer = 0
            self.bits += 1
        # --- avancee des vagues
        self.wave_timer += 1
        if self.wave_timer >= WAVE_TIME and self.wave < MAX_WAVE:
            self.wave_timer = 0
            self.advance_wave()

        # --- 1) auras des tours (revele + ralentissement)
        for t in self.towers:
            if not t.alive:
                continue
            if t.reveal or t.slow > 0:
                for v in self.viruses:
                    if dist2(t.x, t.y, v.x, v.y) <= t.range2:
                        if t.reveal:
                            v.reveal_timer = 30
                        if t.slow > 0:
                            v.slow_timer = 4

        # --- 2) tirs des tours offensives
        for t in self.towers:
            if not t.alive:
                continue
            if t.beam:
                bx, by, bt = t.beam
                bt -= 1
                t.beam = (bx, by, bt) if bt > 0 else None
            if t.fire_anim > 0:
                t.fire_anim -= 1
            if t.dmg <= 0:
                continue
            if t.cd > 0:
                t.cd -= 1
                continue
            target = self.pick_target(t)
            if target:
                target.hp -= t.dmg
                target.hit_flash = 3
                t.cd = t.cooldown
                t.fire_anim = 4
                t.beam = (target.x, target.y, 4)
                if pyxel.frame_count % 2 == 0:
                    self._play(1, 1)
                if target.hp <= 0:
                    target.dead = True
                    self.add_explosion(target.x, target.y, target.col, 8)
                    self._play(2, 2)

        # --- 3) deplacement des virus
        for v in self.viruses:
            if v.dead:
                continue
            if v.slow_timer > 0:
                v.slow_timer -= 1
            if v.reveal_timer > 0:
                v.reveal_timer -= 1
            if v.hit_flash > 0:
                v.hit_flash -= 1
            spd = v.speed * (0.45 if v.slow_timer > 0 else 1.0)
            v.dist += spd
            if v.dist >= PATH_TOTAL:
                # atteint le CPU : le chiffrement grimpe
                v.reached = True
                v.dead = True
                self.encryption = min(100.0, self.encryption + v.enc)
                self.bits += 12
                self.add_explosion(v.x, v.y, v.col, 10)
                self._play(3, 3)
            else:
                v.x, v.y = pos_at(v.dist)

        # --- 4) les virus endommagent les tours qu'ils longent
        for t in self.towers:
            if not t.alive:
                continue
            for v in self.viruses:
                if v.dead:
                    continue
                if dist2(t.x, t.y, v.x, v.y) <= 100:   # ~10 px
                    t.hp -= v.dmg * 0.06
                    if t.hp <= 0:
                        t.alive = False
                        t.hp = 0
                        self.bits += 35           # recompense : defense detruite
                        self.add_explosion(t.x, t.y, t.col, 16)
                        self._play(2, 2)
                        break

        # --- 5) nettoyage + particules
        self.viruses = [v for v in self.viruses if not v.dead]
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vx *= 0.90
            p.vy *= 0.90
            p.life -= 1
        self.particles = [p for p in self.particles if p.life > 0]

    def pick_target(self, t):
        """Cible le virus le plus avance (plus proche du CPU) dans la portee."""
        best, best_d = None, -1.0
        for v in self.viruses:
            if v.dead or not v.targetable_by_shooter():
                continue
            if dist2(t.x, t.y, v.x, v.y) <= t.range2 and v.dist > best_d:
                best, best_d = v, v.dist
        return best

    def add_explosion(self, x, y, col, n):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            s = random.uniform(0.4, 1.8)
            self.particles.append(
                Particle(x, y, math.cos(a) * s, math.sin(a) * s,
                         random.randint(8, 18), col))

    def check_end(self):
        if self.encryption >= 100:
            self.state = "WIN"
            self._play(3, 5)
        elif self.reserve <= 0 and len(self.viruses) == 0:
            self.state = "LOSE"
            self._play(3, 4)

    # ================================================================ DRAW
    def draw(self):
        pyxel.cls(C_BG)
        self.draw_board()
        self.draw_path()
        self.draw_entry()
        self.draw_towers()
        self.draw_viruses()
        self.draw_particles()
        self.draw_cpu()
        self.draw_topbar()
        self.draw_panel()
        if self.paused and self.state == "PLAY":
            self.draw_center_overlay("PAUSE", C_CYAN, "")
        if self.state == "WIN":
            self.draw_center_overlay("SYSTEME COMPROMIS",
                                     C_GREEN, "VICTOIRE  -  R pour rejouer")
        elif self.state == "LOSE":
            self.draw_center_overlay("VIRUS ERADIQUES",
                                     C_RED, "GAME OVER  -  R pour rejouer")

    # ------------------------------------------------------- carte / decor
    def draw_board(self):
        # fond de carte mere
        pyxel.rect(0, TOPH, WIDTH, FIELD_BOTTOM - TOPH, C_BOARD1)
        # grille de pistes faible (effet PCB)
        for x in range(0, WIDTH, 16):
            pyxel.line(x, TOPH, x, FIELD_BOTTOM, C_BOARD2)
        for y in range(TOPH, FIELD_BOTTOM, 16):
            pyxel.line(0, y, WIDTH, y, C_BOARD2)
        # plots de soudure
        for (x, y) in self.pads:
            pyxel.pset(x, y, C_TRACE)
        # condensateurs
        for (x, y, r) in self.caps:
            pyxel.circ(x, y, r, C_SLATE)
            pyxel.circb(x, y, r, C_LSLATE)
            pyxel.pset(x, y, C_YELLOW)
        # petites puces generiques
        for (x, y, w, h) in self.chips:
            pyxel.rect(x, y, w, h, C_SLATE)
            pyxel.rectb(x, y, w, h, C_LSLATE)
            for px in range(x + 1, x + w - 1, 3):
                pyxel.pset(px, y - 1, C_YELLOW)
                pyxel.pset(px, y + h, C_YELLOW)
        # composants nommes
        self._labeled_chip(70, 118, 70, 14, "RAM", C_SLATE, C_CYAN)
        self._labeled_chip(118, 22, 28, 16, "BIOS", C_DVIOLET, C_VIOLET)
        self._labeled_chip(208, 148, 40, 14, "GPU", C_SLATE, C_GREEN)
        self._fan(28, 134, 15)

    def _labeled_chip(self, x, y, w, h, label, fill, edge):
        pyxel.rect(x, y, w, h, fill)
        pyxel.rectb(x, y, w, h, edge)
        for px in range(x + 2, x + w - 1, 4):
            pyxel.pset(px, y - 1, C_YELLOW)
            pyxel.pset(px, y + h, C_YELLOW)
        self._text_center(x + w // 2, y + h // 2 - 2, label, edge)

    def _fan(self, cx, cy, r):
        pyxel.circ(cx, cy, r, C_SLATE)
        pyxel.circb(cx, cy, r, C_LSLATE)
        ang = pyxel.frame_count * 0.15
        for i in range(5):
            a = ang + i * (math.tau / 5)
            x2 = cx + math.cos(a) * (r - 3)
            y2 = cy + math.sin(a) * (r - 3)
            pyxel.line(cx, cy, x2, y2, C_LSLATE)
        pyxel.circ(cx, cy, 2, C_BG)

    def draw_path(self):
        # piste epaisse (vert sombre) + cœur lumineux (cyan)
        for (x1, y1, x2, y2, length, start) in PATH_SEGS:
            if abs(y1 - y2) < 1:            # horizontal
                xa, xb = min(x1, x2), max(x1, x2)
                pyxel.rect(xa, y1 - 4, xb - xa + 1, 9, C_TRACE)
                pyxel.rect(xa, y1 - 1, xb - xa + 1, 3, C_TEAL)
            else:                           # vertical
                ya, yb = min(y1, y2), max(y1, y2)
                pyxel.rect(x1 - 4, ya, 9, yb - ya + 1, C_TRACE)
                pyxel.rect(x1 - 1, ya, 3, yb - ya + 1, C_TEAL)
        # coins
        for (x, y) in PATH_POINTS:
            pyxel.rect(x - 4, y - 4, 9, 9, C_TRACE)
            pyxel.rect(x - 1, y - 1, 3, 3, C_TEAL)
        # flux de donnees (points lumineux qui circulent)
        offset = pyxel.frame_count * 0.7
        d = 0
        while d < PATH_TOTAL:
            x, y = pos_at((d + offset) % PATH_TOTAL)
            pyxel.pset(int(x), int(y), C_GREEN)
            d += 18

    def draw_entry(self):
        # INFECTION ENTRY : chevrons rouges qui pointent vers la droite
        ex, ey = 0, 48
        pyxel.rectb(-1, ey - 8, 18, 16, C_RED)
        for i in range(3):
            cx = 2 + i * 5 + int((pyxel.frame_count // 4) % 5)
            pyxel.tri(cx, ey - 3, cx, ey + 3, cx + 3, ey, C_RED)
        pyxel.text(2, ey - 14, "IN", C_RED)

    # ------------------------------------------------------------ tours
    def draw_towers(self):
        for t in self.towers:
            self._draw_tower(t)

    def _draw_tower(self, t):
        x, y = int(t.x), int(t.y)
        if not t.alive:
            # emplacement detruit (grise / vide)
            pyxel.rectb(x - 5, y - 5, 11, 11, C_BOARD2)
            pyxel.line(x - 3, y - 3, x + 3, y + 3, C_DRED)
            pyxel.line(x + 3, y - 3, x - 3, y + 3, C_DRED)
            return
        # tir (beam)
        if t.beam:
            bx, by, _ = t.beam
            bc = C_VIOLET if t.kind == "AI" else (C_RED if t.kind == "SCANNER" else C_CYAN)
            pyxel.line(x, y, bx, by, bc)
        # socle de puce
        pyxel.rect(x - 6, y - 6, 13, 13, C_SLATE)
        pyxel.rectb(x - 6, y - 6, 13, 13, C_LSLATE)
        for px in range(x - 4, x + 5, 3):
            pyxel.pset(px, y - 7, C_YELLOW)
            pyxel.pset(px, y + 7, C_YELLOW)
        core = C_WHITE if t.fire_anim > 0 else t.col

        if t.kind == "ANTIVIRUS":
            pyxel.rect(x - 3, y - 3, 7, 7, t.col)
            pyxel.rect(x - 1, y - 1, 3, 3, core)
        elif t.kind == "FIREWALL":
            for ry in range(-3, 4, 3):
                pyxel.rect(x - 4, y + ry, 9, 2, t.col)
            # halo de ralentissement (dither)
            pyxel.dither(0.25)
            pyxel.circb(x, y, t.range, C_ORANGE)
            pyxel.dither(1.0)
        elif t.kind == "SCANNER":
            pyxel.circ(x, y, 4, C_DRED)
            a = pyxel.frame_count * 0.25
            pyxel.line(x, y, x + math.cos(a) * 4, y + math.sin(a) * 4, core)
            pyxel.line(x, y, x - math.cos(a) * 4, y - math.sin(a) * 4, core)
        elif t.kind == "AI":
            pyxel.circ(x, y, 4, t.col)
            pyxel.circb(x, y, 4, C_WHITE)
            pyxel.pset(x, y, core)
        # barre de vie de la tour si abimee
        if t.hp < t.max_hp:
            ratio = max(0.0, t.hp / t.max_hp)
            pyxel.rect(x - 6, y - 10, 13, 2, C_DRED)
            pyxel.rect(x - 6, y - 10, int(13 * ratio), 2, C_GREEN)

    # ------------------------------------------------------------ virus
    def draw_viruses(self):
        for v in self.viruses:
            x, y = int(v.x), int(v.y)
            col = C_WHITE if v.hit_flash > 0 else v.col
            # furtif non revele : translucide
            stealth_hidden = v.stealth and v.reveal_timer <= 0
            if stealth_hidden:
                pyxel.dither(0.5)
            self._virus_glyph(v.kind, x, y, col, small=True)
            if stealth_hidden:
                pyxel.dither(1.0)
            # barre de vie
            if v.hp < v.max_hp:
                ratio = max(0.0, v.hp / v.max_hp)
                pyxel.rect(x - 4, y - 7, 8, 1, C_DRED)
                pyxel.rect(x - 4, y - 7, int(8 * ratio), 1, C_GREEN)

    def _virus_glyph(self, kind, x, y, col, small=False):
        """Dessine l'icone d'un virus (utilise sur la carte et dans le panneau)."""
        if kind == "VIRUS":
            pyxel.circ(x, y, 4, col)
            for a in range(0, 360, 45):
                r = math.radians(a)
                pyxel.line(x, y, x + math.cos(r) * 6, y + math.sin(r) * 6, col)
            pyxel.pset(x - 1, y - 1, C_BG)
            pyxel.pset(x + 1, y - 1, C_BG)
        elif kind == "WORM":
            for i, dx in enumerate((-4, 0, 4)):
                pyxel.circ(x + dx, y, 3 - (i == 0), col)
            pyxel.pset(x + 5, y - 1, C_BG)
        elif kind == "TROJAN":
            pyxel.tri(x, y - 5, x - 5, y + 4, x + 5, y + 4, col)
            pyxel.rect(x - 3, y + 4, 7, 2, col)
            pyxel.pset(x - 1, y, C_BG)
        elif kind == "RANSOMWARE":
            pyxel.rect(x - 4, y - 1, 9, 6, col)
            pyxel.rectb(x - 4, y - 1, 9, 6, C_WHITE)
            pyxel.circb(x, y - 3, 3, col)          # anse du cadenas
            pyxel.pset(x, y + 2, C_BG)
        elif kind == "BOT":
            pyxel.rect(x - 4, y - 3, 9, 8, col)
            pyxel.rectb(x - 4, y - 3, 9, 8, C_LSLATE)
            pyxel.pset(x - 2, y - 1, C_BG)
            pyxel.pset(x + 2, y - 1, C_BG)
            pyxel.line(x, y - 4, x, y - 6, col)    # antenne

    def draw_particles(self):
        for p in self.particles:
            pyxel.pset(int(p.x), int(p.y), p.col)
            if p.life > 10:
                pyxel.pset(int(p.x) + 1, int(p.y), C_WHITE)

    # -------------------------------------------------------------- CPU
    def draw_cpu(self):
        x, y, w, h = 204, 22, 44, 30
        pulse = (pyxel.frame_count // 8) % 2
        edge = C_GREEN if self.encryption > 50 else C_RED
        pyxel.rect(x, y, w, h, C_BOARD2)
        pyxel.rectb(x, y, w, h, edge)
        pyxel.rectb(x - 2, y - 2, w + 4, h + 4, C_DRED)
        # pins
        for px in range(x + 3, x + w - 1, 4):
            pyxel.pset(px, y - 3, C_YELLOW)
            pyxel.pset(px, y + h + 2, C_YELLOW)
        self._text_center(x + w // 2, y + 4, "CPU", C_WHITE)
        # petit cadenas central
        lc = C_GREEN if self.encryption >= 100 else (C_RED if pulse else C_DRED)
        cx, cy = x + w // 2, y + 18
        pyxel.rect(cx - 4, cy, 9, 6, lc)
        pyxel.circb(cx, cy - 2, 3, lc)
        # mini-jauge sous le CPU
        gx, gy, gw = x, y + h + 5, w
        pyxel.rect(gx, gy, gw, 3, C_DRED)
        pyxel.rect(gx, gy, int(gw * self.encryption / 100), 3, C_GREEN)

    # ----------------------------------------------------------- UI haut
    def draw_topbar(self):
        pyxel.rect(0, 0, WIDTH, TOPH, C_BOARD1)
        pyxel.line(0, TOPH, WIDTH, TOPH, C_TRACE)
        alive = len(self.viruses)
        pyxel.text(3, 2, "BITS %d   WAVE %d/%d" % (self.bits, self.wave, MAX_WAVE), C_CYAN)
        pyxel.text(3, 9, "ACTIFS %d   RESERVE %d/%d" % (alive, self.reserve, START_RESERVE), C_GREEN)
        # jauge de chiffrement
        bx, by, bw, bh = 150, 3, 102, 9
        pyxel.rectb(bx, by, bw, bh, C_LSLATE)
        fill = int((bw - 2) * self.encryption / 100)
        col = C_GREEN if self.encryption > 60 else (C_YELLOW if self.encryption > 30 else C_RED)
        pyxel.rect(bx + 1, by + 1, fill, bh - 2, col)
        self._text_center(bx + bw // 2, by + 2, "CHIFFREMENT %d%%" % int(self.encryption), C_WHITE)

    # --------------------------------------------------------- UI panneau
    def draw_panel(self):
        pyxel.rect(0, PANELY, WIDTH, HEIGHT - PANELY, C_BOARD1)
        pyxel.line(0, PANELY, WIDTH, PANELY, C_TRACE)
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # --- boutons d'envoi de virus
        for (k, x, y, w, h) in self.virus_btns:
            st = VIRUS_TYPES[k]
            affordable = self.bits >= st["cost"] and self.reserve > 0
            hover = x <= mx < x + w and y <= my < y + h
            pyxel.rect(x, y, w, h, C_BG if affordable else C_BOARD2)
            pyxel.rectb(x, y, w, h, C_WHITE if hover else st["col"])
            self._virus_glyph(k, x + w // 2, y + 10, st["col"] if affordable else C_TRACE)
            self._text_center(x + w // 2, y + 18, VIRUS_NAMES[k], C_LSLATE)
            cc = C_YELLOW if affordable else C_DRED
            self._text_center(x + w // 2, y + 24, str(st["cost"]), cc)

        # --- boutons d'amelioration
        labels = {"speed": "VIT", "hp": "VIE", "dmg": "DEG"}
        for key, (x, y, w, h) in self.upg_btns.items():
            lvl = self.upg_lvl[key]
            cost = 60 * (lvl + 1)
            maxed = lvl >= 5
            affordable = (not maxed) and self.bits >= cost
            hover = x <= mx < x + w and y <= my < y + h
            pyxel.rect(x, y, w, h, C_BG)
            pyxel.rectb(x, y, w, h, C_WHITE if hover else C_VIOLET)
            txt = "%s Lv%d" % (labels[key], lvl)
            pyxel.text(x + 2, y + 2, txt, C_CYAN if not maxed else C_GREEN)
            if maxed:
                pyxel.text(x + w - 12, y + 2, "MAX", C_GREEN)
            else:
                pyxel.text(x + w - 13, y + 2, str(cost), C_YELLOW if affordable else C_DRED)

        # --- pause / vitesse
        px, py, pw, ph = self.pause_btn
        pyxel.rect(px, py, pw, ph, C_BG)
        pyxel.rectb(px, py, pw, ph, C_GREEN)
        self._text_center(px + pw // 2, py + 3, "PLAY" if self.paused else "PAUSE", C_GREEN)
        for (mult, x, y, w, h) in self.speed_btns:
            on = (self.speed == mult)
            pyxel.rect(x, y, w, h, C_GREEN if on else C_BG)
            pyxel.rectb(x, y, w, h, C_GREEN)
            self._text_center(x + w // 2, y + 4, "x%d" % mult, C_BG if on else C_GREEN)

    # ------------------------------------------------------ overlay centre
    def draw_center_overlay(self, title, col, sub):
        pyxel.dither(0.5)
        pyxel.rect(0, 0, WIDTH, HEIGHT, C_BG)
        pyxel.dither(1.0)
        self._text_center(WIDTH // 2, HEIGHT // 2 - 12, title, col)
        if sub:
            self._text_center(WIDTH // 2, HEIGHT // 2, sub, C_WHITE)

    # --------------------------------------------------------------- util
    def _text_center(self, cx, y, s, col):
        pyxel.text(cx - len(s) * 2, y, s, col)


# =============================================================================
#  POINT D'ENTREE
# =============================================================================
if __name__ == "__main__":
    Game()