import json
import sys
from argparse import ArgumentParser
from tabulate import tabulate

arg_parser = ArgumentParser(
    description='Log parser for analyzing log files and generating reports.'
)

arg_parser.add_argument(
    '--file',
    dest='file',
    nargs='+',
    required=True,
    help='Path(s) to one or more log files to be parsed. '
         'Syntax: --file <file1> <file2>...'
)

arg_parser.add_argument(
    '--report',
    dest='report',
    required=False,
    help='Optional: name of the report file to save the results. If not specified, '
         'the report omly will be printed to the console. Syntax: --report <report_name>'
)

arg_parser.add_argument(
    '--date',
    dest='date',
    required=False,
    help='Optional: filter logs by specific date (YYYY-MM-DD). '
         'Syntax: --date <date>'
)

def log_parse(filenames: list, date=None):
    logs_data = dict()
    for filename in filenames:
        try:
            with open(file=filename, mode='r', encoding='utf-8') as file:

                for log in file:
                    data = json.loads(log)

                    if date:
                        log_date = data['@timestamp'][:10]
                        if log_date != date:
                            continue

                    if not data['url'] in logs_data.keys():
                        logs_data[data['url']] = {
                            'count': 1,
                            'total_time': float(data['response_time']),
                        }
                    else:
                        logs_data[data['url']]['count'] += 1
                        logs_data[data['url']]['total_time'] += float(data['response_time'])

        except FileNotFoundError:
            print(f'ERROR: file "{filename}" is not found')
            if len(filenames) == 1:
                sys.exit()

    return logs_data

def create_table(data):
    headers = ['', 'handler', 'total', 'avg_response_time']

    table = []
    for index, (url, stats) in enumerate(data.items()):
        table.append([
            index,
            url,
            stats.get('count', 0),
            round(stats.get('total_time', 0) / stats.get('count', 1), 3)
        ])

    output = tabulate(table, headers=headers, tablefmt='pretty')
    return output

if __name__ == '__main__':
    args = arg_parser.parse_args()
    result = log_parse(args.file, args.date)
    report = create_table(result)

    print(report)

    if args.report:
        with open(file=f'{args.report}.txt', mode='w', encoding='utf-8') as f:
            f.write(report)
