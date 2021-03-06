import json
import shutil
import subprocess
import os
import time
import traceback
import webbrowser

from jinja2 import Environment, FileSystemLoader


def load_json_data(dev, tests, run_all):
    """
        Loading data
        if data.json exists and run_all=False:
            loading progress in data.json
        else:
            return an empty data
    """
    json_file = os.path.join(os.getcwd(), 'logs', dev.replace(".", "_").replace(':', '_'), 'data.json')

    if not run_all and os.path.isfile(json_file):
        data = json.load(open(json_file))
        check_log_dir_for_folders_about_which_no_info(data, tests, dev)
        data = check_log_dir_for_missing_folder(data, dev)
        data['start'] = time.time()
        return data
    else:
        clear_log_dir(tests, dev)
        return {
            'start': time.time(),
            'device': dev,
            'tests': {}
        }


def run_one_report(air, dev):
    """"
        Build one test report for one air script
    """
    try:
        log_dir = get_log_dir(air, dev)
        log = os.path.join(log_dir, 'log.txt')
        if os.path.isfile(log):
            cmd = [
                "airtest",
                "report",
                "tests/" + air,
                "--log_root",
                log_dir,
                "--outfile",
                os.path.join(log_dir, 'log.html'),
                "--lang",
                "en"
            ]
            subprocess.call(cmd, cwd=os.getcwd())

            return {
                'path': os.path.join(log_dir, 'log.html')
            }
        else:
            print("Report build Failed. File not found in dir %s" % log)
    except Exception as e:
        traceback.print_exc()

    return {'status': -1, 'path': ''}


def run_summary(data, dev):
    """
        Build summary test report
    """
    try:
        summary = {
            'time': "%.3f" % (time.time() - data['start']),
            'success': [item['status'] for item in data['tests'].values()].count(0),
            'count': len(data['tests'])
        }
        summary.update(data)
        summary['start'] = time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(data['start']))
        env = Environment(loader=FileSystemLoader(os.getcwd()),
                          trim_blocks=True)
        html = env.get_template('report_tpl.html').render(data=summary)
        report_dir = os.path.join(os.getcwd(), 'logs', dev.replace(".", "_").replace(':', '_'), 'report.html')
        with open(report_dir, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open(report_dir)
    except Exception as e:
        traceback.print_exc()


def check_log_dir_for_folders_about_which_no_info(data, tests, dev):
    """
        Check log directory for folders about which there is no information
        if folder log test exists and data.json has no information about it:
            delete log test dir
    """
    temp_list = tests.copy() # ?????????? ?????????????? ?????????? ??????????????????

    for air in data['tests']:
        if air in temp_list:
            temp_list.remove(air)

    clear_log_dir(temp_list, dev)


def check_log_dir_for_missing_folder(data, dev):
    """
        Check log directory for missing folders
        if information about test exists in data.json and log air folder empty:
            delete test information in data.json
    """
    temp_list = []
    temp_data = data.copy()

    for air in temp_data['tests']:
        log_dir = os.path.join(os.getcwd(), 'logs', dev.replace(".", "_").replace(':', '_'), air)
        if not os.path.exists(log_dir):
            temp_list.append(air)

    for air in temp_list:
        temp_data['tests'].pop(air)

    return temp_data


def clear_log_dir(tests, dev):
    """
        Remove folder logs/*device_name*/*test_name*
    """
    for air in tests:
        log_dir = os.path.join(os.getcwd(), 'logs', dev.replace(".", "_").replace(':', '_'), air)
        if os.path.exists(log_dir):
            shutil.rmtree(log_dir)


def get_log_dir(air, dev):
    """
        Create logs folder logs/*device_name*/*test_name*
    """
    log_dir = os.path.join(os.getcwd(), 'logs', dev.replace(".", "_").replace(':', '_'), air)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir
