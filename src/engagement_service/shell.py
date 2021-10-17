import sys
import subprocess


def async_cmd(cmd):
    print(f"$ {cmd} &")
    try:
        subprocess.Popen(
            [cmd],
            shell=True,
            stdin=None,
            stdout=None,
            stderr=None,
            close_fds=True
        )
    except:
        _error('async_cmd', sys.exc_info()[0])


def cmd(cmd):
    print(f"$ {cmd}")
    try:
        subprocess.run(cmd)
    except:
        _error('cmd', sys.exc_info()[0])


def _error(method, error):
    print(f"shell error: {method} failed: ", error)
