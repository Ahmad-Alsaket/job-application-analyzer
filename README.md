# Job Application Analyzer

Parses a personal job-application log (a plain text file, one application per line)
into a CSV, then analyzes it with pandas: an outcome breakdown (with a bar chart),
applications per month, and companies applied to more than once.

## Data format

One application per line, fields separated by ` - ` (hyphen, en dash or em dash):

```
Company - Role - Month Year - status
```

For example:

```
Acme Corp - Junior Data Analyst - March 2026 - rejected
```

The year is optional (it defaults to 2026), and the role may itself contain ` - `.

## Usage

Install the dependencies:

```
py -m pip install -r requirements.txt
```

Try it with the bundled fake data:

```
py parse_to_csv.py data/applications.sample.txt   # writes data/applications.sample.csv
py analyze.py data/applications.sample.csv        # prints the analysis, saves a PNG chart
```

To use your own data, create `data/applications.txt` in the same format and run
the scripts without arguments:

```
py parse_to_csv.py   # data/applications.txt -> data/applications.csv
py analyze.py
```

Run the tests with:

```
py -m unittest discover tests
```

## Privacy

My real application log (`data/applications.txt`), the CSV generated from it, and
the charts are deliberately excluded from this repository via `.gitignore`.
`data/applications.sample.txt` contains only made-up companies.
