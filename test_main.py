import json
import sys
from unittest.mock import patch
from main import log_parse, create_table, arg_parser

def test_log_parse(tmpdir):

    test_logs = [
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",
         "response_time": 0.1, "http_user_agent": "..."},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",
         "response_time": 0.2, "http_user_agent": "..."},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",
         "response_time": 0.3, "http_user_agent": "..."}
    ]

    temp_log = tmpdir.join('test_log.json')

    with open(temp_log, 'w') as f:
        for log in test_logs:
            f.write(json.dumps(log) + '\n')

    res = log_parse([temp_log])

    exp_res = {
        '/api/context/...': {'count': 3, 'total_time': 0.600}
    }

    for url, stats in res.items():
        expected_stats = exp_res[url]
        assert stats['count'] == expected_stats['count']
        assert round(stats['total_time'], 3) == expected_stats['total_time']

def test_invalid_file(capsys):

    with patch.object(sys, 'argv', ['main.py', '--file', '___.log']):
        args = arg_parser.parse_args()

        with patch.object(sys, 'exit') as mock_exit:
            result = log_parse(args.file)
            if len(args.file) == 1:
                mock_exit.assert_called_once()

    captured = capsys.readouterr()
    assert "ERROR:" in captured.out and "___.log" in captured.out

def test_date_filter(tmpdir):

    test_logs = [
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/test1", "response_time": 0.1},
        {"@timestamp": "2025-06-22T14:57:32+00:00", "url": "/api/test1", "response_time": 0.2},
        {"@timestamp": "2025-06-23T15:57:32+00:00", "url": "/api/test1", "response_time": 0.3}
    ]

    log_file = tmpdir.join("date_test.log")
    with open(log_file, 'w') as f:
        for log in test_logs:
            f.write(json.dumps(log) + '\n')

    res = log_parse([log_file], "2025-06-22")

    exp_res = {
        '/api/test1': {'count': 2, 'total_time': 0.3}
    }

    for url, stats in res.items():
        expected_stats = exp_res[url]
        assert stats['count'] == expected_stats['count']
        assert round(stats['total_time'], 3) == expected_stats['total_time']

def test_create_table():
    test_output = {
        '/api/context/...': {'count': 10, 'total_time': 2.4},
        '/api/homeworks/...': {'count': 20, 'total_time': 2.2},
        '/api/specialization/...': {'count': 10, 'total_time': 4.0}
    }

    exp_report = '''+---+-------------------------+-------+-------------------+
|   |         handler         | total | avg_response_time |
+---+-------------------------+-------+-------------------+
| 0 |    /api/context/...     |  10   |       0.24        |
| 1 |   /api/homeworks/...    |  20   |       0.11        |
| 2 | /api/specialization/... |  10   |        0.4        |
+---+-------------------------+-------+-------------------+'''

    report = create_table(test_output)

    assert report == exp_report

