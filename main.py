"""
main.py: Election Scraper - třetí projekt do Engeto Online Python Akademie

author: Jan Bláha
email: jan.blaha@bcas.cz
"""

import pprint
import requests as rq
from bs4 import BeautifulSoup as bs
import re
import csv

def load_page_content(url):
    try:
        server_response = rq.get(url)
    except:
        return None
    if server_response.status_code == 200:
        return bs(server_response.text, "html.parser")
    else:
        return None
    
def get_base_url(url):
    return "/".join(url.split("/")[:len(url.split("/"))-1])+"/"

def main():
    url = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3206"
  
    baseurl = get_base_url(url)

    content = load_page_content(url)

    cities = dict()

    nalezeno = content.find_all("td", {"class": "overflow_name"})
    links = content.find_all("td", {"class": "cislo"})

    for city, link in zip(nalezeno, links):
        cities[link.get_text()] = (city.get_text(), link.find_all('a', href=True)[0]['href'])

    final_results = dict()

    for city, (city_name, link) in cities.items():
        # print(f"Obec: {obec_nazev}, cislo obce: {obec}")

        city_content = load_page_content(baseurl + link)

        registered = int(city_content.find_all("td", {"class": "cislo", "headers": "sa2"})[0].get_text().replace("\xa0", ""))
        envelopes = int(city_content.find_all("td", {"class": "cislo", "headers": "sa3"})[0].get_text().replace("\xa0", ""))
        valid = int(city_content.find_all("td", {"class": "cislo", "headers": "sa6"})[0].get_text().replace("\xa0", ""))

        # print(f"Volicu: {volicu}, obalek: {obalek}, platne: {platne}")

        parties = dict()

        party_number = city_content.find_all("td", {"class": "cislo", "headers": re.compile(r't[1|2]sa1 t[1|2]sb1')})
        party_name = city_content.find_all("td", {"class": "overflow_name", "headers": re.compile(r't[1|2]sa1 t[1|2]sb2')})
        total_votes = city_content.find_all("td", {"class": "cislo", "headers": re.compile(r't[1|2]sa2 t[1|2]sb3')})

        for number, party, votes in zip(party_number, party_name, total_votes):
            parties[int(number.get_text().replace("\xa0", ""))] = (party.get_text(), int(votes.get_text().replace("\xa0", "")))

        final_results[city] = {"location": city_name, "registered": registered, "envelopes": envelopes, "valid": valid, "parties_votes": parties}

    # pprint.pprint(final_results)

    parties = set()

    for item in final_results:
        parties.update([(k, n[0]) for k, n in zip(final_results[item]["parties_votes"].keys(), final_results[item]["parties_votes"].values())])

    for city in final_results:
        for party in sorted(parties):   # order by party number
            if party[0] not in final_results[city]["parties_votes"]:
                final_results[city]["parties_votes"][party[0]] = (party[1], 0) # add missing party with 0 votes

    for city in final_results: # flatten party votes into main dictionary
        party_votes = final_results[city].pop("parties_votes")
        final_results[city].update(dict([party for party in party_votes.values()]))

    # pprint.pprint(final_results)

    with open('result.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['code'] + list(list(final_results.values())[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for city, data in final_results.items():
            writer.writerow({'code': city, **data})

main()