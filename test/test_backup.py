import subprocess
import argparse
import pytest
from backup import backup
from pytest_mock import mocker

class TestCass(object):
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
        

