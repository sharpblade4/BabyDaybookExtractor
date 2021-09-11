## Description
'Baby Daybook' [application](https://babydaybook.app/) is a newborn tracker app
to log activities such as breastfeeding, sleeping, pooping, etc. in order to
monitor the development of the child.

The parents who use this app insert a lot of data into it over time. 
While the app supplies statistics and exportable PDF file (for paying users only)
it doesn't grant access to the raw data.

The *BabyDaybookExtractor* solves this limitation by utilizing the backup mechanism of the app,
and extract a pandas dataframe with all the data. This, allows the interested parent to
research the data and find interesting patterns or learn from the statistics.

## Usage
### Requirements
Make sure you have a *python* environment in version 3.7 or higher.
To install python follow [this guide](https://wiki.python.org/moin/BeginnersGuide/Download).

### Extract The Data
#### Step 0: From the app
In the application, under the *Account* window, click on the settings wheel icon (top right). 
Then, select *Backup & Restore* and press the sharing icon. 
Choose your preferable method of getting this file to the computer (e.g., emailing yourself).

#### Step 1: From the computer
Run the *BabyDaybookExtractor* on the file as follows:
```shell
python babydaybook_extrator.py -i /PATH/TO/DOWNLOADED/BabyDaybook_20211024.db -o /PATH/TO/output.csv
```
This will create a csv file with all the data, which can be opened by pandas or any other way. 

#### Step 2: [Optional] Analysis
This is an example for analysing the data, using *pandas* library. To run it the python environment 
must have *pandas* library installed. To install it, run `python -m pip install pandas`.

Then, use a python interactive session:
```python
import pandas as pd
df = pd.read_csv('/PATH/TO/output.csv')

df.activity.value_counts()
# Out[]: 
#     breastfeeding                        404
#     sleeping                             147
#     diaper_change                        143
#     bath                                  25
#     temperature                           11

df[df.activity == 'breastfeeding'][['left_duration_seconds', 'right_duration_seconds']].mean()
# Out[]: left_duration_seconds     431.508317
#        right_duration_seconds    573.674952
df[df.activity == 'diaper_change'][['poo', 'pee']].sum()
# Out[]: 
#     poo    130
#     pee    139
```
