#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
from random import random
from enum import Enum

verbose = 3
proba_perdida = 0.0
proba_corrup = 0.0
num_paq_perdidos = 0
num_paq_corromp = 0
num_paq_acapa3 = 0
time = 0.0
tiempo_mensajes = 15.0
total_mensajes = 10
eventos = []
secuencia = 0


class Alicia():
    """
    Clase que representa a Alice la emisora
    """
    def __init__(self, estado, sec, ultimo_paquete):
        self.estado = estado
        self.sec = sec
        self.ultimo_paquete = ultimo_paquete

class Bartolo():
    """
    Clase que representa a Bartolo el receptor
    """
    def __init__(self, sec):
        self.sec = sec

def A_salida(mensaje):
    global secuencia
    if a.estado != 'ESPERANDO_ACK':
        num_sec=secuencia
        ack_num=secuencia
        payload=mensaje.datos
        checksum=get_checksum(payload)
        paquete=Paquete(num_sec,ack_num,payload,checksum)
        a.ultimo_paquete=copy.deepcopy(paquete)
        a_capa_3(Entidad.ALICIA, paquete)
        startimer(Entidad.ALICIA, 10)
        a.estado='ESPERANDO_ACK'
        secuencia=(secuencia+1)%2

           
def A_entrada(paquete):
    #Revisamos que el paquete no este corrupto
    if get_checksum(paquete.payload) == paquete.checksum:
        #Si el paquete recibido es un NACK reenviamos el ultimo paquete
        if(paquete.ack_num<0):
            a_capa_3(Entidad.ALICIA,a.ultimo_paquete)
        else:
            #Si el paquete recibido es un ACK, se actualiza el estado de  alicia
            a.estado='ESPERANDO_LLAMADA'
            stoptimer(Entidad.ALICIA)
    else:
            a_capa_3(Entidad.ALICIA,a.ultimo_paquete)


def A_interrup_timer():
    # En otro caso, volvemos a mandar el paquete
    a_capa_3(Entidad.ALICIA, a.ultimo_paquete)
    startimer(Entidad.ALICIA, 1)


def A_init():
    return Alicia(estado='ESPERANDO_LLAMADA', sec=0, ultimo_paquete=None)

def B_entrada(paquete):
    if get_checksum(paquete.payload) == paquete.checksum:
        payload='ack'
        checksum_ack=get_checksum(payload)
        ack_p=Paquete(paquete.num_sec,paquete.ack_num,payload,checksum_ack)
        a_capa_3(Entidad.BARTOLO,ack_p)
    else:
        payload='nack'
        ## 0 --> -1 1 --> -2
        nack_num= -1 if paquete.ack_num==0 else -2
        checksum_nack=get_checksum(payload)
        nack_p=Paquete(paquete.num_sec,nack_num,payload,checksum_nack)
        a_capa_3(Entidad.BARTOLO,nack_p)
        
def B_init():
    return Bartolo(sec=0)

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
    """
    Donde entidad puede ser ALICIA o BARTOLO e incremento
    corresponde al tiempo de duración del temporizador. Cada entidad solo puede iniciar o terminar
    su propio temporizador (i.e. las funciones de BARTOLO no deben llamar esta función con
    ALICIA como parámetro).
    """
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
    """
    Donde entidad puede ser ALICIA o BARTOLO. Detiene el temporizador.
    No es necesario llamar a esta función cuando el temporizador termina su tiempo de duración, de
    eso se encarga el simulador.
    """
    if verbose > 2:
        print(f'          STOP TIMER: deteniendo en tiempo {time:.2f}')
    for evento in eventos:
        if evento.tipo == TipoEvento.INTERRUP_TIMER and evento.entidad == entidad:
            eventos.remove(evento)
            return None
    print('ADVERTENCIA: no se pudo cancelar el timer')
    

def a_capa_3(entidad, paquete):
    """
    Esta función entrega el paquete a la capa 3 que será enviado a la
    otra entidad. Por ejemplo, si entidad es ALICIA entonces el mensaje será entregado a BARTOLO.
    """
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
        print(f'          A CAPA 3 > {mi_paquete}')
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
            mi_paquete.payload = b'#'+mi_paquete.payload[1:]
        elif x < 0.875:
            mi_paquete.secnum = 255
        else:
            mi_paquete.acknum = 255
        if verbose > 0:
            print('          A CAPA 3 > paquete corrompido')
    if verbose > 2:
        print('          A CAPA 3 > programando llegada del otro lado')
    agregar_evento(nuevo_evento)
    return None

def a_capa_5(entidad, mensaje):
    """
    Esta función entrega el mensaje a la capa 5 de la entidad receptora.
    Ya que en esta práctica solamente BARTOLO fungirá como receptor, no se usará la función
    con ALICIA como argumento.
    """
    if verbose > 2:
        print(f'          A CAPA 5 > se recibieron los datos: {mensaje.datos.decode()}')

def get_checksum(data):
    """
    Método que obtiene el checksum de la información.
    Decidimos pasar la información a cadena para poder trabajar más fácilmente
    sobre caracter por caracter
    """
    # Pasamos los bytes a cadena para trabajarlo como char
    data = data.decode(encoding='UTF-8')
    # Obtenemos la longitud de la cadena
    i = len(data)
    # Si la longitud es impar, entonces le restamos uno para
    # poder agruparlos dos a dos
    if (i & 1):
        # Restamos uno a la posición donde estábamos
        i -= 1
        # Y obtenemos el unicode que equivale al último caracter
        sum = ord(data[i])
    else:
        sum = 0
    # Para cada dos char vamos sumando sus valores en entero
    # y guardamos el resultado en sum
    while i > 0:
        i -= 2
        sum += (ord(data[i + 1]) << 8) + ord(data[i])
    # Si hay desbordamiento, entonces se acarrea sobre el bit
    # de menor peso
    sum = (sum >> 16) + (sum & 0xffff)
    # Calculamos el complemento a uno
    result = (~ sum) & 0xffff
    # Ordenamos correctamente el resultado
    result = result >> 8 | ((result & 0xff) << 8)
    # Devolvemos el binario
    return bin(result)

a = A_init()
b = B_init()

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
    print('\n\n\n\n\n\n'*3)
if __name__ == '__main__':
    main()
