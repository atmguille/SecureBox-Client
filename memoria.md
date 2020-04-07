# SecureBox Client 

## Introducción
Esta práctica ha consistido en el desarrollo de un cliente del servidor SecureBox en Python. TODO: esta frase no me acaba de salir bien: Este cliente ofrece al usuario una manera opaca de llevar a cabo las distintas tareas y se comunica internamente con SecureBox a través de diversos *endpoints* de la API facilitada.

## Organización del proyecto
Si bien esta práctica no ha requerido el mismo nivel de organización que la anterior, hemos intentado de nuevo tener una estructura simple y bien definida. Además, para evitar la instalación de paquetes relacionados con el proyecto en la máquina y que pudiera haber interferencias entre versiones, decidimos usar un *virtual environment*. Su configuración se ha detallado en el readme. Por otro lado, para facilitar el uso y la lectura del código, se han añadido los tipos esperados, tanto en argumentos como en el retorno de las funciones, en la medida de lo posible. Esto es lo que se conoce como *type hinting*, una característica introducida en Python 3.5.

Cabe mencionar que el código del proyecto se encuentra dividido en 4 ficheros:

- **api.py:** en este fichero se encuentra toda la funcionalidad para comunicarse con el servidor.
- **cryptography.py:** aquí se encuentra todo lo relacionado con la firma, cifrado y descifrado de mensajes.
- **securebox.py:** en este archivo están implementadas todas las funciones del cliente. Por ejemplo, aunque para firmar y cifrar un mensaje se use `cryptography.py`, es aquí donde está gestionado el abrir el fichero a cifrar, el manejo de excepciones, el guardado del fichero final o su envío al servidor de SecureBox, etc. En definitiva, este fichero de Python es el pegamento de los dos anteriores. Todos los mensajes mostrados al usuario (salvo los relacionados con los argumentos) se encuentran aquí.
- **main.py:** es el punto de entrada a la aplicación y es donde se gestionan los argumentos recibidos

## Decisiones de diseño
Se han realizado dos ligeras modificaciones con respecto a las especificaciones de Moodle:
- **delete_id**: en Moodle se especifica lo siguiente: "Borra la identidad con ID id registrada en el sistema. Obviamente, sólo se pueden borrar aquellas identidades creadas por el usuario que realiza la llamada." Realmente no acabamos de entender por qué es necesario pasarle un ID cuando sólo hay un ID por token. No obstante, para intentar tapar el fallo de diseño del servidor de cara al usuario final, decidimos guardar el ID en un fichero `bundle.ini`, junto al token y a la clave privada. Gracias a esto, no es necesario pasar un id a `--delete_id`.
- **delete_files**: inicialmente esta opción se llamaba `--delete_file`, pero la hemos mejorado para que pueda borrar un número indeterminado de ficheros. Es por esto que se llama `--delete_files`, en plural. Además, el borrado de ficheros se realiza de manera simultánea, haciendo uso de un *ThreadPoolExecutor*.

## API

Como todas las llamadas a la API del servidor necesitan incluir en su cabecera el token, y este token puede ser introducido de diversas formas (por ejemplo, por *stdin* o leyéndolo de un fichero) se nos ocurrieron varias formas de implementar esto. Una manera sería tener una variable global; otra, que cada función recibiera el token como argumento. Finalmente nos decantamos por hacer uso de la programación orientada a objetos, creando una clase API, cuyo constructor recibiera el token.
Por otro lado, cabe comentar la función `file_upload`. En un inicio, cuando queríamos subir un fichero al servidor, primero lo cifrábamos, depués lo guardábamos en disco para, acto seguido, leerlo de disco y subirlo. Esto se hacía así porque se debía subir un descriptor de fichero, y no los bytes del mensaje como tal. Como se puede observar, esto es totalmente ineficiente. Para evitar tener que guardar el fichero en disco, construimos un descriptor de fichero con los bytes en memoria a través de `io.BytesIO` y, para que el nombre se preserve, inicializamos su atributo *name*. Con ello, evitamos pasar por disco, tal y como queríamos.

## Cryptography

En cuanto al apartado relacionado con criptografía, usamos la librería `PyCryptoDome`. Esta no viene instalada por defecto y por ello se encuentra en `requirements.txt`. En líneas generales se ha seguido la documentación oficial de la librería para el desarrollo. En particular, se han tomado las siguientes decisiones de diseño:
- Se hace uso de la v1.5 al firmar con RSA. En un principio, habíamos optado por usar PSS, ya que es la versión más moderna. Investigando, vimos que la única diferencia es que esta versión ha sido desarrollada para permitir que los métodos modernos de análisis de seguridad demuestren que su seguridad se relaciona directamente con la del problema RSA. Sin embargo, como todos debemos usar el mismo método para ser compatibles, cambiamos a v1.5 en cuánto se nos indico,
- En cuanto al vector de inicialización (IV) que usa AES, se decidió al principio que la mejor opción era cifrarlo junto con la clave simétrica. La idea es dejar sin cifrar la menor cantidad de información posible, otorgándole la mínima ventaja al atacante. De esta forma, si el IV es también secreto, el atacante necesitaría descifrar otros 16 bytes extra, teniendo por tanto más seguridad. Para llevar esto acabo, simplemente concatenamos el IV a la clave simétrica antes de cifrarlo todo por RSA. El receptor, cuando descifre la clave simétrica, obtiene el IV de los 16 primeros bytes (siempre 16) y puede proceder a descifrar el mensaje completo con toda esta información. Sin embargo, de nuevo debemos ser compatibles con el resto de usuarios, por lo que no tiene sentido llevar a cabo esta estrategia si el resto implementa otra. Como se dicidió no cifrar el IV, se concatena al principio del mensaje a enviar, teniendo la siguiente estructura: `IV + encrypted symmetric key + encrypted message`.
- Para que las funciones puedan ser usadas con otras longitudes de clave, se permite especificar el número de bits. Por defecto se usa la longitud requerida para la práctica. También, suponemos que las longitudes de las claves son todas iguales, usando así `key.size_in_bytes()` para evitar hardcodear la longitud.
- En caso de que la firma no sea verídica, la función de la librería lanza una excepción de tipo `ValueError`. Nosotros hemos decidido crear una excepción específica (`SignatureNotAuthentic`) para que desde fuera se controle de una forma más *verbose*. TODO: está palabra tiene sentido aquí? jeje
- Por último, cabe mencionar la necesidad de usar funciones para ajustar el *padding* al tamaño del bloque de cifrado.

## SecureBox

## Main

