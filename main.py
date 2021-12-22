from ursina import *
from random import uniform
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint
from time import time
app = Ursina()
player = FirstPersonController(y=2,origin_y=5,position=(0,2,-3))

ground = Entity(model="plane",scale=(20,1,20),color=color.white,texture="white_cube",texture_scale=(20,20),collider="box")
#cube = Entity(model="cube",scale=(1,1,1),position=(0,0,0),color=color.white,collider="box")
pared1 = Entity(model="quad",scale=(20,10,1),position=(0,5,10),color=color.white,texture="white_cube",texture_scale=(20,16)) #,collider="box"
pared2 = duplicate(pared1, position=(-10,5,0),rotation_y = -90)
pared3 = duplicate(pared1, position=(10,5,0),rotation_y = 90)
pared4 = duplicate(pared1, position=(0,5,-10),rotation_y = 180)
esfera = Entity(model="sphere",scale=(1,1,1),color=color.red,collider="box",position=(0,2,9))

pared1.double_sided = True
#pared1.rotation_y = 90
esferas = []
esferas.append(esfera)
contador = 0

inicio_tiempo = time()
for each in range(0,5):
    esferas.append(Entity(model="sphere",scale=(1,1,1),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)))
def input(key):
    global contador
    if key == "left mouse down":
        Audio("shot.mp3")
        for each in esferas:
            if each.hovered:
                destroy(each)
                esferas.remove(each)
                contador += 1
def update():
    global acumuladores, x, z, esferas, poner_esfera, contador
    if player.position[1] < -20:
        player.position = (2,1,2)

    if len(esferas) < 5:
        esferas.append(Entity(model="sphere",scale=(1,1,1),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)))
    if time() - inicio_tiempo > 60:
        print(contador)
        exit()


app.run()