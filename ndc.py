import pyxel

top_left  = (0,32)
top_right = (pyxel.width, 32)
tm = 0 #Tilemap( 0 - 7 )
Image=0
spawnpoint = (8,32)

#class TowerType(enumerate):
firewall = 1
ruler = 2
packet_filter = 3
phising = 11
DOS =12
trojan= 13

monster_list={#[Name, damage, sprite(posx,posy,sizex,sizey)]
    firewall:["Firewall",2,(0,16,16,16)],
    ruler:["Rules",1,(32,0,16,16)],
    phising:["Phising",1,(0,0,16,16)],
    DOS:["DoS",4,(48,0,16,16)],
    trojan:["Trojan",2,(0,48,16,16)]
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
        self.update_Towers()
        self.update_Monsters()
        self.attacker.money+=0.04
    
    def update_Monsters(self):
        for Monster in self.attacker.monsters:
            if Monster.hp<0 :
                self.attacker.monsters.remove(Monster)
            else :
                Monster.update(self.attacker,self.defenser)

    def update_Towers(self):
        for towr in self.defenser.towers:
            towr.update(self.attacker.monsters)
        #Spawning towers!
        self.defenser.tick+=1
        if self.defenser.tick == 300:
            v2,v1,v3 =monster_list[firewall]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[7]))
        if self.defenser.tick == 600:
            v2,v1,v3 =monster_list[firewall]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[5]))
        if self.defenser.tick == 900:
            v2,v1,v3 =monster_list[ruler]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[3],16))
        if self.defenser.tick == 1200:
            v2,v1,v3 =monster_list[firewall]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[8]))
        if self.defenser.tick == 1500:
            v2,v1,v3 =monster_list[ruler]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[9],16))
        if self.defenser.tick == 1800:
            v2,v1,v3 =monster_list[firewall]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[2]))
        if self.defenser.tick == 2100:
            v2,v1,v3 =monster_list[firewall]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[4]))
        if self.defenser.tick == 2400:
            v2,v1,v3 =monster_list[firewall]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[1]))
        if self.defenser.tick == 2700:
            v2,v1,v3 =monster_list[ruler]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[0],16))
        if self.defenser.tick == 3000:
            v2,v1,v3 =monster_list[ruler]
            self.defenser.towers.append(tower(v1,v2,v3,self.defenser.possible_pos[6],16))
        

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
            pyxel.text(8,24,"Trojan (8)",2)
        else :
            pyxel.text(8,24,"Trojan (8)",1)
        if self.buying[0]!=-1 :
            self.buying[1]-=1
        if self.buying[1]==0:
            self.buying[0]=-1

        pyxel.cursor.camera(-8,-8)
        
        #Buy buttons:
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if pyxel.mouse_y < 32 and pyxel.mouse_y > 24 and pyxel.mouse_x < 64:
                if self.attacker.money > 8:
                    self.attacker.money-=8
                    self.buying=[3,120]
                    v2, v1, v3 = monster_list[trojan]
                    self.attacker.monsters.append(monster(v1,v2,v3,1250,spawnpoint))
            if pyxel.mouse_y < 24 and pyxel.mouse_y > 16 and pyxel.mouse_x < 64:
                if self.attacker.money > 10:
                    self.attacker.money-=10
                    self.buying=[2,120]
                    v2, v1, v3 = monster_list[DOS]
                    self.attacker.monsters.append(monster(v1,v2,v3,500,spawnpoint))
            if pyxel.mouse_y < 16 and pyxel.mouse_y > 8 and pyxel.mouse_x < 64:
                if self.attacker.money > 5:
                    self.attacker.money-=5
                    self.buying=[1,120]
                    v2, v1, v3 = monster_list[phising]
                    self.attacker.monsters.append(monster(v1,v2,v3,750,spawnpoint))
        
        pyxel.text(66,4,self.defenser.__str__(),3)
        pyxel.text(66,14,self.attacker.__str__(),3)
        pyxel.text(64,24,f"X:{pyxel.mouse_x},Y:{pyxel.mouse_y}",3)

        self.draw_tower()
        self.draw_monster()

    def draw_monster(self):
        for Monster in self.attacker.monsters:
            Monster.draw()

    def draw_tower(self):
        for tower in self.defenser.towers:
            tower.draw()




class Defense:
    def __init__(self):
        self.hp=16
        self.limit=10
        self.tick=0
        self.possible_pos=[(24,64+32),(88,160+32),(136,72+32),(15*8,20*8+32),(24*8,80+32),(32,24+32),(64,64+32),(80,128+32),(28*8,6*8+32),(19*8,17*8+32)]
        self.towers=list()

    def take_damage(self,dmg):
        self.hp-=dmg
        self.hp-=1
    
    def __str__(self):
        return f"Enemy Health Point : {self.hp}"

class tower:
    def __init__(self,d,n,s,pos,dist=32):
        self.damage=d
        self.name=n
        self.sprite=s
        self.mdist=dist
        self.posx=pos[0]
        self.posy=pos[1]

    def update(self,monsters,*args):
        for monst in monsters:
            if self.dist(monst)< self.mdist:
                monst.hp-=self.damage

    def draw(self,*args):
        pyxel.blt(self.posx,self.posy,Image,self.sprite[0],self.sprite[1],self.sprite[2],self.sprite[3],0)
    
    def dist(self,m):
        return ((self.posx-m.posx)**2+(self.posy-m.posy)**2)**0.5

        
class Attack:
    def __init__(self):
        self.money=10
        self.monsters=list()

    def pay(self,dmg):
        self.hp-=dmg
    
    def __str__(self):
        return f"Money : {round(self.money,2)}"

class monster:
    def __init__(self,d,n,s,hp,pos):
        self.damage=d
        self.hp =50
        self.name=n
        self.sprite=s
        self.posx=pos[0]
        self.posy=pos[1]
        self.turn=0
    
    def update(self,attack,defense,*args):
        match self.turn:
            case 0:
                self.posy+=1
                if self.posy==112:
                    self.turn+=1
            case 2:
                self.posy+=1
                if self.posy==208:
                    self.turn+=1
            case 1:
                self.posx+=1
                if self.posx==64:
                    self.turn+=1
            case 3:
                self.posx+=1
                if self.posx==136:
                    self.turn+=1
            case 5:
                self.posx+=1
                if self.posx==208:
                    self.turn+=1
            case 4:
                self.posy-=1
                if self.posy==128:
                    self.turn+=1
            case 6:
                self.posy-=1
                if self.posy==50:
                    defense.take_damage(self.damage)
                    attack.monsters.remove(self)


        
    def draw(self,*args):
        pyxel.blt(self.posx,self.posy,Image,self.sprite[0],self.sprite[1],self.sprite[2],self.sprite[3],0)
        

App()