# Nuit du Code - Cyber Defense
# On est le virus : on doit envoyer des virus jusqu'au CPU pour le chiffrer a 100%
# L'ordi se defend avec des tours qui tirent sur les virus.

import pyxel

# le chemin que j'ai dessine (liste de points x, y)
# (si un virage n'est pas bon, change juste les nombres ici)
chemin = [
    (19, 40), (19, 111), (81, 111), (81, 50), (155, 50),
    (155, 91), (171, 91), (171, 127), (98, 127), (98, 149),
    (60, 149), (60, 162), (42, 162), (42, 190), (90, 190),
    (90, 215), (116, 215), (116, 176), (156, 176), (200, 176),
    (200, 120), (230, 120),
]

# les endroits ou l'ordi pose ses tours (x, y)
emplacements_tours = [(45, 95), (118, 66), (135, 110), (66, 175), (180, 150)]


class Virus:
    def __init__(self, pv, vitesse, degats, chiffrement, couleur):
        self.x = chemin[0][0]
        self.y = chemin[0][1]
        self.pv = pv
        self.pv_max = pv
        self.vitesse = vitesse
        self.degats = degats            # degats que le virus fait aux tours
        self.chiffrement = chiffrement  # combien de % il ajoute s'il atteint le CPU
        self.couleur = couleur
        self.cible = 1                  # le prochain point du chemin
        self.arrive = False
        self.mort = False

    def bouge(self):
        # si on a depasse le dernier point, c'est qu'on est arrive au CPU
        if self.cible >= len(chemin):
            self.arrive = True
            return
        bx, by = chemin[self.cible]
        dx = bx - self.x
        dy = by - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < self.vitesse:
            # on est presque sur le point, on passe au suivant
            self.x = bx
            self.y = by
            self.cible += 1
        else:
            # on avance vers le point
            self.x += dx / dist * self.vitesse
            self.y += dy / dist * self.vitesse


class Tour:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.portee = 28
        self.degats = 3
        self.recharge = 0
        self.tir = None     # position du virus vise (pour dessiner le tir)

    def tire(self, virus_list):
        # on attend si la tour vient de tirer
        if self.recharge > 0:
            self.recharge -= 1
            self.tir = None
            return
        # on cherche un virus a portee
        for v in virus_list:
            if v.mort:
                continue
            d = ((v.x - self.x) ** 2 + (v.y - self.y) ** 2) ** 0.5
            if d <= self.portee:
                v.pv -= self.degats
                self.recharge = 24
                self.tir = (v.x, v.y)
                if v.pv <= 0:
                    v.mort = True
                return
        self.tir = None


class App:
    def __init__(self):
        pyxel.init(256, 256, title="Nuit du Code")
        pyxel.mouse(True)
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.argent = 150
        self.reserve = 30
        self.chiffrement = 0
        self.vague = 1
        self.minuteur = 0
        self.temps = 0
        self.virus_list = []
        self.tours = []
        for (x, y) in emplacements_tours:
            self.tours.append(Tour(x, y))
        self.fini = ""   # "", "gagne" ou "perdu"

    def envoie_virus(self, type_virus):
        # 1 = virus simple, 2 = ver (rapide), 3 = cheval de Troie (costaud)
        if type_virus == 1:
            cout = 20
            v = Virus(12, 0.6, 2, 3, 8)     # rouge
        elif type_virus == 2:
            cout = 30
            v = Virus(10, 1.3, 1, 3, 11)    # vert, rapide
        else:
            cout = 50
            v = Virus(40, 0.5, 3, 8, 14)    # rose, beaucoup de vie

        if self.argent >= cout and self.reserve > 0:
            self.argent -= cout
            self.reserve -= 1
            self.virus_list.append(v)

    def update(self):
        # ecran de fin : on attend R pour recommencer
        if self.fini != "":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return

        # touches pour envoyer des virus
        if pyxel.btnp(pyxel.KEY_1):
            self.envoie_virus(1)
        if pyxel.btnp(pyxel.KEY_2):
            self.envoie_virus(2)
        if pyxel.btnp(pyxel.KEY_3):
            self.envoie_virus(3)

        # l'argent (bits) remonte doucement
        self.minuteur += 1
        if self.minuteur >= 30:
            self.minuteur = 0
            self.argent += 2

        # les vagues : l'ordi renforce ses tours avec le temps
        self.temps += 1
        if self.temps >= 600 and self.vague < 20:
            self.temps = 0
            self.vague += 1
            for t in self.tours:
                t.degats += 1

        # les tours tirent
        for t in self.tours:
            t.tire(self.virus_list)

        # les virus bougent
        for v in self.virus_list:
            v.bouge()
            if v.arrive:
                self.chiffrement += v.chiffrement
                v.mort = True
                self.argent += 5
                if self.chiffrement >= 100:
                    self.chiffrement = 100
                    self.fini = "gagne"

        # on enleve les virus morts de la liste
        vivants = []
        for v in self.virus_list:
            if not v.mort:
                vivants.append(v)
        self.virus_list = vivants

        # defaite : plus de reserve et plus aucun virus en vie
        if self.reserve <= 0 and len(self.virus_list) == 0 and self.chiffrement < 100:
            self.fini = "perdu"

    def draw(self):
        pyxel.cls(0)

        # le chemin (mon dessin)
        for i in range(len(chemin) - 1):
            x1, y1 = chemin[i]
            x2, y2 = chemin[i + 1]
            pyxel.line(x1, y1, x2, y2, 12)

        # le depart et le CPU
        dx, dy = chemin[0]
        pyxel.text(dx - 4, dy - 9, "IN", 8)
        cx, cy = chemin[-1]
        pyxel.rectb(cx - 6, cy - 6, 14, 14, 8)
        pyxel.text(cx - 5, cy - 2, "CPU", 7)

        # les tours
        for t in self.tours:
            if t.tir is not None:
                pyxel.line(t.x, t.y, t.tir[0], t.tir[1], 10)
            pyxel.circ(t.x, t.y, 3, 9)
            pyxel.circb(t.x, t.y, 3, 7)

        # les virus
        for v in self.virus_list:
            pyxel.circ(v.x, v.y, 3, v.couleur)
            # petite barre de vie
            if v.pv < v.pv_max:
                pyxel.rect(v.x - 3, v.y - 6, 6, 1, 8)
                pyxel.rect(v.x - 3, v.y - 6, int(6 * v.pv / v.pv_max), 1, 11)

        # le texte (interface)
        pyxel.text(3, 3, "BITS " + str(self.argent), 10)
        pyxel.text(3, 11, "RESERVE " + str(self.reserve), 11)
        pyxel.text(3, 19, "VAGUE " + str(self.vague) + "/20", 6)
        pyxel.text(120, 3, "CHIFFREMENT " + str(int(self.chiffrement)) + "%", 12)
        pyxel.text(3, 246, "1:Virus(20)  2:Ver(30)  3:Cheval(50)", 6)

        # ecrans de fin
        if self.fini == "gagne":
            pyxel.text(80, 120, "GAGNE !  R pour rejouer", 11)
        if self.fini == "perdu":
            pyxel.text(80, 120, "PERDU !  R pour rejouer", 8)


App()