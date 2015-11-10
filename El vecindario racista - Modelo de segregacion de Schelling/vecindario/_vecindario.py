#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ejercicio del Vecindario Racista

Taller de la PyConEs 2015: Simplifica tu vida con sistemas complejos y algoritmos genéticos

Este script contiene las funciones y clases necesarias para ejecutar una simulación del
modelo de emergencia de segregación propuesto por Schelling.

http://www.stat.berkeley.edu/~aldous/157/Papers/Schelling_Seg_Models.pdf

Este script usa arrays de numpy, aunque no debería ser difícil para alguien con experiencia
sustituírlos por otras estructuras si es necesario.

También usa la librería Matplotlib en las funciones que dibujan resultados."""


import numpy as np
import matplotlib.pyplot as plt

#Primero vamos a definir los dos tipos de objeto que necesitamos: 

class Parcela:
    '''Este objeto representa la finca o mundo en el que viven los vecinos
    
    Controla todas las variables globales y contiene la lista de vecinos'''
    def __init__(self, dim1, intolerance = 55, intomax = 100, dim2 = 0, r = 1):        
        '''Esta función se ejecuta al crear el objeto:
        Asignamos a las variables locales una serie de valores que debemos pasar
        como argumento a la hora de crear el mundo:
        -Su anchura
        -La intolerancia de sus ciudadanos(por defecto, 55)
        -Su intolerancia máxima(proporción de vecinos del mismo color máximos para que no quiera mudarse)
        -Su altura (por defecto, igual que la anchura)
        -El radio de análisis de confort'''
        self.dim1 = dim1
        if dim2 == 0: #Si la altura es 0 (por defecto), la hacemos igual a la anchura
            self.dim2 = dim1
        else:
            self.dim2 = dim2
        self.r = r
        self.intolerance = intolerance
        self.intomax = intomax
        self.tot_pos = self.dim1 * self.dim2 #Número total de casillas
        self.libres = list(range(self.tot_pos))#En este momento, todas las casillas están libres
        self.matrix = np.zeros((self.dim2, self.dim1), dtype=np.int8)#Esta matriz representa al vecindario.
        #Esta matriz empieza llena de ceros (aún no hay nade viviendo), pero conforme vayamos 
        #añadiendo vecinos, sus casillas se llenarán con el número que representa al color del ocupante.
        self.matrix_ampli = np.zeros((self.dim2 + 2 * r, self.dim1 + 2 * self.r), dtype=np.int8)
        #Esta matriz es igual que la anterior, pero con un reborde vacío alrededor que luego nos será útil al 
        #al calcular los vecinos de las casillas que están en los bordes.
        self.listavecinos = []
        #En esta lista, que aún está vacía, iremos almacenando a los vecinos que vayamos creando. Así,
        #luego los podremos ir llamando fácilmente.
    def coord(self, num, dim1):
        '''Devuelve las coordenadas del elemento enésimo de la matriz'''
        fila = num//dim1
        columna = num - fila * dim1
        return[fila, columna]
    def asignar(self):
        '''Escoge una casilla aleatoria libre y devuelve su número. Luego, la borra de 
        la lista de casillas libres.'''
        n = np.random.randint(0, len(self.libres))
        return self.libres.pop(n)
    def liberar(self, f, c):
        '''Libera una casilla ocupada, borrándola de las matrices y añadiéndola a la lista
        de casillas libres'''
        n = f * self.dim1 + c #Calcula el número de la casilla a partir de las coordenadas
        self.libres.append(n)        
        self.matrix[f, c] = 0
        self.matrix_ampli[f + 1 , c + 1 ] = 0
    def nuevo(self, color):
        '''Crea un nuevo vecino y le asigna una casilla libre aleatoria'''
        n = self.asignar() #Escoge una casilla libre aleatoria
        coordenadas = self.coord(n, self.dim1)#Calcula sus coordenadas
        self.matrix[coordenadas[0], coordenadas[1]] = color# Asigna a las matrices el color del nuevo vecino
        self.matrix_ampli[coordenadas[0] + self.r , coordenadas[1] + self.r ] = color
        self.listavecinos.append(Vecino(color, self, coordenadas, 
                                        self.intolerance, self.intomax))#Añade el nuevo a la lista de vecinos
    def clear(self):
        '''Borra a todos los vecinos y deja todo limpio y en blanco'''
        self.libres = list(range(self.tot_pos))
        self.matrix = np.zeros((self.dim2, self.dim1), dtype=np.int8)       
        self.matrix_ampli = np.zeros((self.dim2 + 2*self.r, self.dim1 + 2*self.r), dtype=np.int8)
        self.listavecinos = []
    def entorno(self, f, c, color):
        '''Dada una casilla y un color, analiza el entorno de la casilla y 
        devuelve la proporción de casillas ocupadas de ese color'''
        #El parámetro r de análisis se pasa de manera implícita dentro de self
        r = self.r
        vecinos_ocupados = -1 #Empiezan a -1 porque el bucle contará a la propia casilla 
        vecinos_iguales = -1
        for xx in range(1 + 2 * r):
            for yy in range(1 + 2 * r):
                f_a = f + xx
                c_a = c + yy
                color_a = self.matrix_ampli.item(f_a, c_a)#Usamos la matriz ampliada para poder analizar fácilmente
                # las casillas que están en los bordes sin complicar la notación
                if color_a == 0 :
                    pass
                elif color_a == color :
                    vecinos_ocupados += 1
                    vecinos_iguales += 1
                else:
                    vecinos_ocupados += 1
        if vecinos_ocupados == 0 :
            return 1.
        else:
            return vecinos_iguales / vecinos_ocupados
        
class Vecino:
    '''
    Este objeto representa a cada vecino del vecindario, es decir, cada circulito.

    Este objeto está pensado para ser llamado sólo desde el objeto "Parcela".
    '''
    def __init__(self, color, parcela, coords, intolerance = 55, intomax = 100):
        '''Esta función se ejecuta al crear el objeto:
        Asignamos a las variables locales una serie de valores que debemos pasar
        como argumento a la hora de crear cada ciudadano:
        -Su color
        -Su intolerancia(proporción de vecinos del mismo color mínimos para que no quiera mudarse)
        -Su intolerancia máxima(proporción de vecinos del mismo color máximos para que no quiera mudarse)
        -Desde qué parcela se le ha invocado (para luego poder usarla desde él)
        -Sus coordenadas'''
        self.color = color
        self.intolerance = intolerance
        self.intomax = intomax
        self.parcela = parcela
        self.coords = coords
    def mudanza(self):
        '''Esta función sirve para mudar el vecino desde su posición a otro sitio'''
        n = self.parcela.asignar() #Primero se le asigna un sitio libre de la parcela   
        r = self.parcela.r
        coordenadas = self.parcela.coord(n, self.parcela.dim1)# Se calculan las coord del nuevo sitio        
        self.parcela.matrix[coordenadas[0], coordenadas[1]] = self.color# Se cambia el color del nuevo sitio en la matriz 
        self.parcela.matrix_ampli[coordenadas[0] + r , coordenadas[1] + r ] = self.color#Y en la matriz ampliada
        self.parcela.liberar(self.coords[0], self.coords[1])# Se avisa a la parcela de que el sitio viejo está libre
        self.coords = coordenadas# Se cambian las coordenadas que el vecino tiene guardadas a las nuevas
    def satisfecho(self):
        '''Esta función sirve para saver si el vecino está satisfecho con su entorno'''
        vecin_prop = self.parcela.entorno(self.coords[0], self.coords[1], self.color)#Primero, en
                            #la parcela se calcula qué porcentaje de sus vecinos son del mismo color que él
        suficientes_iguales = vecin_prop * 100 >= self.intolerance # Se compara con la intolerancia, 
                            #si la proporción es mayor que su intol, está a gusto (True), si no, (False)
        no_demasiados_iguales = vecin_prop * 100 <= self.intomax # También se compara con la intol máxima,
                            #si la proporción de gente igual alrededor es damasiado alta, tampoco está a gusto
        
        return suficientes_iguales and no_demasiados_iguales, vecin_prop        

    
#Sólo con estos objetos ya podemos ejecutar nuestras simulaciones, pero
#nos será mucho más fácil si definimos unas cuantas funciones útiles:

def crear_mundo(tam = 10, colors = 2, vacios = 20, intolerance = 30, intom = 100,
                prop = [0.5], rad = 1, h_fel = [], h_seg = []):
    '''Crea un nuevo espacio de análisis, con una matriz cuadrada de base.
    Variables:
    -tam: número de casillas del lado de la matriz.
    -colors: número de colores.
    -vacios: porcentaje de plazas vacías que quedarán en la matriz.
    -intolerance: porcentaje mínimo de vecinos adyacentes de su mismo color que admite
    un vecino antes de cambiar su posición.
    -intom: porcentaje máximo de vecinos adyacentes del mismo color que admite antes de mudarse.
    -prop: Proporción de cada color, es una lista con tantos elementos como colores menos uno.
    -rad: radio de análisis cuando se observan los vecinos de alguien.
    -h_fel: Aquí se irán guardando los valores de felicidad.
    -h_seg: Aquí, los de segregación.'''
    
    par = Parcela(tam, intolerance = intolerance, intomax = intom, r=rad) #Se crea una parcela nueva
    size = par.tot_pos
    
    llenos = (size * (100 - vacios))//100 #Se calculan cuantas casillas deben tener ocupantes.
    asignados = 0
    
    
    #A continuación, iremos añadiendo vecinos en la proporción deseada
    for color in range(1, colors):
        asignados_al_final = asignados + int(np.round(llenos * prop[color-1]))
        for i in range(asignados, asignados_al_final):
            par.nuevo(color)
        asignados = asignados_al_final
    for i in range(asignados, llenos + 1):
        par.nuevo(colors) 
        
    #Lo último que hacemos es calcular el nivel de satisfacción y de segregación que 
    #tiene esta distribución inicial
    tot_satis = 0
    tot_seg = 0
    for i in par.listavecinos : 
        satis, prop_vec = i.satisfecho()
        tot_seg += prop_vec
        if satis:
            tot_satis +=1
        
            
    satisfaccion = 100 * tot_satis/len(par.listavecinos) #Es el porcentaje de la población que está a gusto
    segregacion = 100 * tot_seg/len(par.listavecinos) #Es la media del porcentaje de vecinos iguales a uno mismo.
    h_fel.append(np.round(satisfaccion,2))
    h_seg.append(np.round(segregacion,2))
    
    return par, (llenos, colors, prop)

def vecin_print(par, datacolor, dim, n):    
    '''Esta función sirve para dibujar la situación actual del vecindario.
    Necesita:
    -par: el objeto parcela del vecindario.
    -datacolor: una lista que contiene variables que explican cómo representar los datos.
    Esta lista es el segundo argumento de salida de la función "crear_mundo".
    -dim: el ancho de la matriz del mundo.
    -n: el número de la iteración'''
    
    
    
    colordict = {} #Aquí vamos a ir guardando las coordenadas de cada vecino agrupados por colores
    llenos, colors, prop = datacolor #desempaquetamos los datos de datacolor
    colornames = ['b', 'r', 'g', '0.4', 'c', 'k'] #Estos colores son los de los tipos de vecinos
    
    #Ahora, un bucle similar al que creó los vecinos los distribuirá por colores
    #para después poder pintarlos
    asignados = 0
    for color in range(1, colors):
        colorpop = []
        asignados_al_final = asignados + int(np.round(llenos * prop[color-1]))
        for i in range(asignados, asignados_al_final):
            colorpop.append(par.listavecinos[i].coords)
        asignados = asignados_al_final
        colordict[color-1] = np.array(colorpop)
    colorpop = []
    for i in range(asignados, llenos + 1):
        colorpop.append(par.listavecinos[i].coords)
    colordict[colors-1] = np.array(colorpop)   
       
        
    
     
    plt.figure(None, figsize = (10,10))
    plt.title('Vecindario: n =' + str(n))
    tam_point = 105722 * dim ** -1.78 #El tamaño de los círculos se ajusta al tamaño de la matriz
    
    # Al representar el estado, también vamos a mostrar el nivel de satisfacción
    # y segregación, así que los calculamos.
    tot_satis = 0
    tot_seg = 0
    for i in par.listavecinos : 
        satis, prop_vec = i.satisfecho()
        tot_seg += prop_vec
        if satis:
            tot_satis +=1
        else:
            plt.scatter(i.coords[0], i.coords[1], c = '0.6',marker = 's',  s = tam_point, linewidths=0)
            
    satisfaccion = 100 * tot_satis/len(par.listavecinos)
    segregacion = 100 * tot_seg/len(par.listavecinos)
    nota = 'Satisfacción de la población: ' + str(np.round(satisfaccion, 2)) + '%'
    nota2 = 'Segregación de la población: ' + str(np.round(segregacion, 2)) + '%'
    
    #Lo pintamos todo:
    for i in range(colors):
        plt.scatter(colordict[i][:,0], colordict[i][:,1], c = colornames[i], s = tam_point, linewidths=0)

    plt.xlim(-1, dim)
    plt.ylim(-1, dim)
     
    plt.text(0, -1 - dim/20, nota, fontsize=12)
    plt.text(0, -1 - 2*dim/20, nota2,fontsize=12)
    

def step_mudanza(par, datacolor, n, dim, h_fel = None, h_seg = None):
    '''Esta función recorre toda la lista de vecinos y los muda si no están satisfechos.
    después, guarda los valores conseguidos de felicidad y segregación, y por último
    representa todo gráficamente'''
    
    
    if not h_fel: h_fel = []                  
    if not h_seg: h_seg = []  
        
        
    #Mudanza
    for i in par.listavecinos : 
        if not i.satisfecho()[0]:
            i.mudanza()
    
    n += 1
    #Representación gráfica
    colordict = {}
    llenos, colors, prop = datacolor
    colornames = ['b', 'r', 'g', '0.4', 'c', 'k']
    
    asignados = 0
    for color in range(1, colors):
        colorpop = []
        asignados_al_final = asignados + int(np.round(llenos * prop[color-1]))
        for i in range(asignados, asignados_al_final):
            colorpop.append(par.listavecinos[i].coords)
        asignados = asignados_al_final
        colordict[color-1] = np.array(colorpop)
    colorpop = []
    for i in range(asignados, llenos + 1):
        colorpop.append(par.listavecinos[i].coords)
    colordict[colors-1] = np.array(colorpop)   
    
    plt.figure(None, figsize = (10,10))
    tam_point = 105722 * dim ** -1.78
    
    tot_satis = 0
    tot_seg = 0
    for i in par.listavecinos : 
        satis, prop_vec = i.satisfecho()
        tot_seg += prop_vec
        if satis:
            tot_satis +=1
        else:
            plt.scatter(i.coords[0], i.coords[1], c = '0.6',marker = 's',  s = tam_point, linewidths=0)
            
    satisfaccion = 100 * tot_satis/len(par.listavecinos)
    segregacion = 100 * tot_seg/len(par.listavecinos)
    h_fel.append(np.round(satisfaccion,2))
    h_seg.append(np.round(segregacion,2))
    nota = 'Satisfacción de la población: ' + str(np.round(satisfaccion, 2)) + '%'
    nota2 = 'Segregación de la población: ' + str(np.round(segregacion, 2)) + '%'
    plt.title('Vecindario: n =' + str(n))
    
    for i in range(colors):
        plt.scatter(colordict[i][:,0], colordict[i][:,1], c = colornames[i], s = tam_point, linewidths=0)
    plt.xlim(-1, dim )
    plt.ylim(-1, dim )
    plt.text(0, -1 - dim/20, nota, fontsize=12)
    plt.text(0, -1 - 2*dim/20, nota2,fontsize=12)
    return n 


def _step_mudanza_ciego(par, numcolor, n, dim, h_fel = None, h_seg = None):
    '''Esta función recorre la lista de vecinos y los muda si no están satisfechos,
    pero no los representa gráficamente.'''
    
    
    if not h_fel: h_fel = []                  
    if not h_seg: h_seg = []  
         
    
    for i in par.listavecinos : 
        if not i.satisfecho()[0]:
            i.mudanza()
    tot_satis = 0
    tot_seg = 0
    for i in par.listavecinos : 
        satis, prop_vec = i.satisfecho()
        tot_seg += prop_vec
        if satis:
            tot_satis +=1
                    
    satisfaccion = 100 * tot_satis/len(par.listavecinos)
    segregacion = 100 * tot_seg/len(par.listavecinos)
    h_fel.append(np.round(satisfaccion,2))
    h_seg.append(np.round(segregacion,2))
    return n + 1


def step_multiple(par, datacolor, n, dim, h_fel = None, h_seg = None, numsteps = 20):
    '''Recorre la lista "numstep" veces, mudando a los vecinos infelices, y finalmente
    representa gráficamente el resultado'''
        
    if not h_fel: h_fel = []                  
    if not h_seg: h_seg = []  
     
    print('Calculando steps, total', numsteps, ':', end=' ')
    for i in range(numsteps-1):
        n = _step_mudanza_ciego(par, datacolor, n, dim, h_fel, h_seg)
        print(i + 1 , end='·')
        
    print(numsteps)
    n = step_mudanza(par, datacolor, n, dim, h_fel, h_seg)
    return n
    
def evolucion(h_fel, h_seg):
    '''Representa gráficamente la evolución de los valores
    de felicidad y segregación a lo largo de las iteraciones'''
    plt.figure(1, figsize= (8,5))
    plt.title('Evolución de la felicidad del vecindario')
    plt.xlabel('Steps')
    plt.ylabel('Felicidad (%)')
    plt.plot(h_fel)
    plt.grid()
    
    plt.figure(2, figsize= (8,5))
    plt.title('Evolución de la segregación del vecindario')
    plt.xlabel('Steps')
    plt.ylabel('Segregación (%)')
    plt.plot(h_seg)
    plt.grid()
    
    
#Ejemplo:
if __name__ == '__main__':
    

    
    dim = 20
    vacios = 10
    colors = 2
    prop = [0.5]
    n = 0
    intolerance = 35
    intom = 100
    rad = 1
    historia_felicidad = []
    historia_segregacion = []

    par, datacolor = crear_mundo(dim, colors= colors, prop= prop, vacios = vacios,
                             intolerance=intolerance, intom= intom, rad = rad,
                            h_fel = historia_felicidad, h_seg = historia_segregacion)

    vecin_print(par, datacolor, dim, n)
    plt.show()

    n = step_mudanza(par, datacolor, n, dim,
           historia_felicidad, historia_segregacion)
    plt.show()
    n = step_multiple(par, datacolor, n, dim,
           historia_felicidad, historia_segregacion, 15)
    plt.show()
    evolucion(historia_felicidad, historia_segregacion)
    plt.show()
    
