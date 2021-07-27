# SEC EDGAR Company HQ Scraper

A command-line tool to match CIKs (Central Index Keys) to company headquarter locations for that year from the [SEC EDGAR website](https://www.sec.gov/edgar/searchedgar/companysearch.html).

## Installation

Clone this repository.

```bash
git clone https://github.com/daniel-yili-ye/SEC-web-scrapping
```

Install dependencies.

```bash
pip install -r requirements.txt
```

## Usage

Before running the program in the command-line, please save your input file in the same folder where the `script.py` file is located.

If possible, please specify input csv and output csv filenames, otherwise the program will assume the file names listed in the optional parameters below. The input file must also contain `CIK` and `Year` columns.

```bash
python3 script.py [input.csv] [output.csv]
```

The script will include `City`, `new_state`, `SEC Filing`, `Form Type`, and `Date Filed` columns in the output file.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
