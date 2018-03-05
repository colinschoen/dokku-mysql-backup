import subprocess
import argparse
import os
import json
import pytest
from backup import backup
from pytest_mock import mocker

TEST_ASSETS_DIR = "test/assets/"

class TestCass(object):

    def test_write_local_file(self, tmpdir):
        dump = "test sql dump"
        f = tmpdir.join("test.sql")
        backup.write_local_file(dump, f)
        assert f.read() == dump

    def test_sanitize_dbs(self, mocker):
        valid_dbs = [
                'test1',
                'test2'
                ]
        mock_get_all_db_names = mocker.patch.object(
                backup,
                'get_all_db_names',
                autospec=True)
        mock_get_all_db_names.return_value = valid_dbs
        backup.get_all_db_names = mock_get_all_db_names
        # Try with 1 valid DB name
        valid_db = valid_dbs[0]
        assert backup.sanitize_dbs(valid_db) == [valid_db]
        # Try with 1 valid, 1 invalid DB name
        # Should be getting an argument type error
        invalid_db = 'bad'
        with pytest.raises(argparse.ArgumentTypeError):
            backup.sanitize_dbs('{},{}'.format(valid_db, invalid_db))

    def test_is_valid_storage_provider(self):
        assert len(backup.STORAGE_PROVIDERS) > 0, 'There should be 1 or more provider'
        # Use a valid provider
        test_provider = backup.STORAGE_PROVIDERS[0]
        assert backup.is_valid_storage_provider(test_provider)
        # Use an invalid provider
        bad_test_provider = "bad-provider"
        # Should be getting an argument type error
        with pytest.raises(argparse.ArgumentTypeError):
            backup.is_valid_storage_provider(bad_test_provider)
        

    def test_is_valid_dokku(self, mocker):
        mock_subprocess_run = mocker.patch.object(subprocess, 'run', autospec=True)
        mock_completed_process = mocker.patch.object(subprocess, 'CompletedProcess', autospec=True)
        mock_completed_process.returncode = 0
        mock_subprocess_run.return_value = mock_completed_process
        backup.subprocess.run = mock_subprocess_run
        cmd = 'usr/bin/dokku'
        dokku_command = backup.is_valid_dokku(dokku_command=cmd)
        assert dokku_command == [cmd]
        mock_subprocess_run.assert_called_with(dokku_command + ['version'],
                check=mocker.ANY, stdout=mocker.ANY)
        # Change return code to nonzero
        mock_completed_process.returncode = 1
        # Should be getting an argument type error
        with pytest.raises(argparse.ArgumentTypeError):
            dokku_command = backup.is_valid_dokku(dokku_command="bad")
        
    def test_get_all_db_names(self, mocker):
        mock_subprocess_run = mocker.patch.object(subprocess, 'run', autospec=True)
        mock_completed_process = mocker.patch.object(subprocess, 'CompletedProcess', autospec=True)
        # Use a cached output for the mysql:list command
        with open(os.path.join(TEST_ASSETS_DIR, 'db_list_raw.txt'), 'rb') as f:
            contents = f.read()
            mock_completed_process.stdout = contents
            mock_subprocess_run.return_value = mock_completed_process
        # Use cached json list of db name
        with open(os.path.join(TEST_ASSETS_DIR, 'db_list.json')) as f:
            db_list = json.load(f)
        cmd = ['usr/bin/dokku']
        sub_command = ['mysql:list']
        backup_db_list = backup.get_all_db_names(dokku_command=cmd)
        assert backup_db_list == db_list
        mock_subprocess_run.assert_called_with(cmd + sub_command,
            check=mocker.ANY, stdout=mocker.ANY)
