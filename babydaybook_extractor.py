#!/usr/bin/env python3
"""
BabyDaybookExtractor - Extract data from Baby Daybook app backups.

Supports extraction of:
- Daily activities (feeding, sleeping, diapers, etc.) to CSV
- Growth data (weight, height, head circumference) to CSV and interactive HTML chart
"""
import argparse
import csv
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


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


@dataclass
class GrowthEntry:
    date_millis: int
    weight: float
    height: float
    head_size: float
    notes: str

    @property
    def date(self) -> datetime:
        return datetime.fromtimestamp(self.date_millis / 1000)

    @property
    def date_str(self) -> str:
        return self.date.strftime("%Y-%m-%d")


def extract_activities(db_path: str, output_path: str) -> None:
    """Extract daily activities to CSV."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql = """SELECT type, duration, left_duration, right_duration,
             side, pee, poo, temperature, start_millis, end_millis
             FROM daily_actions ORDER BY start_millis"""
    fetched = cursor.execute(sql)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
            "activity", "year", "month", "day",
            "begin_hour", "begin_minute", "end_hour", "end_minute",
            "duration_in_seconds", "left_duration_seconds", "right_duration_seconds",
            "pee", "poo", "temperature",
        ])
        for entry in fetched:
            logged_entry = LoggedEntry(*entry)
            start_date = datetime.fromtimestamp(logged_entry.start_time)
            end_date = datetime.fromtimestamp(logged_entry.end_time)
            writer.writerow([
                logged_entry.activity,
                start_date.year, start_date.month, start_date.day,
                start_date.hour, start_date.minute,
                end_date.hour, end_date.minute,
                logged_entry.duration,
                logged_entry.left_duration, logged_entry.right_duration,
                logged_entry.pee, logged_entry.poo, logged_entry.temperature,
            ])
    conn.close()
    print(f"Activities exported to: {output_path}")


def extract_growth(db_path: str) -> List[GrowthEntry]:
    """Extract growth data from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql = """SELECT date_millis, weight, height, head_size, notes
             FROM growth ORDER BY date_millis"""
    rows = cursor.execute(sql).fetchall()
    conn.close()
    return [GrowthEntry(*row) for row in rows if row[1] > 0 or row[2] > 0 or row[3] > 0]


def export_growth_csv(entries: List[GrowthEntry], output_path: str) -> None:
    """Export growth data to CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["date", "weight_kg", "height_cm", "head_circumference_cm", "notes"])
        for entry in entries:
            writer.writerow([
                entry.date_str,
                round(entry.weight, 3) if entry.weight > 0 else "",
                round(entry.height, 1) if entry.height > 0 else "",
                round(entry.head_size, 1) if entry.head_size > 0 else "",
                entry.notes,
            ])
    print(f"Growth data exported to: {output_path}")


def generate_growth_html(entries: List[GrowthEntry], output_path: str) -> None:
    """Generate an interactive HTML chart with growth data."""
    # Prepare data for the chart
    data_points = []
    for entry in entries:
        data_points.append({
            "date": entry.date_str,
            "weight": round(entry.weight, 3) if entry.weight > 0 else None,
            "height": round(entry.height, 1) if entry.height > 0 else None,
            "head": round(entry.head_size, 1) if entry.head_size > 0 else None,
        })

    data_json = json.dumps(data_points)

    # Determine date range for subtitle
    if entries:
        start_date = entries[0].date.strftime("%b %Y")
        end_date = entries[-1].date.strftime("%b %Y")
        subtitle = f"Data from Baby Daybook &middot; {start_date} – {end_date}"
    else:
        subtitle = "No growth data found"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baby Growth Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            padding: 2rem;
            color: #333;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 0.5rem;
            color: #2c3e50;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 2rem;
        }}
        .charts-container {{
            max-width: 1000px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}
        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}
        .chart-card h2 {{
            margin-bottom: 1rem;
            color: #34495e;
            font-size: 1.1rem;
        }}
        canvas {{ width: 100% !important; }}
        .data-table {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            overflow-x: auto;
        }}
        .data-table h2 {{
            margin-bottom: 1rem;
            color: #34495e;
            font-size: 1.1rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 0.6rem 1rem;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{ color: #7f8c8d; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }}
        td {{ font-size: 0.95rem; }}
        tr:hover {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <h1>&#x1F4C8; Baby Growth Chart</h1>
    <p class="subtitle">{subtitle}</p>

    <div class="charts-container">
        <div class="chart-card">
            <h2>Weight (kg)</h2>
            <canvas id="weightChart"></canvas>
        </div>
        <div class="chart-card">
            <h2>Height (cm)</h2>
            <canvas id="heightChart"></canvas>
        </div>
        <div class="chart-card">
            <h2>Head Circumference (cm)</h2>
            <canvas id="headChart"></canvas>
        </div>
        <div class="data-table">
            <h2>All Measurements</h2>
            <table id="dataTable">
                <thead>
                    <tr><th>Date</th><th>Weight (kg)</th><th>Height (cm)</th><th>Head (cm)</th></tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <script>
        const rawData = {data_json};

        // Populate table
        const tbody = document.querySelector('#dataTable tbody');
        rawData.forEach(d => {{
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${{d.date}}</td><td>${{d.weight ?? '\\u2014'}}</td><td>${{d.height ?? '\\u2014'}}</td><td>${{d.head ?? '\\u2014'}}</td>`;
            tbody.appendChild(tr);
        }});

        const chartOptions = (unit) => ({{
            responsive: true,
            interaction: {{ mode: 'index', intersect: false }},
            plugins: {{
                tooltip: {{
                    callbacks: {{
                        title: (items) => items[0].raw.x,
                        label: (item) => ` ${{item.raw.y}} ${{unit}}`
                    }}
                }},
                legend: {{ display: false }}
            }},
            scales: {{
                x: {{
                    type: 'time',
                    time: {{ unit: 'month', displayFormats: {{ month: 'MMM yyyy' }} }},
                    title: {{ display: true, text: 'Date' }}
                }},
                y: {{
                    title: {{ display: true, text: unit }},
                    beginAtZero: false
                }}
            }}
        }});

        function makeDataset(data, field, color) {{
            return {{
                data: data.filter(d => d[field] != null).map(d => ({{ x: d.date, y: d[field] }})),
                borderColor: color,
                backgroundColor: color + '33',
                borderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                tension: 0.3,
                fill: true
            }};
        }}

        new Chart(document.getElementById('weightChart'), {{
            type: 'line',
            data: {{ datasets: [makeDataset(rawData, 'weight', '#e74c3c')] }},
            options: chartOptions('kg')
        }});

        new Chart(document.getElementById('heightChart'), {{
            type: 'line',
            data: {{ datasets: [makeDataset(rawData, 'height', '#3498db')] }},
            options: chartOptions('cm')
        }});

        new Chart(document.getElementById('headChart'), {{
            type: 'line',
            data: {{ datasets: [makeDataset(rawData, 'head', '#2ecc71')] }},
            options: chartOptions('cm')
        }});
    </script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Growth chart generated: {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract data from Baby Daybook app backup (.db file)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract activities to CSV
  python babydaybook_extractor.py -i backup.db -o activities.csv

  # Extract growth data to CSV
  python babydaybook_extractor.py -i backup.db --growth -o growth.csv

  # Generate interactive HTML growth chart
  python babydaybook_extractor.py -i backup.db --growth --html growth_chart.html

  # Extract growth CSV and HTML chart together
  python babydaybook_extractor.py -i backup.db --growth -o growth.csv --html growth_chart.html
""",
    )
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
        help="path for the extracted CSV output",
        required=False,
    )
    parser.add_argument(
        "--growth",
        action="store_true",
        help="extract growth data (weight, height, head circumference) instead of activities",
    )
    parser.add_argument(
        "--html",
        dest="html_path",
        type=str,
        help="generate an interactive HTML growth chart at the specified path (implies --growth)",
        required=False,
    )
    args = parser.parse_args()

    if not os.path.isfile(args.in_path):
        parser.error(f"Cannot find the .db file at '{args.in_path}'")

    if args.html_path:
        args.growth = True

    if not args.out_path and not args.html_path:
        parser.error("Please specify at least one output: -o for CSV or --html for chart")

    if args.out_path and os.path.isfile(args.out_path):
        parser.error(f"'{args.out_path}' already exists, please supply a path to a new file.")

    if args.html_path and os.path.isfile(args.html_path):
        parser.error(f"'{args.html_path}' already exists, please supply a path to a new file.")

    return args


def main() -> None:
    args = parse_args()

    if args.growth:
        entries = extract_growth(args.in_path)
        if not entries:
            print("No growth data found in the database.")
            return
        print(f"Found {len(entries)} growth records.")
        if args.out_path:
            export_growth_csv(entries, args.out_path)
        if args.html_path:
            generate_growth_html(entries, args.html_path)
    else:
        if not args.out_path:
            print("Error: -o is required when extracting activities.")
            return
        extract_activities(args.in_path, args.out_path)


if __name__ == "__main__":
    main()
