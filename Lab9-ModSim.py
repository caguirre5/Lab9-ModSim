import pygame
import sys
import math

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
screen_width = 800
screen_height = 600

# Colores
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 180, 0)

# Inicializar la pantalla
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simulación de Robot en el Mundial de Soccer")

# Configurar el reloj
clock = pygame.time.Clock()
target_fps = 45  # Establecer el número de FPS deseados

# Posición inicial del robot
robot_x = 700
robot_y = 300
# Posición inicial de la pelota
pelota_x = 500
pelota_y = 200
# Posición inicial de la porteria objetivo
porteria_x = 50
porteria_y = 300

# --------------------------------------------------------
# LOGICA DIFUSA PARA ENCONTRAR LA PELOTA
# --------------------------------------------------------
#Variables CRISP
distancia = ctrl.Antecedent(np.arange(0, 701, 1), 'distancia')
# Definir las funciones de membresía para distancia
distancia['cerca'] = fuzz.trimf(distancia.universe, [0, 125, 250])
distancia['media'] = fuzz.trimf(distancia.universe, [240, 370, 500])
distancia['lejos'] = fuzz.trimf(distancia.universe, [480, 590, 700])


resistencia = ctrl.Antecedent(np.arange(0, 101, 1), 'resistencia')
# Definir las funciones de membresía para distancia
resistencia['baja'] = fuzz.trimf(resistencia.universe, [0, 17, 34])
resistencia['normal'] = fuzz.trimf(resistencia.universe, [30, 50, 70])
resistencia['alta'] = fuzz.trimf(resistencia.universe,[66, 83, 100])

# Definir la variable de salida
movimiento = ctrl.Consequent(np.arange(0, 101, 1), 'movimiento')
# Definir las etiquetas lingüísticas y funciones de membresía
movimiento['caminar'] = fuzz.trimf(movimiento.universe, [0, 17, 34])
movimiento['trotar'] = fuzz.trimf(movimiento.universe, [30, 50, 70])
movimiento['correr'] = fuzz.trimf(movimiento.universe, [66, 83, 100])

#Clausulas de Horn / Definir las reglas difusas
regla1 = ctrl.Rule(distancia['cerca'] & resistencia['baja'], movimiento['caminar'])
regla2 = ctrl.Rule(distancia['cerca'] & resistencia['normal'], movimiento['trotar'])
regla3 = ctrl.Rule(distancia['cerca'] & resistencia['alta'], movimiento['correr'])
regla4 = ctrl.Rule(distancia['media'] & resistencia['baja'], movimiento['caminar'])
regla5 = ctrl.Rule(distancia['media'] & resistencia['normal'], movimiento['trotar'])
regla6 = ctrl.Rule(distancia['media'] & resistencia['alta'], movimiento['correr'])
regla7 = ctrl.Rule(distancia['lejos'] & resistencia['baja'], movimiento['caminar'])
regla8 = ctrl.Rule(distancia['lejos'] & resistencia['normal'], movimiento['trotar'])
regla9 = ctrl.Rule(distancia['lejos'] & resistencia['alta'], movimiento['correr'])

# Crear el sistema de control
sistema_de_control = ctrl.ControlSystem([regla1, regla2, regla3, regla4, regla5, regla6, regla7, regla8, regla9])
sistema = ctrl.ControlSystemSimulation(sistema_de_control)


# --------------------------------------------------------
# LOGICA DIFUSA PARA MEDIR FUERZA CON LA QUE SE DEBE PATEAR LA PELOTA
# --------------------------------------------------------
#Variables CRISP
distancia_porteria = ctrl.Antecedent(np.arange(0, 701, 1), 'distancia_porteria')
# Definir las funciones de membresía para distancia
distancia_porteria['cerca'] = fuzz.trimf(distancia_porteria.universe, [0, 120, 250])
distancia_porteria['media'] = fuzz.trimf(distancia_porteria.universe, [240, 360, 500])
distancia_porteria['lejos'] = fuzz.trimf(distancia_porteria.universe, [480, 600, 700])


angulo = ctrl.Antecedent(np.arange(-180, 181, 1), 'angulo')
# Definir las funciones de membresía para la variable angulo
angulo['izquierda'] = fuzz.trimf(angulo.universe, [-180, -120, -60])
angulo['centro'] = fuzz.trimf(angulo.universe, [-60, 0, 60])
angulo['derecha'] = fuzz.trimf(angulo.universe, [60, 120, 180])


# Definir la variable de salida
fuerza = ctrl.Consequent(np.arange(0, 101, 1), 'fuerza')
# Definir las etiquetas lingüísticas y funciones de membresía
fuerza['suave'] = fuzz.trimf(fuerza.universe, [0, 17, 34])
fuerza['medio'] = fuzz.trimf(fuerza.universe, [30, 50, 70])
fuerza['fuerte'] = fuzz.trimf(fuerza.universe, [66, 83, 100])


#Clausulas de Horn / Definir las reglas difusas
regla1 = ctrl.Rule(distancia_porteria['cerca'] & angulo['izquierda'], fuerza['medio'])
regla2 = ctrl.Rule(distancia_porteria['cerca'] & angulo['centro'], fuerza['suave'])
regla3 = ctrl.Rule(distancia_porteria['cerca'] & angulo['derecha'], fuerza['medio'])
regla4 = ctrl.Rule(distancia_porteria['media'] & angulo['izquierda'], fuerza['fuerte'])
regla5 = ctrl.Rule(distancia_porteria['media'] & angulo['centro'], fuerza['medio'])
regla6 = ctrl.Rule(distancia_porteria['media'] & angulo['derecha'], fuerza['fuerte'])
regla7 = ctrl.Rule(distancia_porteria['lejos'] & angulo['izquierda'], fuerza['fuerte'])
regla8 = ctrl.Rule(distancia_porteria['lejos'] & angulo['centro'], fuerza['fuerte'])
regla9 = ctrl.Rule(distancia_porteria['lejos'] & angulo['derecha'], fuerza['fuerte'])

# Crear el sistema de control
sistema_de_control2 = ctrl.ControlSystem([regla1, regla2, regla3, regla4, regla5, regla6, regla7, regla8, regla9])
sistema2 = ctrl.ControlSystemSimulation(sistema_de_control2)

fuerza_des = 0
fuerza_text = ''

#--------------------------------------------------------------------------------------------------------

# Crear un objeto de fuente
font = pygame.font.Font(None, 36)

can_kick = False
kicked = False
# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Dibujar el fondo
    screen.fill(green)

    # Dibujar el campo de fútbol (cancha, portería, etc.)
    pygame.draw.rect(screen, white, (50, 100, 700, 400), 3)  # Cancha
    pygame.draw.rect(screen, white, (50, 200, 100, 200), 3)  # Area de portería izquierda
    pygame.draw.rect(screen, white, (650, 200, 100, 200), 3)  # Area de portería derecha
    pygame.draw.rect(screen, white, (50, 250, 15, 100), 0)  # Porteria izquierda
    pygame.draw.rect(screen, white, (735, 250, 15, 100), 0) # Portería derecha
    # Dibujar el robot
    pygame.draw.circle(screen, (0,0,0), (int(robot_x), int(robot_y)), 20)
    # Dibujar la pelota
    pygame.draw.circle(screen, red, (int(pelota_x), int(pelota_y)), 10)

    distancia_robot_pelota = ((robot_x - pelota_x) ** 2 + (robot_y - pelota_y) ** 2) ** 0.5

    # Definir valores de entrada
    sistema.input['distancia'] = distancia_robot_pelota
    sistema.input['resistencia'] = 20

    # Calcular la salida difusa
    sistema.compute()   

    result_1 = ''
    desplazamiento = 0

    if sistema.output['movimiento'] > 66:
        result_1= "Correr"
        desplazamiento = 3
    elif sistema.output['movimiento'] > 33:
        result_1= "Trotar"
        desplazamiento = 2
    else:
        result_1= "Caminar"
        desplazamiento = 1

    # Calcular el ángulo entre el robot y la pelota
    angulo = math.atan2(pelota_y - robot_y, pelota_x - robot_x)


    # Renderizar el texto
    texto = font.render(f"Accion: {result_1}", True, (0, 0, 0))
    # Mostrar el texto en la pantalla
    screen.blit(texto, (550, 10))

    # Renderizar el texto
    texto2 = font.render(f"Fuerza de pateo: {fuerza_text}", True, (0, 0, 0))
    # Mostrar el texto en la pantalla
    screen.blit(texto2, (10, 10))

    if distancia_robot_pelota > 18 and not kicked:

        # Como conocemos las coordenadas de la porteria y pelota, podemos definir la fuerza a la que patearemos desde un inicio
        distancia_porteria_pelota_inicial = ((pelota_x - porteria_x) ** 2 + (pelota_y - porteria_y) ** 2) ** 0.5
        # Calcular el ángulo entre la porteria y la pelota
        angulo_porteria = math.atan2(porteria_y - pelota_y, porteria_x - pelota_x)

        # Definir valores de entrada
        sistema2.input['distancia_porteria'] = distancia_porteria_pelota_inicial
        sistema2.input['angulo'] = angulo_porteria

        # Calcular la salida difusa
        sistema2.compute()

        if sistema2.output['fuerza'] > 66:
            fuerza_des = 20
            fuerza_text = 'Fuerte'
        elif sistema2.output['fuerza'] > 33:
            fuerza_des = 15
            fuerza_text = 'Medio'
        else:
            fuerza_des = 10
            fuerza_text = 'Suave'   


        # Calcular las nuevas coordenadas del robot
        nuevo_x = robot_x + desplazamiento * math.cos(angulo)
        nuevo_y = robot_y + desplazamiento * math.sin(angulo)

        # Actualizar la posición del robot
        robot_x = nuevo_x
        robot_y = nuevo_y
    else:
        can_kick = True
        kicked = True

    
    if can_kick:
        
        
        # Como conocemos las coordenadas de la porteria y pelota, podemos definir la fuerza a la que patearemos desde un inicio
        distancia_porteria_pelota = ((pelota_x - porteria_x) ** 2 + (pelota_y - porteria_y) ** 2) ** 0.5 

        

        if distancia_porteria_pelota > 18:
            # Calcular las nuevas coordenadas del robot
            nuevo_x = pelota_x + fuerza_des * math.cos(angulo_porteria)
            nuevo_y = pelota_y + fuerza_des * math.sin(angulo_porteria)

            # Actualizar la posición del robot
            pelota_x = nuevo_x
            pelota_y = nuevo_y 

            fuerza_des -= 1

            if fuerza_des == 0:# and (pelota_x != porteria_y) and (pelota_y != porteria_x)
                can_kick = False
                kicked = False

    pygame.display.update()
    clock.tick(target_fps)
# Salir de Pygame
pygame.quit()
sys.exit()
