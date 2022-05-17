import subprocess
from airtest.core.android.adb import ADB
import os


def run_on_multi_device(run_all=True):
    """
        run_all
            = True: run test fully;
            = False: continue test with the progress in data.json.
    """
    tasks = []
    for dev in devices:
        tasks = []
        cmd = [
            "python",
            "run_tests_on_device.py",
            str(run_all),
            dev,
            tests
        ]
        tasks.append({
            'process': subprocess.Popen(cmd, cwd=os.getcwd()),
            'dev': dev
        })
    for task in tasks:
        task['process'].wait()


if __name__ == '__main__':
    tests = "test_001.air,test_002.air"
    devices = [tmp[0] for tmp in ADB().devices()]
    run_on_multi_device(True)
