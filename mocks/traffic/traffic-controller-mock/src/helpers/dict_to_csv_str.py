import csv
import io
from typing import List, Dict


def dict_to_csv_str(csv_data: List[Dict[str, str]]) -> str:
    if not csv_data:
        return

    fields = csv_data[0].keys()
    output = io.StringIO()

    writer = csv.DictWriter(output, fieldnames=fields, delimiter=',')
    writer.writeheader()
    writer.writerows(csv_data)
    return output.getvalue()


if __name__ == "__main__":
    print(dict_to_csv_str([{"a": 1, "b": 2}, {"a": 3, "b": 4}]))