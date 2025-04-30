import time
import re
import csv
import os
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Set up and return Selenium WebDriver"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_top250_movie_ids():
    """Get the list of movie IDs from IMDB Top 250 page"""
    driver = setup_driver()
    movie_ids = []
    seen_ids = set()  # Used to track already added IDs
    
    try:
        # Access IMDB Top 250 page
        print("Accessing IMDB Top 250 page...")
        driver.get("https://www.imdb.com/chart/top/?ref_=nv_mv_250")
        time.sleep(3)  # Wait for page to load
        
        # Find all movie links
        print("Searching for movie links...")
        
        # Try multiple selectors to find movie links
        selectors = [
            "a[href^='/title/tt']",
            ".ipc-title-link-wrapper",
            ".titleColumn a",
            ".lister-list .titleColumn a"
        ]
        
        movie_links = []
        for selector in selectors:
            try:
                print(f"Trying selector: {selector}")
                links = driver.find_elements(By.CSS_SELECTOR, selector)
                if links:
                    movie_links.extend(links)
                    print(f"Found {len(links)} links with selector {selector}")
            except Exception as e:
                print(f"Error with selector {selector}: {str(e)}")
        
        print(f"Found a total of {len(movie_links)} possible movie links through various selectors")
        
        # Extract movie IDs
        for link in movie_links:
            try:
                href = link.get_attribute("href")
                if href:
                    movie_id_match = re.search(r"/title/(tt\d+)/", href)
                    if movie_id_match:
                        movie_id = movie_id_match.group(1)
                        if movie_id not in seen_ids:
                            movie_ids.append(movie_id)
                            seen_ids.add(movie_id)
            except Exception as e:
                print(f"Error processing link: {str(e)}")
        
        print(f"Initially found IDs for {len(movie_ids)} movies")
        
        # If still not enough, try all links on the page
        if len(movie_ids) < 250:
            print("Trying all links on the page...")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    if href and "/title/tt" in href:
                        movie_id_match = re.search(r"/title/(tt\d+)/", href)
                        if movie_id_match:
                            movie_id = movie_id_match.group(1)
                            if movie_id not in seen_ids:
                                movie_ids.append(movie_id)
                                seen_ids.add(movie_id)
                except:
                    continue

        # Check for pagination, if found, click on next page and continue extracting IDs
        try:
            next_page_buttons = driver.find_elements(By.CSS_SELECTOR, ".pagination a.next-page")
            if next_page_buttons:
                print("Found pagination, attempting to get movie IDs from more pages...")
                page = 1
                while len(next_page_buttons) > 0 and page < 5:  # Limit to a maximum of 5 pages
                    page += 1
                    next_page_buttons[0].click()
                    time.sleep(3)  # Wait for new page to load
                    
                    print(f"Processing page {page}...")
                    # Repeat the above process to get links from the new page
                    for selector in selectors:
                        try:
                            links = driver.find_elements(By.CSS_SELECTOR, selector)
                            for link in links:
                                href = link.get_attribute("href")
                                if href:
                                    movie_id_match = re.search(r"/title/(tt\d+)/", href)
                                    if movie_id_match:
                                        movie_id = movie_id_match.group(1)
                                        if movie_id not in seen_ids:
                                            movie_ids.append(movie_id)
                                            seen_ids.add(movie_id)
                        except:
                            continue
                    
                    # Update next page buttons
                    next_page_buttons = driver.find_elements(By.CSS_SELECTOR, ".pagination a.next-page")
        except Exception as e:
            print(f"Error processing pagination: {str(e)}")
        
        # Limit to the top 250 movies
        movie_ids = movie_ids[:250]
        print(f"Finally found IDs for {len(movie_ids)} movies")
        
        # Output all movie IDs
        print("\nAll movie IDs:")
        for movie_id in movie_ids:
            print(movie_id)
        
        # Save movie IDs to CSV file
        with open("imdb_top250_ids.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Movie ID"])
            for movie_id in movie_ids:
                writer.writerow([movie_id])
        
        print("Movie IDs have been saved to imdb_top250_ids.csv")
        
        return movie_ids
        
    except Exception as e:
        print(f"Error getting movie IDs: {str(e)}")
        return []
    
    finally:
        # Close WebDriver
        print("Closing WebDriver...")
        driver.quit()

def extract_movie_quotes(movie_ids, limit=3):
    """Extract quotes from specified list of movie IDs
    
    Args:
        movie_ids: List of movie IDs
        limit: Limit the number of movies to process, default is 3
    
    Returns:
        Dictionary containing movie quotes in format {movie_id: {'title': title, 'quotes': [quotes]}}
    """
    # Limit the number of movies to process
    movie_ids_to_process = movie_ids[:limit]
    print(f"Will process quotes for the following {len(movie_ids_to_process)} movies: {movie_ids_to_process}")
    
    # Create results directory
    if not os.path.exists("movie_quotes"):
        os.makedirs("movie_quotes")
    
    driver = setup_driver()
    all_quotes = {}
    
    try:
        for movie_id in movie_ids_to_process:
            print(f"\nProcessing quotes for movie {movie_id}...")
            
            # First visit the movie's main page to get the accurate movie title
            movie_main_url = f"https://www.imdb.com/title/{movie_id}/"
            driver.get(movie_main_url)
            time.sleep(3)  # Wait for page to load
            
            # Extract movie title - look on the main page
            try:
                # Try multiple selectors to find the movie title
                title_selectors = [
                    "h1.sc-b73cd867-0",  # New IMDb title selector
                    "h1.TitleHeader__TitleText-sc-1wu6n3d-0",  # Another possible title selector
                    "h1[data-testid='hero__pageTitle']",  # Test ID-based selector
                    "h1.title",  # Old IMDb
                    "h1"  # Most generic selector if all others fail
                ]
                
                movie_title = None
                for selector in title_selectors:
                    try:
                        title_element = driver.find_element(By.CSS_SELECTOR, selector)
                        movie_title = title_element.text.strip()
                        if movie_title:
                            break
                    except:
                        continue
                
                if not movie_title:
                    # Try to extract from page title
                    page_title = driver.title
                    if page_title:
                        # Usually IMDb page title format is "Movie Name (Year) - IMDb"
                        title_match = re.match(r"(.+?)(?:\s*\(\d{4}\))?(?:\s*-\s*IMDb)?$", page_title)
                        if title_match:
                            movie_title = title_match.group(1).strip()
                
                if not movie_title:
                    movie_title = f"Movie_{movie_id}"
            except:
                movie_title = f"Movie_{movie_id}"
                print(f"Could not get movie title, using ID as title: {movie_title}")
            
            print(f"Movie title: {movie_title}")
            
            # Then visit the quotes page
            quotes_url = f"https://www.imdb.com/title/{movie_id}/quotes/?ref_=tt_dyk_qu"
            driver.get(quotes_url)
            time.sleep(3)  # Wait for page to load
            
            # Try multiple selectors to find quotes
            quotes = []
            selectors = [
                ".ipc-html-content-inner-div",  # New IMDB
                ".sodatext",  # Old IMDB
                ".quote",     # Another possible format
                "div.quote"   # Yet another possible format
            ]
            
            found_quotes = False
            for selector in selectors:
                try:
                    quote_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if quote_elements:
                        found_quotes = True
                        print(f"Found {len(quote_elements)} quotes using selector {selector}")
                        
                        for element in quote_elements:
                            quote_text = element.text.strip()
                            if quote_text:
                                # Clean quote text - remove unnecessary prefixes
                                quote_text = re.sub(r"^Edit$", "", quote_text, flags=re.MULTILINE).strip()
                                if quote_text:
                                    quotes.append(quote_text)
                        
                        break  # If quotes are found, don't try other selectors
                except Exception as e:
                    print(f"Error searching quotes with selector {selector}: {str(e)}")
            
            # If regular selectors didn't find anything, try to get all possible content on the page
            if not found_quotes or not quotes:
                print("Trying to get all possible quote content from the page...")
                try:
                    # Get main content area
                    content_area = driver.find_element(By.TAG_NAME, "main")
                    # Analyze content to get quotes
                    content_text = content_area.text
                    
                    # Remove some generic non-quote content
                    content_text = re.sub(r"Contribute to this page", "", content_text)
                    content_text = re.sub(r"Add a quote", "", content_text)
                    content_text = re.sub(r"Edit", "", content_text)
                    
                    # Simple processing: split by empty lines
                    potential_quotes = [q.strip() for q in content_text.split("\n\n") if q.strip()]
                    
                    # Filter out lines that are too short (likely navigation items or other UI elements)
                    potential_quotes = [q for q in potential_quotes if len(q) > 15]
                    
                    quotes.extend(potential_quotes)
                    print(f"Found {len(potential_quotes)} possible quote fragments through page content analysis")
                except Exception as e:
                    print(f"Error trying to get all content: {str(e)}")
            
            # Ensure filename safety
            safe_title = "".join([c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in movie_title])
            safe_title = safe_title.strip()
            if not safe_title:
                safe_title = f"Movie_{movie_id}"
            
            print(f"Found a total of {len(quotes)} quotes")
            all_quotes[movie_id] = {'title': movie_title, 'quotes': quotes}
            
            # Save quotes for single movie
            with open(f"movie_quotes/{movie_id}_{safe_title}.txt", "w", encoding="utf-8") as f:
                f.write(f"Movie: {movie_title} (ID: {movie_id})\n")
                f.write("=" * 50 + "\n\n")
                for i, quote in enumerate(quotes, 1):
                    f.write(f"Quote #{i}:\n{quote}\n\n")
            
            print(f"Saved quotes for movie {movie_id} ({movie_title}) to file")
        
        # Save all processed movie quotes to a CSV file
        with open("movie_quotes/all_quotes.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Movie ID", "Movie Title", "Quote Number", "Quote"])
            for movie_id, movie_data in all_quotes.items():
                movie_title = movie_data['title']
                for i, quote in enumerate(movie_data['quotes'], 1):
                    writer.writerow([movie_id, movie_title, i, quote])
        
        print("\nAll quotes have been saved to movie_quotes/all_quotes.csv")
        return all_quotes
        
    except Exception as e:
        print(f"Error extracting movie quotes: {str(e)}")
        return all_quotes
    
    finally:
        # Close WebDriver
        print("Closing WebDriver...")
        driver.quit()

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Scrape IMDB Top 250 movies and extract quotes')
    parser.add_argument('--limit', type=int, default=3, 
                        help='Limit the number of movies to extract quotes from (default: 3)')
    args = parser.parse_args()
    
    # Get list of movie IDs
    movie_ids = get_top250_movie_ids()
    
    # If movie IDs are found, extract quotes for movies up to the specified limit
    if movie_ids:
        print(f"\nStarting to extract movie quotes (limit: {args.limit} movies)...")
        extract_movie_quotes(movie_ids, limit=args.limit)
    else:
        print("No movie IDs found, cannot extract quotes")
