import argparse
import subprocess

def backup():
    pass

def get_all_db_names():
    rows = subprocess.run(['dokku', 'mysql:list']).split('/n')

    db_names = [row.split(' ')[0]for row in rows[1:]]
    return db_names
    
    
def is_valid_dokku(dokku_command=None):
    """
    Checks whether dokku_command is a well defined path to an executable.

    args: 
        - dokku_command (optional): str Path to dokku command location
    returns:
        - bool Whether dokku_command is a valid dokku command
    """
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
    parser = argparse.ArgumentParser(description='Backup dokku-mysql instances to Google Cloud')
    parser.add_argument('--dokku-command', help='Dokku command to run (defaults to /usr/bin/dokku)', default='/usr/bin/dokku', type=is_valid_dokku)
    parser.add_argument('--dbs', type=str, help='Comma delimited db instance names to backup.')
    parser.add_argument('--debug', type=bool, help='Display additional debug information.')
    args = parser.parse_args()

