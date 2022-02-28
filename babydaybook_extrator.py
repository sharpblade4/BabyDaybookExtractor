#!/usr/bin/env python3
import argparse
import csv
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass
class LoggedEntry:
    activity: str
    duration: int
    left_duration: int
    right_duration: int
    side: str
    pee: int
    poo: int
    temperature: float
    start_time: int
    end_time: int

    def __post_init__(self):
        millis_to_seconds_factor = 1e3
        self.left_duration /= millis_to_seconds_factor
        self.right_duration /= millis_to_seconds_factor
        self.duration /= millis_to_seconds_factor
        self.start_time /= millis_to_seconds_factor
        self.end_time /= millis_to_seconds_factor


def extract(db_path: str, output_path: str, all_data_raw: bool = False) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql = (
        """select 
        type as activity, duration, left_duration, right_duration, 
        side, pee, poo, temperature, start_millis as start_t, end_millis as end_t
    from daily_actions
    """
        if not all_data_raw
        else "select * from daily_actions"
    )
    fetched = cursor.execute(sql)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if not all_data_raw:
            writer.writerow(
                [
                    "activity",
                    "year",
                    "month",
                    "day",
                    "begin_hour",
                    "begin_minute",
                    "end_hour",
                    "end_minute",
                    "duration_in_seconds",
                    "left_duration_seconds",
                    "right_duration_seconds",
                    "pee",
                    "poo",
                    "temperature",
                ]
            )
        for entry in fetched:
            logged_entry = LoggedEntry(*entry)
            start_date = datetime.fromtimestamp(logged_entry.start_time)
            end_date = datetime.fromtimestamp(logged_entry.end_time)
            writer.writerow(
                [
                    logged_entry.activity,
                    start_date.year,
                    start_date.month,
                    start_date.day,
                    start_date.hour,
                    start_date.minute,
                    end_date.hour,
                    end_date.minute,
                    logged_entry.duration,
                    logged_entry.left_duration,
                    logged_entry.right_duration,
                    logged_entry.pee,
                    logged_entry.poo,
                    logged_entry.temperature,
                ]
            )


def parse_args() -> Tuple[str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        dest="in_path",
        type=str,
        help="path to .db backup file from the app",
        required=True,
    )
    parser.add_argument(
        "-o",
        dest="out_path",
        type=str,
        help="path for the extracted output (new file will be created)",
        required=True,
    )
    args = parser.parse_args()
    if not os.path.isfile(args.in_path):
        print(f"Cannot find the .db file in path '{args.in_path}'")
        exit(-1)
    if os.path.isfile(args.out_path):
        print(
            f"'{args.out_path}' already exists, please supply a path to a file which doesn't exist."
        )
        exit(-1)
    return args.in_path, args.out_path


def raw_processing() -> None:
    import pandas as pd
    import sqlite3
    import datetime
    import matplotlib.pyplot as plt
    
    con = sqlite3.connect("./BabyDaybook_20220228.db")
    df = pd.read_sql_query("SELECT * from daily_actions", con)
    (df[df.type=='sleeping'].groupby(['year','month','day']).sum().duration/(3600*1e3)).plot(title='sleeping hours per day')
    plt.show()
    df[df.type=='bottle'].groupby(['year','month','day']).sum().volume[1:-1].plot(title='milk ml per day')
    plt.show()

    
def main() -> None:
    in_path, out_path = parse_args()
    extract(in_path, out_path)


if __name__ == "__main__":
    main()
