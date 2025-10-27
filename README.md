# Elections Scraper

A Python script for scraping election results from the Czech Statistical Office's election website (volby.cz). This project is part of the Engeto Python Academy curriculum.

## Description

This script scrapes parliamentary election results for a specified district in the Czech Republic. It collects detailed voting data including:
- Location names and codes
- Number of registered voters
- Number of issued envelopes
- Number of valid votes
- Detailed results for each political party

## Installation

1. Clone this repository:
```bash
git clone https://github.com/j3corre/Engeto_Projekt_3.git
cd Engeto_Projekt_3
```

2. Create a virtual environment:
```bash
python -m venv elections_scraper
```

3. Activate the virtual environment:
- Windows:
```bash
elections_scraper\Scripts\activate.bat
```
- Unix/MacOS:
```bash
source elections_scraper/bin/activate
```

4. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the script using the following format:
```bash
python main.py <URL> <output_filename>
```

Where:
- `<URL>` is the URL of the election results page for your chosen district
- `<output_filename>` is the name of the CSV file where results will be saved

### Example

```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3206" rokycany_vysledky.csv
```

## Output Format

The script creates a CSV file with semicolon (;) as the delimiter, containing the following columns:
- `code` - Municipality code
- `location` - Municipality name
- `registered` - Number of registered voters
- `envelopes` - Number of issued envelopes
- `valid` - Number of valid votes
- Additional columns for each political party showing their vote counts

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- See `requirements.txt` for complete list

## Author

- **Jan Bláha**
- Email: jan.blaha@bcas.cz