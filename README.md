# Scrapper Distribuido :computer:

## Autores 鉁掞笍

**Nombre(s) y Apellidos** | **Grupo** | **Correo**| **GitHub**
:-:|:-:|:-:|:-:
Reinaldo Barrera Travieso | C-411 | r.barrera@estudiantes.matcom.uh.cu| [@Reinaldo14](https://github.com/Reinaldo14) 
Ariel Plasencia D铆az | C-412 | a.plasencia@estudiantes.matcom.uh.cu| [@ArielXL](https://github.com/ArielXL) 

## Empezando 馃敡

### Implementaci贸n

El proyecto est谩 implementado en [python 3.6.8](https://docs.python.org/release/3.6.8/). Para una mejor y mayor comprensi贸n del c贸digo fuente propuesto entendemos que hay que tener profundos conocimientos acerca de python como lenguaje de programaci贸n. Nos apoyamos fundamentalmente en las librer铆as [threading](https://docs.python.org/es/3.6/library/threading.html), [socket](https://docs.python.org/es/3.6/library/socket.html), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) y [urllib](https://docs.python.org/es/3.6/library/urllib.html) para su implementaci贸n.

Para la instalaci贸n de las dependencias ejecutamos el siguiente comando:

```bash
pip install -r requirements.txt
```

### Ejecuci贸n

Para ejecutar nuestro proyecto de manera m谩s sencilla proveemos un [makefile](src/makefile) con varias opciones. A continuaci贸n mostramos la ayuda.

```bash
cd src/
make help
info                           Display project description
version                        Show the project version
server                         Run a server with default parameters
client                         Run a client with default parameters
install                        Install the project dependencies
clean                          Remove temporary files
help                           Show this help
```

Para personalizar los par谩metros de entrada consulte la documentaci贸n del fichero a ejecutar escribiendo las siguientes l铆neas:

```bash
cd src/
python server.py --help
python client.py --help
```

## Sobre el Scrapper Distribuido :spider_web:

### Chord

Chord es un protocolo de b煤squeda distribuida que se puede utilizar para compartir archivos peer to peer (p2p). Chord distribuye objetos a trav茅s de una red din谩mica de nodos e implementa un protocolo para encontrar estos objetos una vez que se han colocado en la red. La ubicaci贸n de los datos se implementa en la parte superior de Chord asociando una clave con cada elemento de datos y almacenando el par clave, elemento de datos en el nodo al que se asigna la clave. Cada nodo de esta red es un servidor capaz de buscar claves para aplicaciones clientes, pero tambi茅n participa como almac茅n de claves. Adem谩s, se  adapta de manera eficiente a medida que los nodos se unen y abandonan el sistema, y puede responder a consultas incluso si el sistema cambia continuamente. Por lo tanto, Chord es un sistema descentralizado en el que ning煤n nodo en particular es necesariamente un cuello de botella de rendimiento o un 煤nico punto de fallas.

#### Llaves

Cada clave insertada en la tabla de hash distribuida (DHT por sus siglas en ingl茅s) tiene un hash para que quepa en el espacio de claves admitido por la implementaci贸n particular de Chord. El espacio de claves, en esta implementaci贸n, reside entre 0 y 2**m-1, donde m = 100 (indicado por MAX_BITS en el c贸digo).

#### Anillos de Nodos

As铆 como cada clave que se inserta en el DHT tiene un valor hash, cada nodo del sistema tambi茅n tiene un valor hash en el espacio de claves del DHT. Para obtener este valor de hash, simplemente usamos el hash de la combinaci贸n ip:puerto, usando el mismo algoritmo de hash que usamos para las claves de hash insertadas en el DHT. Chord ordena el nodo de forma circular, en la que el sucesor de cada nodo es el nodo con el siguiente hash m谩s alto. El nodo con el hash m谩s grande, sin embargo, tiene el nodo con el
hash m谩s peque帽o como su sucesor. Es f谩cil imaginar los nodos colocados en un anillo, donde el sucesor de cada nodo es el nodo que le sigue cuando sigue una rotaci贸n en el sentido de las agujas del reloj.

### Eficiencia y Escalabilidad

Chord est谩 dise帽ado para ser altamente escalable, es decir, para que los cambios en las dimensiones de la red no afecten significativamente a su rendimiento. En particular, si n es el n煤mero de nodos de la red, su costo es proporcional a log(n). Es escalable porque solo depende del n煤mero de bits del que se compone un identificador. Si queremos m谩s nodos, simplemente asignamos identificadores m谩s largos. Es eficiente, porque hace b煤squedas en un orden log(n), ya que en cada salto, se puede reducir a la mitad el n煤mero de saltos que quedan por hacer.

### Resistencia a fallas

Chord admite la desconexi贸n o falla desinformada de los nodos al hacer ping continuamente a su nodo sucesor. Al detectar un nodo desconectado, el anillo de nodos se estabilizar谩 autom谩ticamente. Los archivos en la red tambi茅n se replican en el nodo sucesor, por lo que en caso de que un nodo falle, otro nodo se encarga de 茅l, este 煤ltimo nodo ser谩 redirigido a su sucesor.

### Web Scrapping

Web scrapping es una t茅cnica utilizada mediante programas de software para extraer informaci贸n de sitios web. Usualmente, estos programas simulan la navegaci贸n de un humano en la World Wide Web ya sea utilizando el protocolo HTTP manualmente, o incrustando un navegador en una aplicaci贸n. El web scrapping est谩 muy relacionado con la indexaci贸n de la web, la cual indexa la informaci贸n de la web utilizando un robot y es una t茅cnica universal adoptada por la mayor铆a de los motores de b煤squeda. Sin embargo, el web scrapping se enfoca m谩s en la transformaci贸n de datos sin estructura en la web (como el formato HTML) en datos estructurados que pueden ser almacenados y analizados en una base de datos central, en una hoja de c谩lculo o en alguna otra fuente de almacenamiento. Alguno de los usos del web scrapping son la comparaci贸n de precios en tiendas, la monitorizaci贸n de datos relacionados con el clima de cierta regi贸n y la detecci贸n de cambios y la integraci贸n de datos en sitios webs. En los 煤ltimos a帽os el web scrapping se ha convertido en una t茅cnica muy utilizada dentro del sector del posicionamiento web gracias a su capacidad de generar grandes cantidades de datos para crear contenidos de calidad.

En nuestro caso para esta funcionalidad utilizamos las librer铆as [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) y [urllib](https://docs.python.org/es/3.6/library/urllib.html) provistas por el lenguaje de programaci贸n python. Con ellas podemos extraer de manera sencilla el texto html de una determinada url, as铆 como sus fotos y dem谩s archivos relacionados. Cabe mencionar que el web scrapping se lleva a cabo por niveles de profundidad, variable especificada en la entrada del algoritmo.

### Sistema Distribuido

El sistema distribuido est谩 constituido por nodos los cuales tienen ciertas responsabilidades o roles. La existencia de un 煤nico rol para cada nodo no impide que dos nodos no puedan estar en un mismo hostname. El sistema est谩 disponible siempre que halla alg煤n nodo disponible (eso no implica que deba dar una respuesta r谩pida ante los pedidos). En caso de que alg煤n nodo abandone la red, ya sea tanto informada como desinformadamente,  no se pierden los datos, 茅stos son replicados por los restantes nodos existentes en la red. Tambi茅n es capaz de reconectarse y funcionar como un solo sistema cuando exista la posibilidad de comunicaci贸n entre los nodos de los subsistemas.

En nuestro proyecto cada nodo tiene las siguientes funcionalidades:

1. *Join network*: Se une a otro nodo seg煤n IP y PORT especificados.

2. *Leave network*: Deja la red de manera informada y replica los archivos que contiene el nodo.

3. *Print finger table*: Imprime la finger table del nodo.

4. *Print my predecessor and successor*: Imprime tanto el ID del nodo actual como su predecesor y sucesor.

5. *Print IP, PORT and LEVEL*: Imprime tanto el ID, IP, PORT y LEVEL (nivel de profundidad) del nodo actual.

6. *Print files on the network*: Imprime los archivos contenidos en el nodo.

7. *Make web scrapping*: Dada una url y un nivel de profundidad, se descargan todos los ficheros correspondientes a la url en la carpeta *src/downloads/urls/*  con la profundidad especificada y se sube el html principal hacia la red.

8. *Upload file*: Se sube un archivo determinado y replicado a varios nodos en la red.

9. *Download file*: Se descarga el archivo especificado en la direcci贸n *src/downloads/files/*.

## Un ejemplo completo :page_with_curl:

Con la idea de evidenciar el cumplimiento de los requisitos pedidos para nuestro proyectos mostramos varios ejemplos, en forma de videos, basados en un servidor y varios clientes, los cuales llevar谩n a cabo diferentes consultas al sistema distribuido de manera concurrente. Estos videostutoriales podemos encontrarlos en la ruta *doc/*.

## License 馃搫

Este proyecto se encuentra bajo los requerimientos de la licencia [LICENSE](LICENSE), la cual puede consultar para m谩s informaci贸n y detalles.

## Referencias :card_file_box:

Para la implementaci贸n del proyecto nos apoyamos fundamentalmente en algunas consultas hechas en la red de redes y en el documento [Chord: A Scalable Peer-to-peer Lookup Service for Internet Applications](doc/chord.pdf), este 煤ltimo nos sirvi贸 de gran ayuda para una mejor y mayor comprensi贸n e implementaci贸n del protocolo chord.
