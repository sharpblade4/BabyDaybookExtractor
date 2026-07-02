## Description
'Baby Daybook' [application](https://babydaybook.app/) is a newborn tracker app
to log activities such as breastfeeding, sleeping, pooping, etc. in order to
monitor the development of the child.

The parents who use this app insert a lot of data into it over time. 
While the app supplies statistics and exportable PDF file (for paying users only)
it doesn't grant access to the raw data.

The *BabyDaybookExtractor* solves this limitation by utilizing the backup mechanism of the app,
and extracts the raw data to CSV files and interactive HTML charts. This allows the interested parent to
research the data and find interesting patterns or learn from the statistics.

## Features
- **Activity extraction**: Export all daily activities (feeding, sleeping, diapers, baths, etc.) to CSV
- **Growth data extraction**: Export weight, height, and head circumference measurements to CSV
- **Interactive growth chart**: Generate a standalone HTML file with interactive charts (powered by Chart.js)

## Usage
### Requirements
Make sure you have a *python* environment in version 3.7 or higher.
No external dependencies are required — the script uses only the Python standard library.

To install python follow [this guide](https://wiki.python.org/moin/BeginnersGuide/Download).

### Getting the Backup File
In the application, under the *Account* window, click on the settings wheel icon (top right). 
Then, select *Backup & Restore* and press the sharing icon. 
Choose your preferable method of getting this file to the computer (e.g., emailing yourself).

### Extract Activities
Extract daily activities (feeding, sleeping, diapers, etc.) to CSV:
```shell
python babydaybook_extractor.py -i /PATH/TO/BabyDaybook_backup.db -o activities.csv
```

### Extract Growth Data
Export weight, height, and head circumference to CSV:
```shell
python babydaybook_extractor.py -i /PATH/TO/BabyDaybook_backup.db --growth -o growth.csv
```

### Generate Growth Chart
Generate an interactive HTML chart:
```shell
python babydaybook_extractor.py -i /PATH/TO/BabyDaybook_backup.db --growth --html growth_chart.html
```

You can also generate both CSV and HTML at once:
```shell
python babydaybook_extractor.py -i /PATH/TO/BabyDaybook_backup.db --growth -o growth.csv --html growth_chart.html
```

The HTML chart includes:
- Weight over time (kg)
- Height over time (cm)
- Head circumference over time (cm)
- A summary data table

Open the `.html` file in any browser — no server needed.

![Growth Chart Example](https://img.shields.io/badge/Chart.js-Interactive-blue)

### [Optional] Analysis with pandas
Install pandas: `python -m pip install pandas`

```python
import pandas as pd

# Activities analysis
df = pd.read_csv('activities.csv')
df.activity.value_counts()

# Growth analysis
growth = pd.read_csv('growth.csv')
print(growth[['date', 'weight_kg', 'height_cm']])
```

## Database Structure
The Baby Daybook backup is a SQLite database containing these tables:
| Table | Description |
|-------|-------------|
| `daily_actions` | All logged activities (feeding, sleeping, diapers, baths, etc.) |
| `growth` | Weight, height, and head circumference measurements |
| `babies` | Baby profile information |
| `moments` | Milestone moments |
| `teething` | Teeth tracking |
| `daily_notes` | Daily notes |

## Migration Note
The script filename was corrected from `babydaybook_extrator.py` to `babydaybook_extractor.py`.
The old file is kept for backward compatibility but the new filename is recommended.
