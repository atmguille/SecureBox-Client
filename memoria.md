# SecureBox Client 

## Introducción
Esta práctica ha consistido en el desarrollo de un cliente del servidor SecureBox en Python. Éste implementa las distintas funcionalidades requeridas, comunicándose con el servidor a través de los diversos endpoints de la API

## Organización del proyecto
Si bien esta práctica no ha requerido el mismo nivel de organización que la anterior, hemos intentado de nuevo tener una estructura simple y bien definida. Además, para evitar la instalación de paquetes relacionados con el proyecto en la máquina y que pudiera haber interferencias entre versiones, decidimos usar un *virtual environment*. Su configuración se ha detallado en el readme. Por otro lado, para facilitar el uso y la lectura del código, se han añadido los tipos esperados, tanto en argumentos como en el retorno de las funciones, en la medida de lo posible. Esto es lo que se conoce como *type hinting*, una característica introducida en Python 3.5.

Cabe mencionar que el código del proyecto se encuentra dividido en 5 ficheros:

- **api.py:** en este fichero se encuentra toda la funcionalidad para comunicarse con el servidor.
- **cryptography.py:** aquí se encuentra todo lo relacionado con la firma, cifrado y descifrado de mensajes.
- **securebox.py:** en este archivo están implementadas todas las funciones del cliente. Por ejemplo, aunque para firmar y cifrar un mensaje se use `cryptography.py`, es aquí donde está gestionado el abrir el fichero a cifrar, el manejo de excepciones, el guardado del fichero final o su envío al servidor de SecureBox, etc. En definitiva, este fichero de Python es el pegamento de los dos anteriores. Todos los mensajes mostrados al usuario (salvo los relacionados con los argumentos o que con el *bundle*) se encuentran aquí.
- **bundle.py:** gestiona el archivo de configuración, el cual contiene el token, el ID y la clave privada del usuario.
- **main.py:** es el punto de entrada a la aplicación y es donde se gestionan los argumentos recibidos.

Además, como **api.py**, **cryptography.py** y **bundle.py** tienen excepciones propias, hemos decidido separarlas unas de otras y crear directorios específicos que agrupen el código y las excepciones.

## Decisiones de diseño
Se han realizado dos ligeras modificaciones con respecto a las especificaciones de Moodle:
- **delete_id**: en Moodle se especifica lo siguiente: "Borra la identidad con ID id registrada en el sistema. Obviamente, sólo se pueden borrar aquellas identidades creadas por el usuario que realiza la llamada." Realmente no acabamos de entender por qué es necesario pasarle un ID cuando sólo hay un ID por token. No obstante, para intentar tapar el fallo de diseño del servidor de cara al usuario final, decidimos guardar el ID en un fichero `bundle.ini`, junto al token y a la clave privada. Gracias a esto, no es necesario pasar un id a `--delete_id`.
- **delete_files**: inicialmente esta opción se llamaba `--delete_file`, pero la hemos mejorado para que pueda borrar un número indeterminado de ficheros. Es por esto que se llama `--delete_files`, en plural. Además, el borrado de ficheros se realiza de manera simultánea, haciendo uso de un *ThreadPoolExecutor*.

Además, el punto de entrada a la aplicación pasa a llamarse **main.py** para evitar confusiones con **securebox.py**, que contiene toda la funcionalidad del cliente.
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

Una vez más empleamos programación orientada objetos. La clase `SecureBoxClient` recibe un *token* que sirve para crear un atributo `API` para permitir la comunicación con el servidor. En este fichero están implementadas todas las funcionalidades requeridas. Cabe mencionar `delete_files`.

```python
def delete_files(self, *files_id: str):
    if "all" in files_id:
        files_id = [file["fileID"] for file in self.api.file_list()]
        with ThreadPoolExecutor(max_workers=len(files_id)) as pool:
            for file_id in files_id:
                print(f"Deleting file {file_id}...")
                pool.submit(self.api.file_delete, file_id)
```

Como hemos comentado antes, se puede borrar un número indeterminado de ficheros, lo cual se hará de manera paralela usando un *ThreadPoolExecutor*. Además, se puede usar `delete_files("all")` para borrar todos los ficheros subidos por el usuario. Hemos implementado además dos funciones sumamente útiles: `encrypt_helper` y `decrypt_helper`.

### encrypt_helper

```python
def encrypt_helper(self, filename: str, private_key: RsaKey = None, receiver_id: str = None,
                       to_disk: bool = False) -> bytes:
```

Esta función la creamos para unificar la funcionalidad de cifrar y/o firmar en local con la de enviar archivos a SecureBox. Siempre recibe el nombre del fichero a firmar y/o cifrar. Si recibe un clave privada RSA el fichero se firmará. Si recibe un ID, se cifrará el fichero (firmado, en el caso de que se haya proporcionado una clave privada RSA) con la clave pública del usuario. Por último, hay un argumento `to_disk`, en caso de estar a *True* se guardará el fichero firmado y/o cifrado en disco (con extensiones `.signed` y `.crypt`, respectivamente).

### decrypt_helper

```python
def decrypt_helper(self, filename: str = None, file_id: str = None, sender_id: str = None, 
                       private_key: RsaKey = None) -> None:

```

De igual manera creamos esta función para unificar la funcionalidad de descifrar y/o verificar la firma en local con la de descargar archivos de SecureBox. Recibe o la ruta de un fichero o el ID de un fichero almacenado en el servidor de SecureBox. Si recibe un ID de emisor tratará de verificar la firma usando la clave pública del usuario que envió el fichero. Si recibe una clave privada se descifrará el fichero haciendo uso de dicha clave. Además, para mayor velocidad si se ha de descargar un fichero de SecureBox y verificar la firma, se realizará de manera paralela la descarga de la clave pública del emisor.

## Bundle

La clase Bundle, implementada en el fichero del mismo nombre gestiona el archivo de configuración de nuestro cliente, el cual contiene el ID, el token y la clave privada del usuario. Se hace uso de la librería configparser para leer un archivo con un formato similar al siguiente:

```ini
[SecureBox]
token = <TOKEN DEL USUARIO>
key = -----BEGIN RSA PRIVATE KEY-----
      MIICXAIBAAKBgQDVtiJhzUYhnXUY9BCcTMXZSaiUsA8GYWHVFf+j3+wyM2volQ0/
      geRSiUykYC33C+jnelX50NMtzPinVHHwBGr+brCbvEe9B4mdQKAQdoX9+Xjrdi6Q
      ZrtR6Y5/TCXeTD3UOMTbLa0wPI8+ZATJ4JVZRlbD6lVRHHIc2WXFUm8SdQIDAQAB
      AoGAUkNwyqrkow3kRD22oyOeSPzkio+WyQL1ULvOErugRNasY/P0DI0oYWj+eouX
      RfBsr6XUsHvkvk2XLXoA/b4FnMSynK65bkbqh63UuHta4gjWpzjQIKhL6055RnQW
      O27I/vW3PkYpZt6OZeDm916CGANplh5x4i9/FSfVrj5UTkECQQDzRL2hP9GjQpYZ
      nHWmPVwkHfKSUUQF9isoeT4jqEAB4iSXFIyIxR/FKQP/A082Zno2o/dCPnJgmk3z
      i4/FpdcFAkEA4OVk/MygJE6sYuR8/QBqgpe039o9M+FbNvRi6AEWtGtQ/EbMzvE1
      DMNPW2MefKpN+OZ3iTrMFppLoEKRptxIsQJBAOna5hSR/hxc0WBzeOHDUMVjiKHB
      v4ufluOEkgjDICzvUU9vMJ32KdFl2XKXotlf8BKA0xv6Xgehrlf2jNJq12UCQEr4
      TYT0VcIks9S3pG7Wr6rfFb21y8c6raSRLVN34XC9gZ7Hn0ixIeUiSpcFYMlgIGQD
      t/94KUazothGuLUuI9ECQGzfwCA9+6seKLwFhXMuQ+b+peOkxTAlzy3PMGuI+sia
      oLNl27bvUA6ZCnJK7fG8P81yXbd8hgUeF/H4G4MQFZs=
      -----END RSA PRIVATE KEY-----
user_id = <ID DEL USUARIO>


```

Así, toda la información está en un sólo fichero que se lee al correr el cliente. De no existir un este fichero, se preguntaría  por pantalla el token, el nombre de usuario y el email y se llamaría automáticamente a la función `create_id`. Esta función generará una clave privada para el usuario y usará la API para registrarle en el servidor, obteniendo su ID.

Además, para añadir un extra de seguridad pensamos en cifrar el bundle usando AES. Cuando se crea éste, se solicita una contraseña para cifrarlo, usando la función `getpass`, que no muestra la contraseña al introducirla. Si no se proporciona una (es decir, si la contraseña es vacía) no se cifrará. De ser cifrada, cada vez que el usuario quiera usar el cliente usando su bundle tendrá que introducirla. 

## Main
Como se ha comentado antes, es el punto de entrada a la aplicación y el que el cliente debe ejecutar para tener acceso a toda la funcionalidad. Desde aquí se realiza toda la gestión de argumentos apoyándonos en la librería `argparse`, para después llamar a los distintos métodos de **securebox.py**. En relación al control de argumentos, pueden llamar la atención las dos primeras líneas de la función `main`. Estas sirven para detectar de una forma más limpia y a través del argumento *required* de `argparse` cuándo determinados argumentos son necesarios, evitando tener que hacer comprobaciones externas. Por otro lado, para evitar hacer un try except sobre una zona de código demasiado amplia, se crea la función `main`.

## Conclusión
Es cierto que esta práctica ha supuesto un coste menor de desarrollo con respecto a la anterior, dado que ha sido necesaria una estructura más sencilla, al uso de librerías externas y de un lenguaje de programación de más alto nivel como `Python`. Sin embargo, ha permitido observar desde más cerca el proceso de cifrado y familiarizarse con el uso de una *API* y las distintas formas de llamar a sus métodos. También, nos hemos dado cuenta de lo necesario que es llegar a un consenso a la hora de desarrollar, ya que de no haber sido así, no seríamos compatibles entre nosotros y el servicio no serviría para nada, como pasó en un inicio.
