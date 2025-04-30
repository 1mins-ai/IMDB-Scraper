# IMDB Top 250 Movie Quotes Scraper

This project provides a Python script to scrape movie IDs and quotes from IMDB's Top 250 movies list.

## Features

- Automatically scrapes the IMDB Top 250 movies list
- Extracts movie IDs from the Top 250 list
- Retrieves movie titles and quotes for each movie
- Saves data in both CSV format and individual text files
- Provides detailed logging to track the scraping process
- Implements error handling to continue even if individual movies fail

## System Requirements

- Python 3.7 or higher
- Required dependencies (see below)

## Installing Dependencies

```bash
pip install selenium webdriver-manager
```

## Script Description

### imdb_top250_scraper.py

This script uses Selenium WebDriver to simulate browser behavior and extract data from IMDB, which is necessary for handling JavaScript-loaded content.

**Main Features:**
- Uses Selenium to automate browser interactions
- Supports processing dynamically loaded content
- Simulates real user browsing behavior
- Extracts movie IDs from the Top 250 list
- Retrieves quotes for specified movies (default: first 3 movies)

## Usage

Run the script with:

```bash
python imdb_top250_scraper.py
```

You can specify how many movies to extract quotes from using the `--limit` parameter (Default 3 for testing):

```bash
python imdb_top250_scraper.py --limit 10
```

By default, the script will:
1. Extract all movie IDs from the IMDB Top 250 list
2. Save these IDs to a CSV file
3. Extract quotes for the first 3 movies (or the number specified by `--limit`)
4. Save quotes to individual text files and a combined CSV file

## Output Files

- **imdb_top250_ids.csv** - Contains all movie IDs from the IMDB Top 250 list
- **movie_quotes/** - Directory containing:
  - Individual text files for each processed movie (format: `{movie_id}_{movie_title}.txt`)
  - **all_quotes.csv** - Combined CSV file with all quotes from processed movies

The CSV files contain the following columns:
1. Movie ID
2. Movie Title
3. Quote Number
4. Quote

## Notes

- Please respect IMDB's terms of service and avoid sending too many requests in a short period
- Website structure may change, which might require selector updates
- When using this script, ensure you have the appropriate browser driver installed

## Disclaimer

This project is for educational and research purposes only. Users should assume all risks and responsibilities associated with using this script. Do not use this tool for any activities that violate IMDB's terms of service or any applicable laws.

## License

[MIT](https://opensource.org/licenses/MIT) 