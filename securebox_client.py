import argparse
import sys
from log import logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SecureBox client', add_help=False)
    parser.add_argument('-h', '--help', action='help', help='muestra este mensaje de ayuda y finaliza')  # TODO: idioma
    parser.add_argument('--log_level', choices=['debug', 'info', 'warning', 'error', 'critical'], default='info',
                        help='Indica nivel de los logs. Por defecto, info.')
    parser.add_argument('--log_file', action="store_true",
                        help='Si se indica, los logs serán redireccionados a un fichero. Indique nombre de '
                             'fichero si quiere (log/file.log por defecto)')
    parser.add_argument('--log_config', action='store_true',
                        help='Si se indica, carga configuración del log desde log/logging.ini '
                             'e ignora el resto de parámetros especificados por línea de comandos')
    parser.add_argument('--create_id', nargs='*', metavar='nombre email [alias]',  # TODO: better idea??
                        help='Crea una nueva identidad (par de claves púlica y privada) '
                             'para un usuario con nombre nombre y correo email, y la registra en SecureBox, '
                             'para que pueda ser encontrada por otros usuarios. alias es una cadena identificativa opcional.')
    parser.add_argument('--search_id', metavar='cadena',
                        help='Busca un usuario cuyo nombre o correo electrónico contenga '
                             'cadena en el repositorio de identidades de SecureBox, y devuelve su ID.')
    parser.add_argument('--delete_id', metavar='id', type=int,
                        help='Borra la identidad con ID id registrada en el sistema. Sólo se pueden borrar '
                             'aquellas identidades creadas por el usuario que realiza la llamada.')
    parser.add_argument('--upload', metavar='fichero',
                        help='Envia un fichero a otro usuario, cuyo ID es especificado con la opción --dest_id. '
                             'Por defecto, el archivo se subirá a SecureBox firmado y cifrado con las claves adecuadas '
                             'para que pueda ser recuperado y verificado por el destinatario.')
    parser.add_argument('--source_id', metavar='id', type=int, help='ID del emisor del fichero.')
    parser.add_argument('--dest_id', metavar='id', type=int, help='ID del receptor del fichero.')
    parser.add_argument('--list_files', action='store_true', help='Lista todos los ficheros pertenecientes al usuario.')
    parser.add_argument('--download', metavar='id_fichero', type=int, help='Recupera un fichero con ID id_fichero del sistema')
    parser.add_argument('--delete_file', metavar='id_fichero', type=int, help='Borra un fichero del sistema.')
    parser.add_argument('--encrypt', metavar='fichero',
                        help='Cifra un fichero, de forma que puede ser descifrado '
                             'por otro usuario, cuyo ID es especificado con la opción --dest_id.')
    parser.add_argument('--sign', metavar='fichero', help='Firma un fichero.')
    parser.add_argument('--enc_sign', metavar='fichero', help='Cifra y firma un fichero, combinando funcionalmente las dos opciones anteriores.')

    args = parser.parse_args()

    log = logger.set_logger(args)

    if not len(sys.argv) > 1:
        log.warning("No arguments specified! Finishing execution...")
        exit(0)
    elif not 2 <= len(args.create_id) <= 3:
        log.error("create_id expects 2 arguments (or 3 if alias is present).")
        exit(1)
