import argparse
import datetime
import hashlib
import random
import subprocess
import string

DEFAULT_DOKKU_COMMAND = "/usr/bin/dokku"
FILE_NAME_FORMAT = "{db_name}_{year}_{month}_{day}_{hash}"
FILE_EXTENSION = ".sql"
DESTINATION_PATH = "/Users/Colin/Desktop/backups/"

def backup():
    db_names = get_all_db_names()
    command = 'mysql:export {db_name}'
    now = datetime.datetime.now()
    print("Starting backup...")
    print("Dumping to {}".format(DESTINATION_PATH))
    print("Backing up dbs")
    for db_name in db_names:
        print("===> {}".format(db_name))
        random_chars  = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
        file_name = FILE_NAME_FORMAT.format(db_name=db_name, year=now.year,
                month=now.month, day=now.day, hash=random_chars)
        process = subprocess.run(args.dokku_command + [command.format(
            db_name=db_name)],
            stdout=subprocess.PIPE, check=False)
        dump = process.stdout.decode("utf-8")
        full_path = DESTINATION_PATH + file_name + FILE_EXTENSION
        with open(full_path, "w") as f:
            f.write(dump)
        print(file_name + FILE_EXTENSION)

def get_all_db_names():
    command = ['mysql:list']
    process = subprocess.run(args.dokku_command + command,
            stdout=subprocess.PIPE, check=False)
    rows = process.stdout.decode("utf-8").split('\n')
    db_names = [row.split(' ')[0]for row in rows[1:] if row.split(' ')[0]]
    return db_names
    
    
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
    print("valid")
    return dokku_command


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backup dokku-mysql instances to Google Cloud')
    parser.add_argument('--dokku-command', help='Dokku command to run (defaults to /usr/bin/dokku)', default='DEFAULT_DOKKU_COMMAND', type=is_valid_dokku)
    parser.add_argument('--dbs', type=str, help='Comma delimited db instance names to backup.')
    parser.add_argument('--debug', type=bool, help='Display additional debug information.')
    args = parser.parse_args()
    backup()

