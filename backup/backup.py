import argparse
import configargparse
import datetime
import hashlib
import os
import random
import subprocess
import string
import functools

from google.cloud import storage

DEFAULT_DOKKU_COMMAND = "/usr/bin/dokku"
STORAGE_PROVIDERS = [
        'local' # Backup to local machine
        'gcs' # Google Cloud Storage
        ]
FILE_NAME_FORMAT = "{db_name}_{year}_{month}_{day}_{hash}"
FILE_EXTENSION = ".sql"

def gcs_upload(bucket_id, f, dest_path):
    storage_client = storage.Client()

    

def backup():
    command = 'mysql:export {db_name}'
    now = datetime.datetime.now()
    print("Starting backup...")
    print("Dumping to {}".format(args.backup_dir))
    print("Backing up dbs")
    for db_name in args.dbs:
        print("===> {}".format(db_name))
        random_chars  = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
        file_name = FILE_NAME_FORMAT.format(db_name=db_name, year=now.year,
                month=now.month, day=now.day, hash=random_chars)
        process = subprocess.run(args.dokku_command + [command.format(
            db_name=db_name)],
            stdout=subprocess.PIPE, check=False)
        dump = process.stdout.decode("utf-8")
        full_path = os.path.join(args.backup_dir, file_name + FILE_EXTENSION)
        if args.storage_method == 'gcs':
            gcs_upload("bid", dump, full_path)
        else:
            write_local_file(dump, full_path)
        print(file_name + FILE_EXTENSION)
    print("{} databases backed up. Backup complete.".format(len(args.dbs)))

def write_local_file(dump, path):
    with open(path, "w") as f:
        f.write(dump)


def sanitize_dbs(db_names=None):
    db_names = db_names or args.dbs
    if type(db_names) is str:
        db_names = db_names.split(',')
    valid_db_names = get_all_db_names()
    for db_name in db_names:
        if db_name not in valid_db_names:
            raise argparse.ArgumentTypeError(msg)
    return db_names


@functools.lru_cache(maxsize=32)
def get_all_db_names():
    command = ['mysql:list']
    process = subprocess.run(args.dokku_command + command,
            stdout=subprocess.PIPE, check=False)
    rows = process.stdout.decode("utf-8").split('\n')
    db_names = [row.split(' ')[0]for row in rows[1:] if row.split(' ')[0]]
    return db_names
    
def is_valid_dir(destination_directory=None):
    destination_directory = destination_directory or args.backup_dir
    msg = "Invalid backup destination directory. Check it exists"
    if not os.path.exists(destination_directory):
        raise argparse.ArgumentTypeError(msg)
    return destination_directory


def is_valid_dokku(dokku_command=None):
    """
    Checks whether dokku_command is a well defined path to an executable.

    args: 
        - dokku_command (optional): str Path to dokku command location
    returns:
        - bool Whether dokku_command is a valid dokku command
    """
    print("Verifying dokku...", end=" ")
    dokku_command = dokku_command or args.dokku_command
    dokku_command = dokku_command.split(' ')
    msg = 'Invalid dokku-command path.'
    try:
        process = subprocess.run(dokku_command + ['version'],
            stdout=subprocess.PIPE, check=False)
    except Exception as e:
        raise argparse.ArgumentTypeError(msg)
    if process.returncode:
        raise argparse.ArgumentTypeError(msg)
    return dokku_command


if __name__ == "__main__":
    conf_parser = configargparse.ArgParser(
            default_config_files=['backup.cfg'],
            description='Backup dokku-mysql instances.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False
            )
    conf_parser.add('-c', '--config', is_config_file=True, dest='config_file', default='backup.cfg', type=str, help='Config file path')
    conf_parser.add('--dokku-command', help='Dokku command to run (defaults to /usr/bin/dokku)', default='DEFAULT_DOKKU_COMMAND', type=is_valid_dokku)
    conf_parser.add_argument('--dbs', type=str, help='Comma delimited db instance names to backup.')
    conf_parser.add('--backup-dir', type=is_valid_dir, default=os.getcwd(), help='The directory to place db dumps in.')
    conf_parser.add('--gcloud-key-file', type=str, help='Path to Google Cloud .json key file.')
    conf_parser.add('--gcloud-project-id', type=str, help='Path to Google Cloud .json key file.')
    conf_parser.add('--storage-method', type=lambda sp: sp in STORAGE_PROVIDERS, help='An external storage provider to upload database dumps to. ({})'.format(STORAGE_PROVIDERS), default='local')
    conf_parser.add('--debug', type=bool, help='Display additional debug information.')

    args = conf_parser.parse_args()

    # Handle some defaults specially since they require dokku-command to validate
    args.dbs = args.dbs or get_all_db_names()
    args.dbs = sanitize_dbs()

    backup()

