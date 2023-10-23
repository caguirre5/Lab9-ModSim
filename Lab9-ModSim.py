import pygame
import sys
import math

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# def definir_sistema_pelota(ball_pos, ):
#     # Define el sistema de lógica difusa para encontrar la pelota
#     ...

# def definir_sistema_fuerza():
#     # Define el sistema de lógica difusa para saber la fuerza de pateo
#     ...

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
screen_width = 800
screen_height = 600

# Colores
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)

# Inicializar la pantalla
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simulación de Robot en el Mundial de Soccer")

# Posición inicial del robot
robot_x = 700
robot_y = 300
# Posición inicial de la pelota
pelota_x = 200
pelota_y = 300
# Posición inicial de la porteria objetivo
porteria_x = 50
porteria_y = 250

# --------------------------------------------------------
# LOGICA DIFUSA PARA ENCONTRAR LA PELOTA
# --------------------------------------------------------
#Variables CRISP
distancia = ctrl.Antecedent(np.arange(0, 701, 1), 'distancia')
# Definir las funciones de membresía para distancia
distancia['cerca'] = fuzz.trimf(distancia.universe, [0, 150, 300])
distancia['media'] = fuzz.trimf(distancia.universe, [150, 300, 450])
distancia['lejos'] = fuzz.trimf(distancia.universe, [300, 500, 700])


resistencia = ctrl.Antecedent(np.arange(0, 101, 1), 'resistencia')
# Definir las funciones de membresía para distancia
resistencia['baja'] = fuzz.trimf(resistencia.universe, [0, 25, 50])
resistencia['normal'] = fuzz.trimf(resistencia.universe, [25, 50, 75])
resistencia['alta'] = fuzz.trimf(resistencia.universe, [50, 75, 100])

# Definir la variable de salida
movimiento = ctrl.Consequent(np.arange(0.1, 0.4, 0.1), 'movimiento')
# Definir las etiquetas lingüísticas y funciones de membresía
movimiento['caminar'] = fuzz.trimf(movimiento.universe, [0.1, 0.1, 0.2])
movimiento['trotar'] = fuzz.trimf(movimiento.universe, [0.1, 0.2, 0.3])
movimiento['correr'] = fuzz.trimf(movimiento.universe, [0.2, 0.3, 0.3])

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

#variables Linguisticas

#Clausulas de Horn


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
    
    pygame.display.update()

    distancia_robot_pelota = ((robot_x - pelota_x) ** 2 + (robot_y - pelota_y) ** 2) ** 0.5

    # Definir valores de entrada
    sistema.input['distancia'] = distancia_robot_pelota
    sistema.input['resistencia'] = 10

    # Calcular la salida difusa
    sistema.compute()   


    # Calcular el ángulo entre el robot y la pelota
    angulo = math.atan2(pelota_y - robot_y, pelota_x - robot_x)

    if distancia_robot_pelota > 18:
        # Calcular las nuevas coordenadas del robot
        nuevo_x = robot_x + (sistema.output['movimiento']) * math.cos(angulo)
        nuevo_y = robot_y + (sistema.output['movimiento']) * math.sin(angulo)

        # Actualizar la posición del robot
        robot_x = nuevo_x
        robot_y = nuevo_y


# Salir de Pygame
pygame.quit()
sys.exit()
