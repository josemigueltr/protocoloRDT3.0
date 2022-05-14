#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
from random import random
from enum import Enum

verbose = 3
proba_perdida = 0.4
proba_corrup = 0.3
num_paq_perdidos = 0
num_paq_corromp = 0
num_paq_acapa3 = 0
time = 0.0
tiempo_mensajes = 15.0
total_mensajes = 5
eventos = []

def A_salida(mensaje):
    if estado_A!='ESPERANDO':
        num_sec= 0 1
        #Preguntar que es ack_num
        ack_num=
        payload=mensaje.datos
        checksum=
        paquete=Paquete(num_sec,ack_num,payload,checksum)
        a_capa_3(Entidad.ALICIA,paquete)
        startimer(Entidad.ALICIA,tiempo_mensajes)
        estado_A='ESPERANDO'


def A_entrada(paquete):
    #Mensajes ack o nack
    #Si recibimos ack pasamos al estado no esperando
    #si recibimos nack  ¿Que hacemos? mandamos a llamar a interrup timer para reeenviar el paquete
    pass

def A_interrup_timer():
    #Preguntar si se hace de manera automatica
    pass

def A_init():
    #inicializar estados 
    pass

def B_entrada(paquete):
    #Revisar si el paquete esta conrrompido o no
    #Si esta corrompido mandar mensaje nack
    #Si no esta corrompido mandar mensaje ack
    #como mandamos el mensaje ack o nack
    pass

def B_init():
    #inicializar estados
    pass


# Mensaje de la capa de aplicación
class Mensaje:
    def __init__(self, datos=b''):
        self.datos = datos


# Paquete que será movido a través de la capa de red
class Paquete:
    def __init__(self, num_secuencia=0, num_ack=0, checksum=0, payload=None):
        self.num_secuencia = num_secuencia
        self.num_ack = num_ack
        self.checksum = checksum
        self.payload = payload

    def __str__(self):
        return f'PAQUETE (num_secuencia: {self.num_secuencia}   ' \
               f'num_ack: {self.num_ack}   ' \
               f'checksum: {self.checksum}   ' \
               f'payload: {self.payload})'


# Enumeración para indicar qué entidad está llamando una función
class Entidad(Enum):
    ALICIA = 1
    BARTOLO = 2
    
    def __str__(self):
        return self.name



class TipoEvento(Enum):
    INTERRUP_TIMER = 1
    DESDE_CAPA_5 = 2
    DESDE_CAPA_3 = 3
    
    def __str__(self):
        return self.name


class Evento:
    def __init__(self, tiempo=0.0, tipo=None, entidad=None, paquete=None):
        self.tiempo = tiempo
        self.tipo = tipo
        self.entidad = entidad
        self.paquete = paquete
    
    def __str__(self):
        return f'tiempo: {self.tiempo:.2f}   ' \
               f'tipo: {self.tipo}   ' \
               f'entidad: {self.entidad}   ' \
               f'paquete: {self.paquete}'


def agregar_evento(evento):
    if verbose > 2:
        print(f"            INSERTEVENT: time is {time:.2f}")
        print(f"            INSERTEVENT: future time will be {evento.tiempo:.2f}")
    eventos.append(evento)
    eventos.sort(key=lambda x: x.tiempo)
    
def generar_sig_llegada():
    if verbose > 2:
        print('          GENERAR SIGUIENTE LLEGADA')
    x = tiempo_mensajes * random() * 2
    evento = Evento()
    evento.tiempo = time + x
    evento.tipo = TipoEvento.DESDE_CAPA_5
    evento.entidad = Entidad.ALICIA
    agregar_evento(evento)
        
def startimer(entidad, incremento):
    if verbose > 2:
        print(f'          START TIMER> empieza en el tiempo {time:.2f}')
    for evento in eventos:
        if evento.tipo == TipoEvento.INTERRUP_TIMER and evento.entidad == entidad:
            print('ADVERTENCIA: Se intentó iniciar un timer que ya había sido iniciado')
            return None
    evento = Evento()
    evento.tiempo = time + incremento
    evento.tipo = TipoEvento.INTERRUP_TIMER
    evento.entidad = entidad
    agregar_evento(evento)
    
def stoptimer(entidad):
    if verbose > 2:
        print(f'          STOP TIMER: deteniendo en tiempo {time:.2f}')
    for evento in eventos:
        if evento.tipo == TipoEvento.INTERRUP_TIMER and evento.entidad == entidad:
            eventos.remove(evento)
            return None
    print('ADVERTENCIA: no se pudo cancelar el timer')
    
def a_capa_3(entidad, paquete):
    lastime = 0.0
    global num_paq_perdidos, num_paq_corromp, num_paq_acapa3
    num_paq_acapa3 += 1
    if random() < proba_perdida:
        num_paq_perdidos += 1
        if verbose > 0:
            print('          A CAPA 3 > se perdió el paquete')
            return None
    mi_paquete =  copy.copy(paquete)
    if verbose > 2:
        print('          A CAPA 3 > {mi_paquete}')
    nuevo_evento = Evento()
    nuevo_evento.tipo = TipoEvento.DESDE_CAPA_3
    nuevo_evento.entidad = Entidad.ALICIA if entidad == Entidad.BARTOLO else Entidad.BARTOLO
    nuevo_evento.paquete = mi_paquete
    lastime = time
    for evento in eventos:
        if evento.tipo == TipoEvento.DESDE_CAPA_3 and evento.entidad == nuevo_evento.entidad:
            lastime = evento.tiempo
    nuevo_evento.tiempo = lastime + 1 + 9*random()
    
    if random() < proba_corrup:
        num_paq_corromp += 1
        x = random()
        if x < 0.75:
            mi_paquete.payload[0] = '#'
        elif x < 0.875:
            mi_paquete.seqnum = 999999
        else:
            mi_paquete.acknum = 999999
        if verbose > 0:
            print('          A CAPA 3 > paquete corrompido')
    if verbose > 2:
        print('          A CAPA 3 > programando llegada del otro lado')
    agregar_evento(nuevo_evento)
    return None

def a_capa_5(mensaje):
    if verbose > 2:
        print(f'          A CAPA 5 > se recibieron los datos: {mensaje.datos.decode()}')
        
def main():
    global time
    nsim = 0
    generar_sig_llegada()
    while nsim <= total_mensajes and eventos:
        evento = eventos.pop(0)
        if verbose >= 2:
            print(f'\nEVENTO {evento}')
        time = evento.tiempo
        if evento.tipo == TipoEvento.DESDE_CAPA_5:
            generar_sig_llegada()
            j = nsim % 26
            msj = Mensaje()
            msj.datos = bytes([j+97]*20)
            if verbose > 2:
                print(f'          MAINLOOP: datos: {msj.datos.decode()}')
            nsim += 1
            if evento.entidad == Entidad.ALICIA:
                A_salida(msj)
            else:
                B_salida(msj)
        elif evento.tipo == TipoEvento.DESDE_CAPA_3:
            paquete = Paquete()
            paquete.num_secuencia = evento.paquete.num_secuencia
            paquete.checksum = evento.paquete.checksum
            paquete.num_ack = evento.paquete.num_ack
            paquete.payload = evento.paquete.payload
            if evento.entidad == Entidad.ALICIA:
                A_entrada(paquete)
            else:
                B_entrada(paquete)
        elif evento.tipo == TipoEvento.INTERRUP_TIMER:
            if evento.entidad == Entidad.ALICIA:
                A_interrup_timer()
            else:
                B_interrup_timer()
        else:
            print('INTERNAL PANIC: evento desconocido')

if __name__ == '__main__':
    main()
