# dokku-mysql-backup
Python script to backup all dokku mysql instances to Google Cloud.

Dokku Mysql Backup
==============

Setting up
----------

1. Install [Python 3.4 or above](https://www.python.org/downloads/) and
   [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
2. Clone this repository:

        git clone git@github.com:colinschoen/dokku-mysql-backup.git

    and change directories into the repository.

3. Create a virtualenv:

        virtualenv -p python3 env/

4. Activate the virtualenv:

        source env/bin/activate

5. Install all dependencies:

        pip install -r requirements.txt

> You only have to run through the setup process once. However, you **must run
> `source env/bin/activate` every time you work in the repo.** The command activates
> the tools we use to publish our website.
