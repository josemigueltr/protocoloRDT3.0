#  Implementacion delprotocoloRDT 3.0
#   Redes de computadoras 2022-1

Integereantes:
- Ariana de Belen Fernandez Montenegro 
- José Miguel Toledo Reyes

NOTA: Se realizaron algunos cambios en el codigo que se nos proporciono para su correcto funcionamiento,entre los cambios mas destacados que podemos mencionar se encuentran los siguientes:

En la parte del codigo la cual se encarga de corromper el paquete que se esta enviando en las lineas las cuales se encargan de modificar el numero de secuencia y el numero de ack del paquete cambiamos las lineas las cuales indicaban que dichos valores serian iguales a 999999 por las siguientes:

(Numero de secuencia)
Antes:
```mi_paquete.seqnum = 999999```

Despues:

```mi_paquete.num_secuencia = randint(0, 9)```

(Numero de ack)

Antes:

```mi_paquete.num_ack = 999999```

Despues:

```mi_paquete.num_ack = randint(0, 9)```


Decidimos cambiar el valor que se le asignaba al numero de ack y de secuencia  por un valor aleatorio entre 0-9 para que funcionara de una mejor manera el simulador.  


De igual manera en las ejecuciones que se realizaron como se nos indico que  asginaramos un valor de verbose=2 ,proba_perdida = 0.3 y proba_corrup = 0.2  llegamos a notar que algunas veces en la impresion de la informacion llegaba a haber algunos errores especificamente con la informacion del paquete , llego a cocurrir que  no se imprimia la informacion del paquete , si no que solo se mostraba la pabra NONE y esto se lo atribuimos a que
cuando se  crea un nuevo evento  el indica que se mandara un envio o entrega  este se ejecuta antes de que llegue el paquete o se cree , es por eso que se utiliza la informacion de un paquete vacio y por ende  cuasndo se imprime el mensaje se muestra un mensaje que dice NONE

# Ejecuciones

Para mostrar las 3 simulaciones que se nos pidieron documentar, se anexan 3 archivos pdf los cuales contienen la informacion sobre cada una de esas  3 ejecuciones que se realizaron, de igual manera en cada uno de esos pedf se muestran con una simbologia de colores las confirmaciones de mensajes , las perdidas y como es que nuestro protocolo se recupera ante dichas perdidas.

Cabe resaltar que en las ejecuciones se puede ver claramente por medio de unos mensajes que icluimos cuando es que un mensaje se envia, cuando es que los paquetes que se quieren enviar son ignorados porque se esta esperando un mensaje de confirmacion ACK,cuando es que  el receptro recibe un mensaje corrupto y manda un mensaje ACK con el numero de secuencia invertido y de igual manera cuando es que el emisor recibe un paquete ack con el numero de secuencia invertido y decide esperar a que se agote el tiempo para reenviar el mensaje.\\

NOTA: Cuando  el receptor recibe un mensaje corrupto mandara un mensaje ACK con el numero de secuencia contrario, para indicar que ha ocurrido un error al recibir el paquete, es decir si el  paquete corrupto corresponde al numero de secuencia 0 entonces su numero de ack el cual tiene el mismo valor que le numero de secuencia se cambiara por el contrario a este para que  cuando se envien y se reciba del lado del emisor lo pueda detectar como un paquete que indica un error y por ende reenvie el ultimo paquete.





























