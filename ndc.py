import pyxel

top_left  = (0,32)
top_right = (pyxel.width, 32)
tm = 0 #Tilemap( 0 - 7 )

#class TowerType(enumerate):
firewall = 1
ruler = 2
packet_filter = 3
phising = 11
DOS =12
voicephising = 13

monster_list={#[Name, damage, sprite(posx,posy,sizex,sizey)]
    firewall:["Firewall",2,(0,0,16,16)],
    ruler:["Rules",1,(0,0,16,16)],
    phising:["Phising",1,(0,0,16,16)],
    DOS:["DoS",4,(0,0,16,16)],
    voicephising:["Voice-Phising",2,(0,0,16,16)]
}

class App:

    def __init__(self):
        pyxel.init(256, 256, title="Nuit du Code")
        self.buying=[-1,0] # buy nb, time_left
        pyxel.load("theme.pyxres")
        pyxel.sounds[0].pcm("assets/audio_bgm1.ogg")
        pyxel.mouse(True)
        self.attacker = Attack()
        self.defenser = Defense()

        pyxel.run(self.update, self.draw)

    def update(self):
        pyxel.play(0,0, loop=True)

    def draw(self):
        pyxel.cls(0)
        pyxel.line(0,31,256,31,13)
        pyxel.line(63,0,63,31,13)
        pyxel.bltm(0,32,tm,0,0,pyxel.width,pyxel.height-32)
        pyxel.text(8,0,"Buy enemies :",1)
        if self.buying[0]==1:
            pyxel.text(8,8,"phishing (5)",2)
        else :
            pyxel.text(8,8,"phishing (5)",1)
        if self.buying[0]==2:
            pyxel.text(8,16,"DOS (10)",2)
        else :
            pyxel.text(8,16,"DOS (10)",1)
        if self.buying[0]==3:
            pyxel.text(8,24,"voice-fish(8)",2)
        else :
            pyxel.text(8,24,"voice-fish(8)",1)
        if self.buying[0]!=-1 :
            self.buying[1]-=1
        if self.buying[1]==0:
            self.buying[0]=-1

        pyxel.cursor.camera(-8,-8)
        
        #Buy buttons:
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if pyxel.mouse_y < 32 and pyxel.mouse_y > 24 and pyxel.mouse_x < 64:
                self.buying=[3,120]
            if pyxel.mouse_y < 24 and pyxel.mouse_y > 16 and pyxel.mouse_x < 64:
                self.buying=[2,120]
            if pyxel.mouse_y < 16 and pyxel.mouse_y > 8 and pyxel.mouse_x < 64:
                self.buying=[1,120]
        
        pyxel.text(66,4,self.defenser.__str__(),3)
        pyxel.text(66,14,self.attacker.__str__(),3)
        pyxel.text(64,24,f"X:{pyxel.mouse_x},Y:{pyxel.mouse_y}",3)



class Defense:
    def __init__(self):
        self.hp=16
        self.towers=list()

    def take_damage(self,dmg):
        self.hp-=dmg
    
    def __str__(self):
        return f"Enemy Health Point : {self.hp}"

class tower:
    def __init__(self,d,n,s,pos):
        self.damage=d
        self.name=n
        self.sprite=s
        self.posx=pos[0]
        self.posy=pos[1]

        
class Attack:
    def __init__(self):
        self.money=10
        self.monsters=list()

    def pay(self,dmg):
        self.hp-=dmg
    
    def __str__(self):
        return f"Money : {self.money}"

class monster:
    def __init__(self,d,n,s,pos):
        damage=d
        name=n
        sprite=s
        posx=pos[0]
        posy=pos[1]
        
        

App()