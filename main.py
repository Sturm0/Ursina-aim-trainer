from ursina import *
from random import uniform, randint
from ursina.prefabs.first_person_controller import FirstPersonController
from time import time as obtener_tiempo
import datetime
from os import system,name
import math

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
                escenario = int(each.split("=")[1])
                print(escenario)
                print(type(escenario))
                

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
inicio_tiempo = obtener_tiempo()
cadencia = 5
grados = 0
tiro_sonido = Audio("shot.mp3")

if escenario == 1:
    for each in range(0,5):
        esferas.append(Entity(model="sphere",scale=(.8,.8,.8),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)))
elif escenario == 2:
    esferas.append(Entity(model="sphere",scale=(1,1,1),color=color.red,collider="box",position=(0,4,9)))

Text.size = 0.025
Text.default_resolution = 1080 * Text.size

info = Text(text="Tiempo: "+str(datetime.timedelta(seconds=round(obtener_tiempo()-inicio_tiempo))))
info.x = -.86
info.y = .47
info.origin = (-.5,.5)
info.background = True
info.visible = True
def input(key):
    global contador_eliminaciones, contador_fallos, salir, pared1, escenario, cadencia

    if escenario == 1 and key == "left mouse down":
        Audio("shot.mp3")
        acerto = False

        if escenario == 1:
            for each in esferas:
                if each.hovered:
                    destroy(each)
                    esferas.remove(each) # ¿ si hago esto es necesario lo de arriba? fijarse
                    contador_eliminaciones += 1
                    acerto = True

        if not acerto:
            contador_fallos += 1
        # if pared1.hovered: #esta es la forma más "limpia" de hacerlo pero por alguna razón no parece estar funcionando bien
        #     contador_fallos += 1

    elif escenario == 2 and (held_keys['left mouse']): # 'left mouse down' <-- no esta funcionando
        if cadencia == 7:
            Audio("shot.mp3") # <-- buscar algo mejor para ronda de ametralladora
            acerto = False
            for each in esferas:
                if each.hovered:
                    contador_eliminaciones += 1
                    acerto = True
            if not acerto:
                contador_fallos += 1
            cadencia = 0
        else:
            cadencia += 1

    elif key == "escape":
        salir = True

    # held keys tiene un comportamiento diferente si es "u" o si es "left mouse down", parece que lo mismo ocurre con todas las teclas con respecto a "left mouse down", "left mouse" solo tampoco parece tener el mismo comportamiento que el resto de teclas
    # if held_keys['left mouse']:
    #     print("it works !",randint(0,255))
    #extrañamente el bloque de código anterior en un programa mínimo sí funciona bien puesto en input(), en el caso de este programa solo parece funcionar como se espera dentro de update()


arriba = True
def update():
    global esferas, poner_esfera, contador_eliminaciones, contador_fallos,inicio_tiempo, info, salir, escenario, arriba, grados
    
    if held_keys['left mouse']: #para más información sobre porque puse esto acá y no en input() directo referir a los comentarios de la línea ~100-108
       input('left mouse')


    if player.position[1] < -20:
        player.position = (0,10,-5)

    if escenario == 1:
        if len(esferas) < 5:
            esferas.append(Entity(model="sphere",scale=(.8,.8,.8),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)))
    elif escenario == 2:
        
        if arriba:
            esferas[0].z = math.sin(math.radians(grados))*10
            esferas[0].y = math.cos(math.radians(grados))*10
            grados += 50*time.dt
            if grados > 90:
                arriba = False
        else:                
            grados -= 50*time.dt

            if grados < 0:
                arriba = True
                
        esferas[0].z = math.sin(math.radians(grados))*10
        esferas[0].y = math.cos(math.radians(grados))*10


    if salir or (eleccion_usuario==2 and obtener_tiempo() - inicio_tiempo > 60):
        if name == "nt":
            system("cls")
        else:
            system("clear")
        if escenario == 2:
            print("Aciertos:",contador_eliminaciones)            
        else:
            print("Eliminaciones:",contador_eliminaciones)
        print("Fallos:",contador_fallos)
        exit()
    info.text ="Tiempo: "+str(datetime.timedelta(seconds=round(obtener_tiempo()-inicio_tiempo)))

app.run()