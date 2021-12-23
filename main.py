from ursina import *
from random import uniform
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint
from time import time
import datetime
from os import system,name
#app = Ursina(fullscreen=True)
print("Ingrese 1 o 2 respectivamente para elegir un modo")
print("(1) Free")
print("(2) Challenge")
eleccion_usuario = int(input())
salir = False

with open("Configuraciones.txt",'r') as archivo:
    for each in archivo:
        if each[0] != "#":
            if each.split("=")[0] == "Pantalla_completa":
                if eval(each.split("=")[1]):
                    app = Ursina(fullscreen=True)
                else:
                    app = Ursina()    
            else:
                escenario = each.split("=")[1]
                

player = FirstPersonController(position=(0,10,-5)) # por alguna razón si pongo un Y inicial más lógico el jugador se empieza a caer del mundo (ni idea)
player.cursor.color = color.black
player.speed = 0
ground = Entity(model="plane",scale=(20,1,20),color=color.white,texture="white_cube",texture_scale=(20,20),collider="box")
pared1 = Entity(model="quad",scale=(20,10,1),position=(0,5,10),color=color.white,texture="white_cube",texture_scale=(20,16))
pared2 = duplicate(pared1, position=(-10,5,0),rotation_y = -90)
pared3 = duplicate(pared1, position=(10,5,0),rotation_y = 90)
pared4 = duplicate(pared1, position=(0,5,-10),rotation_y = 180)

pared1.double_sided = True
esferas = []
contador_eliminaciones = 0
contador_fallos = 0
inicio_tiempo = time()

for each in range(0,5):
    esferas.append(Entity(model="sphere",scale=(.8,.8,.8),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)))

Text.size = 0.025
Text.default_resolution = 1080 * Text.size

info = Text(text="Tiempo: "+str(datetime.timedelta(seconds=round(time()-inicio_tiempo))))
info.x = -.86
info.y = .47
info.origin = (-.5,.5)
info.background = True
info.visible = True
def input(key):
    global contador_eliminaciones, contador_fallos, salir, pared1
    if key == "left mouse down":
        Audio("shot.mp3")
        acerto = False
        for each in esferas:
            if each.hovered:
                destroy(each)
                esferas.remove(each)
                contador_eliminaciones += 1
                acerto = True
        if not acerto:
            contador_fallos += 1
            print(contador_fallos)
        # if pared1.hovered: #esta es la forma más "limpia" de hacerlo pero por alguna razón no parece estar funcionando bien
        #     contador_fallos += 1
                
    elif key == "escape":
        salir = True
    
def update():
    global esferas, poner_esfera, contador_eliminaciones, contador_fallos,inicio_tiempo, info, salir
    if player.position[1] < -20:
        player.position = (0,10,-5)

    if len(esferas) < 5:
        esferas.append(Entity(model="sphere",scale=(.8,.8,.8),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)))
    if salir or (eleccion_usuario==2 and time() - inicio_tiempo > 60):
        if name == "nt":
            system("cls")
        else:
            system("clear")
        print("Eliminaciones:",contador_eliminaciones)
        print("Fallos:",contador_fallos)
        exit()
    info.text ="Tiempo: "+str(datetime.timedelta(seconds=round(time()-inicio_tiempo)))

app.run()