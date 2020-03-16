import argparse
import configparser

from crypto import *
from log import logger
from api.api import *

CONFIGURATION_FILE = "bundle.ini"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SecureBox client')
    parser.add_argument('--log_level', choices=['debug', 'info', 'warning', 'error', 'critical'], default='info',
                        help='Indicate logging level. info by default')
    parser.add_argument('--log_file', action="store_true",
                        help='If present, log will be redirected to a file. Add file name if wanted, file.log by default')
    parser.add_argument('--log_config', action='store_true',
                        help='If present, log config will be loaded from logging.ini, ignoring other config specified through command line')
    parser.add_argument('--create_id', nargs=2, metavar=('name', 'email'),  # TODO: alias
                        help='Creates a new identity (public and private key pair) for a user with name and email specified. '
                             'The user is then registered in SecureBox, so it can be found from other users')
    parser.add_argument('--search_id', metavar='string',
                        help='Looks for a user in SecureBox whose name or email contains the string specified, '
                             'returning its ID.')
    parser.add_argument('--delete_id', metavar='id',
                        help='Deletes the identity with the id specified. Please note that the user that creates '
                             'an identity is the only one allowed to delete it.')
    parser.add_argument('--upload', metavar='file',
                        help='Sends a file to another user, whose ID is specified in --dest_id. '
                             'By default, the file will be uploaded to SecureBox signed and encrypted with the appropiate keys '
                             'so the receiver is able to decrypt and verify it.')
    parser.add_argument('--source_id', metavar='id', help='Sender\'s ID.')
    parser.add_argument('--dest_id', metavar='id', help='Receiver\'s ID.')
    parser.add_argument('--list_files', action='store_true', help='List all the files owned by the user.')
    parser.add_argument('--download', metavar='file_id', help='Downloads the file with the specified file_id')
    parser.add_argument('--delete_file', metavar='file_id', help='Deletes the file with the specified file_id')
    parser.add_argument('--encrypt', metavar='file',
                        help='Encrypts a file so that it can be decrypted by the user whose id is specified by --dest_id.')
    parser.add_argument('--sign', metavar='file', help='Signs the file')
    parser.add_argument('--enc_sign', metavar='file', help='Encrypts and signs a file.')

    args = parser.parse_args()

    log = logger.set_logger(args)

    # Try to read the configuration file
    config = configparser.ConfigParser()
    try:
        with open(CONFIGURATION_FILE) as f:
            config.read_file(f)
    except IOError as e:
        log.warning(f"File {CONFIGURATION_FILE} not found, creating one...")
        print("Insert token: ")
        token = input()
        print("Insert username: ")
        username = input()
        print("Insert email: ")
        email = input()

        api = API(token)

    exit(0)

    if args.create_id:
        log.info(f"Creating a new identity")

        username, email = args.create_id
        key = rsa_generate_key()

        user = user_register(username, email, get_public_key(key))
        ts = user["ts"]

        log.info(f"Done, looking for our user ID")
        users = user_search(email)
        user_at_server = min(users, key=lambda u: abs(float(u["ts"]) - ts))

        user_id = user_at_server["userID"]

        save_key(key, user_id)

    if args.search_id:
        log.info(f"Searching {args.search_id}...")
        for user in user_search(args.search_id):
            log.info(user)

    if args.delete_id:
        log.info(f"Deleting {args.delete_id}...")
        user_delete(args.delete_id)
        # TODO: la API no nos dice si existe o no existe

    if args.upload:
        filename = args.upload
        source_id = args.source_id
        destination_id = args.dest_id

        with open(filename, "rb") as file:
            message = file.read()

            # Sign message using our private key
            local_key = load_key(source_id)
            signature = sign_message(message, local_key)

            # Encrypt signed message using the remote public key
            remote_key = user_get_public_key(destination_id)
            encrypted_message = encrypt_message(signature + message, remote_key)

            file_id = file_upload(filename, encrypted_message)
            log.info(f"Successfully signed, crypted and uploaded file {filename} which got ID {file_id}")

    if args.list_files:
        log.info("Looking for files...")
        for file in file_list():
            log.info(f"FileID: {file['fileID']}. Filename: {file['fileName']}")

    if args.download:
        file_id = args.download
        # TODO: si no meten source_id, que no se verifique la firma
        source_id = args.source_id
        destination_id = args.dest_id

        # Retrieve encrypted and signed file from server
        encrypted_message, filename = file_download(file_id)
        # Get local private key to decrypt the message
        private_key = load_key(destination_id)
        signed_message = decrypt_message(encrypted_message, private_key)

        # Check signature, retrieving the public key of the sender first
        public_key = user_get_public_key(source_id)
        message = verify_signature(signed_message, public_key)

        with open(filename, "wb") as file:
            file.write(message)

        log.info(f"File {filename} downloaded, decrypted and verified successfully")

    if args.delete_file:
        log.info(f"Deleting file {args.delete_file}...")
        log.info(f"Correctly deleted file {file_delete(args.delete_file)}")

    if args.encrypt:
        filename = args.encrypt
        receiver_id = args.dest_id
        receiver_public_key = user_get_public_key(receiver_id)

        with open(filename, "rb") as file:
            message = file.read()
            encrypted_message = encrypt_message(message, receiver_public_key)

            with open(filename + ".crypt", "wb") as encrypted_file:
                encrypted_file.write(encrypted_message)

    if args.sign:
        filename = args.sign
        source_id = args.source_id  # TODO: without id

        with open(filename, "rb") as file:
            message = file.read()

            # Sign message using our private key
            local_key = load_key(source_id)
            signature = sign_message(message, local_key)

            # Save signed message
            with open(filename + ".crypt", "wb") as signed_file:  # TODO: extension .crypt si solo está firmado?
                signed_file.write(signature + message)

    if args.enc_sign:
        # TODO
        pass