"""
main.py: Election Scraper - třetí projekt do Engeto Online Python Akademie

author: Jan Bláha
email: jan.blaha@bcas.cz
"""

import sys
import requests as rq
from bs4 import BeautifulSoup as bs
import re
import csv

def load_page_content(url):
    """ Loads page content from given URL and returns BeautifulSoup object """
    try:
        server_response = rq.get(url)
    except:
        return None
    if server_response.status_code == 200:
        return bs(server_response.text, "html.parser")
    else:
        return None
    
def get_base_url(url):
    """ Returns base URL from full URL """
    return "/".join(url.split("/")[:len(url.split("/"))-1])+"/"

def write_csv(filename, elections_data):
    """ Writes election data to CSV file 
    Args:
        filename: str, output CSV filename
        elections_data: dict in format {city_code: {data_key: data_value, ...}, ...}
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['code'] + list(list(elections_data.values())[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for city, data in elections_data.items():
            writer.writerow({'code': city, **data})

def get_cities_links(url):
    """ Returns a dictionary of city codes and their corresponding names and links from the main election page 
    Args:
        url: str, URL of the main election page
    """
    print(f"Nacitani seznamu obci z {url} ...")
    base_url = get_base_url(url)

    content = load_page_content(url)

    cities = dict()

    cities_names = content.find_all("td", {"class": "overflow_name"})
    cities_links = content.find_all("td", {"class": "cislo"})

    for city, link in zip(cities_names, cities_links):
        cities[link.get_text()] = (city.get_text(), link.find_all('a', href=True)[0]['href']) # The key is the city code

    return base_url, cities

def clean_up_results(results):
    """ Unify party lists across all cities 
    1) Create a set of all parties across all cities
    2) For each city, add missing parties with 0 votes 
    Args:
        results: dict in format {city_code: {"location": city_name, "registered": registered, "envelopes": envelopes, "valid": valid, "parties_votes": parties_votes}}
    Returns:
        dict in format {city_code: {"location": city_name, "registered": registered, "envelopes": envelopes, "valid": valid, party_name1: votes1, party_name2: votes2, ...}}
    """
    parties = set()

    for item in results:
        parties.update([(k, n[0]) for k, n in zip(results[item]["parties_votes"].keys(), results[item]["parties_votes"].values())])

    for city in results:
        for party in sorted(parties):   # order parties by party number
            if party[0] not in results[city]["parties_votes"]:
                results[city]["parties_votes"][party[0]] = (party[1], 0) # add missing party with 0 votes

    for city in results: # flatten party votes into main dictionary
        party_votes = results[city].pop("parties_votes")
        results[city].update(dict([party for party in party_votes.values()]))

    return results

def get_city_election_results(base_url, cities):
    """ Returns election results for each city
    Args:
        base_url: str, base URL of the election pages
        cities: dict in format {city_code: (city_name, city_link), ...}
    Returns:
        dict in format {city_code: {"location": city_name, "registered": registered, "envelopes": envelopes, "valid": valid, party_name1: votes1, party_name2: votes2, ...}, ...}
    """
    print("Nacitani vysledku jednotlivych obci ...")
    final_results = dict()

    for city, (city_name, link) in cities.items():
        city_content = load_page_content(base_url + link)   # Load city page content

        registered = int(city_content.find_all("td", {"class": "cislo", "headers": "sa2"})[0].get_text().replace("\xa0", ""))
        envelopes = int(city_content.find_all("td", {"class": "cislo", "headers": "sa3"})[0].get_text().replace("\xa0", ""))
        valid = int(city_content.find_all("td", {"class": "cislo", "headers": "sa6"})[0].get_text().replace("\xa0", ""))

        parties = dict()

        # Have to use regex here because of different table header ids for different columns
        party_number = city_content.find_all("td", {"class": "cislo", "headers": re.compile(r't[1|2]sa1 t[1|2]sb1')})
        party_name = city_content.find_all("td", {"class": "overflow_name", "headers": re.compile(r't[1|2]sa1 t[1|2]sb2')})
        total_votes = city_content.find_all("td", {"class": "cislo", "headers": re.compile(r't[1|2]sa2 t[1|2]sb3')})

        for number, party, votes in zip(party_number, party_name, total_votes):
            parties[int(number.get_text().replace("\xa0", ""))] = (party.get_text(), int(votes.get_text().replace("\xa0", "")))

        final_results[city] = {"location": city_name, "registered": registered, "envelopes": envelopes, "valid": valid, "parties_votes": parties}

    return clean_up_results(final_results)

def main(url, filename):
    """ Main function to orchestrate the scraping process 
    1) Get list of cities and their links
    2) Get election results for each city
    3) Write results to CSV file
    Args:
        url: str, URL of the main election page
        filename: str, output CSV filename
    """
    base_url, cities = get_cities_links(url)

    city_results = get_city_election_results(base_url, cities) # Pass base_url and cities {"code": (name, link)} to fetch data of city pages

    print(f"Ulozeni vysledku do souboru {filename}")
    write_csv(filename, city_results)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Spusteni: python main.py <URL> <filename.csv>")
        sys.exit(1)
    url = sys.argv[1]
    if len(url.split("/"))<4: # Basic check for URL format
        print("Chyba: parametr URL nemá tvar <URL>")
        sys.exit(1)
    filename = sys.argv[2]
    main(url, filename)