import pyxel

class App:

    def __init__(self):
        pyxel.init(256, 256, title="Nuit du Code")
        self.x = 0
        pyxel.load("theme.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        self.x = (self.x + 1) % pyxel.width

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(self.x, 0, 8, 8, 9)

App()