from ursina import *
from random import uniform, randint, choice
from ursina.prefabs.first_person_controller import FirstPersonController
from time import time as obtener_tiempo
import datetime
from os import system,name
import math
import sqlite3


print('Lista de escenarios:')
print('1 equivalente a "1wall6targets TE"')
print('2 equivalente a "Vertical Long Strafes"')
print('3 equivalente a "Close Long Strafes"')
print('4 equivalente a "FuglaaXYLongStrafe"')
print('5 equivalente a "Tile Frenzy - Strafing - 01"')
print('6 equivalente a "LG Pin Practice 360"')

escenario = int(input("Ingrese el número del escenario: "))

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
                sensibilidad = eval(each.split("=")[1])
                
player = FirstPersonController(position=(0,10,-5)) # por alguna razón si pongo un Y inicial más lógico el jugador se empieza a caer del mundo (ni idea)
player.mouse_sensitivity = Vec2(sensibilidad[0], sensibilidad[1])
player.cursor.color = color.black
player.speed = 0
cubo_referencia = Entity(parent=player.camera_pivot,model="cube",scale=(.001,.001,.001),color=color.red,position=(0,0,2))

#hacer lista de paredes después
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
cadencia = 2
grados = 0
tiro_sonido = Audio("shot.mp3")
cambiar_direccion = 2


if escenario == 1:
    for each in range(0,6):
        esferas.append(Entity(model="sphere",scale=(.8,.8,.8),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)))
elif escenario == 2:
    esferas.append(Entity(model="sphere",scale=(1,1,1),color=color.red,collider="box",position=(0,4,9)))
elif escenario == 3:
    esferas.append(Entity(model=Cylinder(20, start=0,height=4,radius=.75), color=color.red,position=(0,0,9),collider="box")) #sí, ya se que no es una esfera; pero así es más fácil
    player.position = (0,5,0)
elif escenario == 4:
    esferas.append(Entity(model="sphere",scale=(1,1,1),color=color.red,collider="box",position=(0,2,9))) #position=(9,9,9)
    player.gravity = 0
    player.positon = (0,5,0)

    for each in (pared1,pared2,pared3,pared4):
        each.scale = (20,20,1)
        each.y = 10
elif escenario == 5:
    for each in range(0,5):
        esferas.append([Entity(model="cube",scale=(1.5,1.5,1.5),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)),choice((True,False))]) #el choice acá determina si va a ir para la derecha o para la izquierda
elif escenario == 6:
    val_scal = (pared1.scale_x*2,pared1.scale_y*2,pared1.scale_z)

    for each in (pared1,pared2,pared3,pared4):
        each.scale = (val_scal[0],val_scal[1],val_scal[2])
        each.texture_scale = (val_scal[0],val_scal[1]) #revisar como afecta el tamaño de las texturas al rendimiento

    ground.scale = (ground.scale[0]*2,ground.scale[1],ground.scale[2]*2)
    #print("ESTO:",ground.scale)
    ground.texture_scale = (ground.scale[0],ground.scale[2])

    pared1.z *= 2
    pared2.x *= 2
    pared3.x *= 2
    pared4.z *= 2

    player.position = (0,1,0)
    player.gravity = 0

    for each in (pared1,pared2,pared3,pared4):
        each.color = color.rgba(255,255,255,255)
    class Cilindro(Entity):
        def __init__(self):
            super().__init__(self, model=Cylinder(20, start=0,height=4,radius=.75), color=color.red,position=(randint(-20,20),randint(1,5),randint(-20,20)),collider="box")
            
            self.collider = BoxCollider(self,center=(0,2,0),size=(1.5,4,1.5))
            #self.collider.visible = True #<-- aparentemente el colisionador de tipo caja no funciona del todo bien en cilindros
            self.saltar = True
            self.vidas = 20
            self.x_direccion = 1
            self.z_direccion = 1
            self.esta_siendo_golpeado = False
        def __dir_sent(self,cilindro,signoX,signoZ):
            #esta función es utilizada para el movimiento de los cilindros en el escenario 6
            global ground
            if .75-ground.scale_x/2 < cilindro.x < -.75+ground.scale_x/2 and .75-ground.scale_z/2 < cilindro.z < -.75+ground.scale_z/2:
            
                cilindro.x = cilindro.x + signoX*.5
                cilindro.z = cilindro.z + signoZ*.5
                cilindro.x_direccion = signoX*1
                cilindro.z_direccion = signoZ*1

        def movimiento(self,pared1):
            
            if self.saltar:

                self.y += time.dt*5
                if not self.esta_siendo_golpeado: #quizá es buena idea solo desactivar el movimiento vertical acá cuando esta siendo golpeado

                    self.x = self.x + self.x_direccion * time.dt * 5
                    self.z = self.z + self.z_direccion * time.dt * 5
            else:
                self.y -= time.dt*5
                if not self.esta_siendo_golpeado: #quizá es buena idea solo desactivar el movimiento vertical acá cuando esta siendo golpeado
                    self.x = self.x + self.x_direccion * time.dt * 5
                    self.z = self.z + self.z_direccion * time.dt * 5

            if self.y <= 0:
                self.x_direccion = choice((1,-1))
                self.z_direccion = choice((1,-1))
                self.saltar = True
                
            if self.x >= 20:
                self.x_direccion = -1
                
            if self.x <= -20:
                self.x_direccion = 1
                
            if self.z >= 20:
                self.z_direccion = -1
            if self.z <= -20:
                
                self.z_direccion = 1

            if self.y > pared1.scale_y:
                self.saltar = False

        def movimiento_rayo(self,rayo):
            #esta función maneja el movimiento cuando el cilindro es chocado por un rayo
            if rayo.normal[0] > 0 and self.z > 0:
                self.__dir_sent(self,-1,1)
            elif rayo.normal[0] < 0 and self.z > 0:
                self.__dir_sent(self,1,1)

            elif rayo.normal[0] > 0 and self.z < 0:
                self.__dir_sent(self,-1,-1)
            elif rayo.normal[0] < 0 and self.z < 0:
                self.__dir_sent(self,1,-1)
            else:
                if self.x > 0 and self.z > 0:
                    self.__dir_sent(self,1,1)
                elif self < 0 and self.z > 0:
                    self.__dir_sent(self,-1,1)
                elif self.x < 0 and self.z < 0:
                    self.__dir_sent(self,-1,-1)
                elif self.x > 0 and self.z < 0:
                    self.__dir_sent(self,1,-1)
            
                

    for index,each in enumerate(range(0,5),0):
        #esferas.append(Entity(model=Cylinder(20, start=0,height=4,radius=.75), color=color.red,position=(randint(-20,20),1,randint(-20,20)),collider="box"))
        esferas.append(Cilindro())
        esferas[index].saltar = choice((True, False))
        
#esferas.append(Entity(model="sphere",scale=(1,1,1),color=color.red,collider="box",position=(10,1,0)))

z_sig = 1 #solo es usado cuando el escenario es el 3
x_sig = 1 #solo es usado cuando el escenario es el 3
y_sig = -1 #solo es usado cuando el escenario es el 4
#izquierda = False #solo es usado en el escenario 5

Text.size = 0.025
Text.default_resolution = 1080 * Text.size



#sección para texto de tiempo
info = Text(text="Tiempo: "+str(datetime.timedelta(seconds=round(obtener_tiempo()-inicio_tiempo))))
info.x = -.86
info.y = .47
info.origin = (-.5,.5)
info.background = True
info.visible = True

def input(key):
    global contador_eliminaciones, contador_fallos, salir, pared1, escenario, cadencia, tiro_sonido, cubo_referencia, esferas
    if escenario in (1,5) and key == "left mouse down":
        
        tiro_sonido.play()
        acerto = False

        if escenario == 1:
            for each in esferas:
                if each.hovered:
                    destroy(each)
                    esferas.remove(each)
                    contador_eliminaciones += 1
                    acerto = True
        elif escenario == 5:
            for each in esferas:
                if each[0].hovered:
                    destroy(each[0])
                    esferas.remove(each)
                    contador_eliminaciones += 1
                    acerto = True
                    esferas.append([Entity(model="cube",scale=(1.5,1.5,1.5),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)),choice((True,False))])

        if not acerto:
            contador_fallos += 1

    elif (escenario in (2,3,4)) and (held_keys['left mouse']): # 'left mouse down' <-- no esta funcionando
        if cadencia == 7:
            tiro_sonido.play() # <-- buscar algo mejor para ronda de ametralladora
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
    elif escenario == 6:

        if cadencia == 2: #cadencia == 7
            origin = cubo_referencia.world_position
            rayo = raycast(origin, direction=cubo_referencia.forward, distance=50, debug=True)
            
            
            if rayo.normal != None:
                
                for each in esferas:
                    #esto debería estar dentro de la clase cilindro, ya que refiere a su movimiento
                    if each.hovered: # <-- debería haber otra forma mejor de hacerlo pero por ahora creo que va a servir
                        each.esta_siendo_golpeado = True
                        each.movimiento_rayo(rayo)

                        each.vidas -= 1
                        if each.vidas <= 0:
                            destroy(each)
                            esferas.remove(each)
                            esferas.append(Cilindro())
                            esferas[len(esferas)-1].saltar = choice((True, False))
                    else:
                        each.esta_siendo_golpeado = False
            cadencia = 0
        else:
            cadencia += 1
                    

    if key == "escape":
        salir = True

    # held keys tiene un comportamiento diferente si es "u" o si es "left mouse down", parece que lo mismo ocurre con todas las teclas con respecto a "left mouse down", "left mouse" solo tampoco parece tener el mismo comportamiento que el resto de teclas
    # if held_keys['left mouse']:
    #     print("it works !",randint(0,255))
    #extrañamente el bloque de código anterior en un programa mínimo sí funciona bien puesto en input(), en el caso de este programa solo parece funcionar como se espera dentro de update()


arriba = True
def update():
    global esferas, poner_esfera, contador_eliminaciones, contador_fallos,inicio_tiempo, info, salir, escenario, arriba, grados, cambiar_direccion,x_sig,z_sig, pared1
    
    if held_keys['left mouse']: #para más información sobre porque puse esto acá y no en input() directo referir a los comentarios de la línea ~100-108
       input('left mouse')

    if player.position[1] < -20:
        player.position = (0,10,-5)

    if escenario == 1:
        if len(esferas) < 6:
            esferas.append(Entity(model="sphere",scale=(.8,.8,.8),color=color.red,collider="box",position=(randint(-9,9),randint(1,9),9)))
    elif escenario == 2:
        
        if arriba:
            esferas[0].z = math.sin(math.radians(grados))*10
            esferas[0].y = math.cos(math.radians(grados))*10
            grados += 50*time.dt
            if round(obtener_tiempo()-inicio_tiempo) == cambiar_direccion:
                cambiar_direccion += 1
                if randint(0,1) == 1:
                    arriba = False
            if grados > 90:
                arriba = False
        else:                
            grados -= 50*time.dt

            if round(obtener_tiempo()-inicio_tiempo) == cambiar_direccion:
                cambiar_direccion += 1
                if randint(0,1) == 1:
                    arriba = True
            if grados < 0:
                arriba = True
                
        esferas[0].z = math.sin(math.radians(grados))*10
        esferas[0].y = math.cos(math.radians(grados))*10

    elif escenario == 3:

        esferas[0].z += 5*time.dt*z_sig
        esferas[0].x += 5*time.dt*x_sig
        #print("z: ",esferas[0].z,"x: ",esferas[0].x)

        if round(obtener_tiempo()-inicio_tiempo) == cambiar_direccion:
                cambiar_direccion += 1
                z_sig = choice((-1,1))
                x_sig = choice((-1,1))

        if esferas[0].z >= 10 or (esferas[0].z >= -3 and esferas[0].z <= 0 and esferas[0].x >= -3 and esferas[0].x <= 3):
            z_sig = -1
        elif esferas[0].z <= -10 or (esferas[0].z >= 0 and esferas[0].z <= 3 and esferas[0].x >= -3 and esferas[0].x <= 3):
            z_sig = 1

        if esferas[0].x > 10:
            x_sig = -1
        elif esferas[0].x < -10:
            x_sig = 1
    elif escenario == 4:
        esferas[0].y += 5*time.dt*z_sig
        esferas[0].x += 5*time.dt*x_sig
        if round(obtener_tiempo()-inicio_tiempo) == cambiar_direccion:
            cambiar_direccion += 1
            y_sig = choice((-1,1))
            x_sig = choice((-1,1))

        if esferas[0].x > 10:
            x_sig = -1
        elif esferas[0].x < -10:
            x_sig = 1

        if esferas[0].y >= 20:
            z_sig = -1
        elif esferas[0].y <= 1:
            z_sig = 1

    elif escenario == 5:
        for each in esferas:
            if each[1]:
                each[0].x += 5*time.dt
            else:
                each[0].x -= 5*time.dt

            if each[0].x >= 10:
                each[1] = False
            elif each[0].x <= 0:
                each[1] = True

    elif escenario == 6:
        for each in esferas:
            each.movimiento(pared1)
                
    if salir or (eleccion_usuario==2 and obtener_tiempo() - inicio_tiempo > 60):

        def camb_respct(cur,contador_el_fa,Aciertos_Fallos,eleccion_usuario):
            #esta función da el cambio respecto a otro número con un formateando de forma legible
            cur.execute('SELECT AVG(%s) FROM Rondas WHERE "Escenario ID" == %s AND "Modo" == %s;'%(Aciertos_Fallos,escenario,eleccion_usuario)) # por alguna razón la sintaxis ('?',(val1)) no parece estar funcionando correctamente así que use %s en cambio
            #cur.execute('SELECT AVG(?) FROM Rondas WHERE "Escenario ID" == ?;',(Aciertos_Fallos,escenario)) esto devuelve siempre 0.0
            promedio_fa = cur.fetchone()[0]+1*10**(-10)
            texto_camb_respct_prom_fa = f"{(contador_el_fa*100)/promedio_fa-100 :.2f}" #texto para cambio respecto a promedio acierto o fallo

            if float(texto_camb_respct_prom_fa) > 0:
                texto_camb_respct_prom_fa = "+"+texto_camb_respct_prom_fa

            return promedio_fa,texto_camb_respct_prom_fa

        # if name == "nt":
        #     system("cls")
        # else:
        #     system("clear")


        db = sqlite3.connect("rondas_historial.sqlite")
        cur = db.cursor()

        cur.execute('INSERT INTO rondas("Nombre jugador","Escenario ID","Modo","Aciertos","Fallos") VALUES (?,?,?,?,?);',("Jugador1",escenario,eleccion_usuario,contador_eliminaciones,contador_fallos))
        db.commit()

        if escenario in (2,3,4):
            print("Aciertos:",contador_eliminaciones)
        else:
            print("Eliminaciones:",contador_eliminaciones)
        print("Fallos:",contador_fallos)


        promedio_aciertos,texto_camb_respct_prom_acier = camb_respct(cur,contador_eliminaciones,"Aciertos",eleccion_usuario) #texto para cambio respecto a promedio acierto
        print("Cambio respecto al promedio (aciertos): ",texto_camb_respct_prom_acier,"%")

        promedio_fallos,texto_camb_respct_prom_fallos = camb_respct(cur,contador_fallos,"Fallos",eleccion_usuario) #texto para cambio respecto a promedio fallos
        print("Cambio respecto al promedio (fallos): ",texto_camb_respct_prom_fallos,"%")

        print("Promedio aciertos: ",f"{promedio_aciertos:.2f}")
        print("Promedio fallos: ",f"{promedio_fallos:.2f}")

        cur.close()
        db.close()
        exit()
    info.text ="Tiempo: "+str(datetime.timedelta(seconds=round(obtener_tiempo()-inicio_tiempo)))

app.run()