import argparse
import sys
from securebox import *

# TODO: que hacemos con logging?
# TODO: este main en moodle se llama securebox_client.py, por si tienen tests automáticos habría que cambiarlo

if __name__ == '__main__':

    is_dest_id_required = '--upload' in sys.argv or '--encrypt' in sys.argv or 'enc_sign' in sys.argv
    is_source_id_required = '--download' in sys.argv or '--decrypt-and-verify' in sys.argv or '--verify' in sys.argv

    parser = argparse.ArgumentParser(description='SecureBox client')
    parser.add_argument('--log_level', choices=['debug', 'info', 'warning', 'error', 'critical'], default='info',
                        help='Indicate logging level. info by default')
    parser.add_argument('--log_file', action="store_true",
                        help='If present, log will be redirected to a file. Add file name if wanted, file.log by default')
    parser.add_argument('--log_config', action='store_true',
                        help='If present, log config will be loaded from logging.ini, ignoring other config specified through command line')
    parser.add_argument('--create_id', nargs=2, metavar=('name', 'email'),
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
    parser.add_argument('--source_id', metavar='id', required=is_source_id_required, help='Sender\'s ID.')
    parser.add_argument('--dest_id', metavar='id', required=is_dest_id_required, help='Receiver\'s ID.')
    parser.add_argument('--list_files', action='store_true', help='List all the files owned by the user.')
    parser.add_argument('--download', metavar='file_id', help='Downloads the file with the specified file_id')
    parser.add_argument('--delete_files', nargs='*', metavar='file_id', help='Deletes the files with the specified file_id\'s')
    parser.add_argument('--encrypt', metavar='file',
                        help='Encrypts a file so that it can be decrypted by the user whose id is specified by --dest_id.')
    parser.add_argument('--sign', metavar='file', help='Signs the file')
    parser.add_argument('--enc_sign', metavar='file', help='Encrypts and signs a file.')
    parser.add_argument('--decrypt-and-verify', metavar='file',
                        help='Decrypts a file sent by user whose id is specified by --source_id, verifying its signature')
    parser.add_argument('--verify', metavar='file', help='Verifies a file signed by the user specified in --source_id')
    parser.add_argument('--decrypt', metavar='file', help='Decrypts the file whose filename is provided')

    args = parser.parse_args()

    # Try to read the ini file to retrieve the token
    bundle = Bundle()
    if bundle.initialization_needed():
        logging.warning(f"File {Bundle.filename} not found... Creating ID...")

        token = input("Insert token: ")
        bundle.set_token(token)
        username = input("Insert username: ")
        email = input("Insert email: ")

        sb = SecureBoxClient(token)
        sb.create_id(bundle, username, email)
    else:
        token = bundle.get_token()
        sb = SecureBoxClient(token)

    if args.create_id:
        username, email = args.create_id
        sb.create_id(bundle, username, email)

    if args.search_id:
        query = args.search_id
        sb.search_id(query)

    if args.delete_id:
        user_id = bundle.get_user_id()
        sb.delete_id(user_id)

    if args.upload:
        filename = args.upload
        receiver_id = args.dest_id
        private_key = bundle.get_key()

        sb.upload(filename, receiver_id, private_key)

    if args.list_files:
        sb.list_files()

    if args.download:
        file_id = args.download
        sender_id = args.source_id
        private_key = bundle.get_key()

        sb.download(file_id, sender_id, private_key)

    if args.delete_files:
        files_id = args.delete_files
        sb.delete_files(*files_id)

    if args.encrypt:
        filename = args.encrypt
        receiver_id = args.dest_id

        sb.encrypt_helper(filename, receiver_id=receiver_id, to_disk=True)

    if args.sign:
        filename = args.sign
        private_key = bundle.get_key()

        sb.encrypt_helper(filename, private_key=private_key, to_disk=True)

    if args.enc_sign:
        filename = args.enc_sign
        receiver_id = args.dest_id
        private_key = bundle.get_key()

        sb.encrypt_helper(filename, private_key=private_key, receiver_id=receiver_id, to_disk=True)

    if args.decrypt:
        filename = args.decrypt
        private_key = bundle.get_key()

        sb.decrypt_helper(filename=filename, private_key=private_key)

    if args.decrypt_and_verify:
        filename = args.decrypt_and_verify
        sender_id = args.source_id
        private_key = bundle.get_key()

        sb.decrypt_helper(filename=filename, sender_id=sender_id, private_key=private_key)

    if args.verify:
        filename = args.verify
        sender_id = args.source_id

        sb.decrypt_helper(filename=filename, sender_id=sender_id)
