from datetime import datetime


def is_date_inside_interval(date_as_str: str, start_as_str: str, end_as_str: str) -> bool:
    if date_as_str is None:
        return True
    date = datetime.strptime(date_as_str, "%Y-%m-%d %H:%M:%S")

    if start_as_str is None:
        start = datetime(0, 1, 1)
    else:
        start = datetime.strptime(start_as_str, "%Y-%m-%d %H:%M:%S")

    if end_as_str is None:
        end = datetime(9999, 1, 1)
    else:
        end = datetime.strptime(end_as_str, "%Y-%m-%d %H:%M:%S")

    return start <= date <= end
