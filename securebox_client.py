import argparse
import sys
from log import logger

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

    if not len(sys.argv) > 1:
        log.warning("No arguments specified! Finishing execution...")
        exit(0)
