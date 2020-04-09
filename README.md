# Messenger-Analyzer
Parses JSON files that hold Facebook messenger data and allows user to generate graphs and trends. Download Facebook Messenger data in JSON format and edit rootpath to use

## Usage

Make sure to have Python 3 installed.

Pass the path to your Facebook messages/inbox directory of data as a command line argument.

```bash
python3 main.py "path/to/json/facebook/messages/inbox/"
```

## Required Libraries

* pandas
* matplotlib
* seaborn
* numpy
* spacy (with en_core_web_sm model)
