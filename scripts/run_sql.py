import sys
from pathlib import Path

import duckdb


def main() -> None:
    sql_files = [Path(arg) for arg in sys.argv[1:]]
    con = duckdb.connect()  # in-memory database, gone when the script ends

    for index, sql_file in enumerate(sql_files):
        relation = con.sql(sql_file.read_text(encoding="utf-8"))
        is_last = index == len(sql_files) - 1
        if is_last and relation is not None:
            relation.show(max_rows=50)


if __name__ == "__main__":
    main()
    