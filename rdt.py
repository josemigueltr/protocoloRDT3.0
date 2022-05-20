#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
from random import randint, random
from enum import Enum

verbose = 2
#Porcentaje de que los paquetes se pierdan
proba_perdida = 0.3
#Probabilidad de que los paquetes se corrompan
proba_corrup = 0.2
num_paq_perdidos = 0
num_paq_corromp = 0
num_paq_acapa3 = 0
time = 0.0
tiempo_mensajes = 5.0
total_mensajes = 100
eventos = []
secuencia=0


def get_checksum(payload, num_ack, num_secuencia):
    """
        Funcion que calcula el checksum de un paquete
        para corroborar si se ha corrompido durante la transmisión
    """
    payload = payload.decode(encoding='UTF-8')
    l = len(payload)
    #Hacemos que la longitud de la cadena sea multiplo de 2
    l=l-1 if l%2!=0 else l    
    # Al empezar la suma agregamos el numero de scuencia y el numero de ack
    sum = (ord(str(num_ack))) + (ord(str(num_secuencia)))
    #Agregamos los caracteres del payload al sum
    for i in reversed(range(0,l+1,2)):
        if(i==0):
            break
        sum += (ord(payload[i-2 + 1]) << 8) + ord(payload[i-2])
    #Manejamos el desbordamiento y sacamos complemento a 1
    resultado = (~ (sum >> 16) + (sum & 0xffff)) & 0xffff
    return bin(resultado >> 8 | ((resultado & 0xff) << 8))


class Alicia():
    """
        Clase para representar a Alicia la emisora
        posee un estado y un ultimo paquete
    """
    def __init__(self, estado,  ultimo_paquete):
        self.estado = estado
        self.ultimo_paquete = ultimo_paquete


def A_salida(mensaje):
    """
        Funcion que se encarga de mandar un paquete a Bartolo
        :param mensaje: mensaje a enviar 
    """
    #Secuencia que indica cual es el bit actual que se manejara en paquete
    global secuencia
    #Si no se esta esperando nada  mandamos el mensaje
    if a.estado != 'ESPERANDO_ACK':
        #Creamos el paquete
        paquete = Paquete(num_secuencia=secuencia, num_ack=secuencia, checksum=get_checksum(mensaje.datos, num_ack=secuencia, num_secuencia=secuencia), payload=mensaje.datos)
        print(f'            {paquete}')
        #Actualizo es estado de Alicia
        a.estado = 'ESPERANDO_ACK'
        #Actualizo el ultimo paquete para enviarlo en los reenvios
        a.ultimo_paquete = copy.deepcopy(paquete)
        a_capa_3(Entidad.ALICIA, paquete)
        startimer(Entidad.ALICIA, 10)
        print("\n-------------------------------------------------------")
        print(f"PAQUETE ENVIADO ...")
        print("-------------------------------------------------------\n")
    else:
        #Se esta esperando un mensaje de confirmacion ack asi que se ignoran paquetes
        print("\n-------------------------------------------------------")
        print(f"PAQUETE NO ENVIADO ... SE ESTA ESPERANDO ACK")
        print("-------------------------------------------------------\n")

    

def A_entrada(paquete):
    """
        Funcion que se encarga de manejar los paquetes que llegan a Alicia
        :param paquete: paquete que llega a Alicia
    """
    global secuencia
    print("\n-------------------------------------------------------")
    print(f"RECIBIENDO PAQUETE DE BARTOLO")
    print("-------------------------------------------------------\n")
    #Revisamos que el paquete no se haya corrompido
    if paquete.checksum == get_checksum(paquete.payload, paquete.num_ack, paquete.num_secuencia):
        #El numero de secuencia es distinto o es duplicado
        if paquete.num_ack !=secuencia:
            print("\n-------------------------------------------------------")
            print("SE RECIBIO UN ACK CON NUMERO DE SECUENCIA INVERTIDO")
            print("-------------------------------------------------------\n")
            
        #recibimos un ack
        else:
            print("\n-------------------------------------------------------")
            print("SE RECIBIO UN PAQUETE DE CONFIRMACION ACK")
            print("-------------------------------------------------------\n")
            #Actualizamos el numero de secuencia y el estado de Alicia
            a.estado = 'ESPERANDO_LLAMADA'
            secuencia = (secuencia + 1 ) % 2
            stoptimer(Entidad.ALICIA)
    #Se recibe un paquete corrupto        
    else:
        print("\n-------------------------------------------------------")
        print("SE RECIBIO UN PAQUETE CORRUPTO")
        print("-------------------------------------------------------\n")

def A_interrup_timer():
    #Si se acabo el tiempo del timer volvemos a inicializarlo y reenviamos el ultimo paquete
    print(f'            {a.ultimo_paquete}')
    print("\n-------------------------------------------------------")
    print(f"SE ACABO EL TIEMPO ... PAQUETE REENVIADO")
    print("-------------------------------------------------------\n")
    a_capa_3(Entidad.ALICIA, a.ultimo_paquete)
    startimer(Entidad.ALICIA, 10)


def A_init():
    """
        Funcion que se encarga de inicializar a Alicia
    """
    return Alicia(estado='ESPERANDO_LLAMADA', ultimo_paquete=None)

def B_entrada(paquete):
    """
        Funcion que se encarga de manejar los paquetes que llegan a Bartolo
        :param paquete: paquete que llega a Bartolo  
    """
    global secuencia
    print("\n-------------------------------------------------------")
    print(f"RECIBIENDO PAQUETE DE ALICIA")
    print("-------------------------------------------------------\n")
    #Revisamos que el paquete halla llegado bien 
    if paquete.checksum == get_checksum(paquete.payload, paquete.num_ack, paquete.num_secuencia):
        #Revisamos que la secuencia del paquete sea la correcta(duplicado)
        if paquete.num_secuencia != secuencia:
            print("\n-------------------------------------------------------")
            print("SE RECIBIO UN PAQUETE CON SECUENCIA INCORRECTA ... MANDANDO ACK CON NUMERO DE SECUENCIA CONTRARIO")
            print("-------------------------------------------------------\n")
            #Si el numero de secuencia del paquete es incorrecto enviamos un ack con el numero de secuencia contrario
            num_nack=1 if paquete.num_ack ==0 else 0
            p_nack = Paquete(num_secuencia=paquete.num_secuencia, num_ack=num_nack, checksum=get_checksum(b' ', num_ack=num_nack, num_secuencia=paquete.num_secuencia), payload=b' ')
            a_capa_3(Entidad.BARTOLO, p_nack)
            return
        print("\n-------------------------------------------------------")    
        print(f"PAQUETE CORRECTO ...  MANDANDO ACK" )
        print("-------------------------------------------------------\n")
        #Si el paquete es correcto mandamos un mensaje de confirmacion ack
        p_ack = Paquete(num_secuencia=paquete.num_secuencia, num_ack=paquete.num_ack, checksum=get_checksum(b' ', num_ack=paquete.num_ack, num_secuencia=paquete.num_secuencia), payload=b' ')
        a_capa_3(Entidad.BARTOLO, p_ack)
        a_capa_5(Entidad.BARTOLO, Mensaje(paquete.payload))
    else:
        #Si el paquete esta corrupto mandamos un ack con el numero de secuencia contrario 
        print("\n-------------------------------------------------------")
        print("PAQUETE CORRUPTO ... MANDANDO ACK CON NUMERO DE SECUENCIA CONTRARIO")
        print("-------------------------------------------------------\n")
        num_nack=1 if paquete.num_ack ==0 else 0
        p_nack = Paquete(num_secuencia=paquete.num_secuencia, num_ack=num_nack, checksum=get_checksum(b' ', num_ack=num_nack, num_secuencia=paquete.num_secuencia), payload=b' ')
        a_capa_3(Entidad.BARTOLO, p_nack)
   

def B_init():
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
        if x < .75:
            mi_paquete.payload = b'#'+mi_paquete.payload[1:]
        elif x < 0.875:
            #random entre 0 y 255
            mi_paquete.num_secuencia = randint(0, 9)
        else:
            #random entre 0 y 255
            mi_paquete.num_ack = randint(0, 9)
        if verbose > 0:
            print('          A CAPA 3 > paquete corrompido')
    if verbose > 2:
        print('          A CAPA 3 > programando llegada del otro lado')
    agregar_evento(nuevo_evento)
    return None

def a_capa_5(entidad, mensaje):
    if verbose > 2:
        print(f'          A CAPA 5 > se recibieron los datos: {mensaje.datos.decode()}')


a= A_init()

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
