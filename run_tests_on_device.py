import json
import subprocess
import os
import traceback
import sys
from report import load_json_data, get_log_dir, run_one_report, run_summary

RUN_ALL = True if sys.argv[1] == "True" else False
DEVICE = sys.argv[2]
TESTS = sys.argv[3].split(',')

json_file = os.path.join(os.getcwd(), 'logs', DEVICE.replace(".", "_").replace(':', '_'), 'data.json')


def run():
    try:
        results = load_json_data(DEVICE, TESTS, RUN_ALL)
        tasks = run_tests(results)

        for task in tasks:
            results['tests'][task['air']] = run_one_report(task['air'], DEVICE)
            results['tests'][task['air']]['status'] = task['status']

        json.dump(results, open(json_file, "w"), indent=4)
        run_summary(results, DEVICE)
    except Exception as e:
        traceback.print_exc()


def run_tests(results):
    """
        Run air tests sequentially on device
    """
    tasks = []
    for air in TESTS:
        if not RUN_ALL and results['tests'].get(air) and \
                results['tests'].get(air).get('status') == 0:
            print("Skip test %s" % air)
            continue

        log_dir = get_log_dir(air, DEVICE)
        cmd = [
            "airtest",
            "run",
            "tests/" + air,
            "--device",
            "Android:///" + DEVICE,
            "--log",
            log_dir
        ]

        try:
            tasks.append({
                'status': subprocess.Popen(cmd, cwd=os.getcwd()).wait(),
                'air': air
            })
        except Exception as e:
            traceback.print_exc()
    return tasks


if __name__ == '__main__':
    run()

