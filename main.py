import threading # Allow to run scheduler
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import urllib.request
import time
from html_table_parser.parser import HTMLTableParser


# Required becasue libraly htmlparser have problems
import collections.abc
collections.Callable = collections.abc.Callable


time_scheduler = 3600 # How frequently scheduler should validate data (In seconds)
cachedata = [
    {}
]

classtoScrap = []

class scraping:
    def __init__(self):
        self.soup = None
        self.response = None
        self.content_div = None
        self.url = ""
        self.plan = ""
        self.plan_path = ""
        self.cache = Caching(self)

    def GetPLanUrl(self):
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

        for a in self.soup.find_all("a", href=True):
            if a.find("img", alt="Plan lekcji") or a.find("span", string="Plan zajęć"):
                self.plan = a["href"]
                print(f"dasa {self.plan}")
                print(a["href"])
                return self.plan
        for a in self.soup.find_all("a"):
            if a.get_text(strip=True) == "Plan zajęć":
                self.plan = a["href"]
                return self.plan


    def GetClassReference(self):
        self.response = requests.get(self.plan)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        self.content_div = self.soup.find('a', string="Oddziały")

        if self.content_div["href"]:
            result = f"{self.plan}/{self.content_div['href']}"
            self.plan_path = result
            print(result)
            return result

    def GetClassPlan(self, whichclass):
        if len(self.url) < 1:
            print("url is empty")
            return None
        self.cache.CheckIfUrlisCache()
        planurl = self.plan_path
        if planurl == None:
            return None
        try:
            self.response = requests.get(planurl)
        except requests.exceptions.ConnectionError:
            print("Check your internet connection")
            return None


        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        self.content_div = self.soup.find('a', string=whichclass)
        if self.content_div and self.content_div.get("href"):
            href = self.content_div["href"]
            full_url = f"{self.plan}/{href}"
            format = Format()
            data = format.Formatdata(fulurl=full_url)
            addtocache(whichclass=whichclass, data=data)
            return data
        else:
            print(
                f"Class {whichclass} don't exist in this system"
                "if you sure that it exist create an issue on our github"
            )
            return None
class Format:

    def __init__(self):
        self.table = None
        self.data = None
        self.p = None
        self.xhtml = None
        self.cache = Caching

    def Formatdata(self,fulurl):

        def url_get_contents(url):
            req = urllib.request.Request(url=url)
            f = urllib.request.urlopen(req)
            return f.read()

        self.xhtml = url_get_contents(fulurl).decode('utf-8')
        self.p = HTMLTableParser()
        self.p.feed(self.xhtml)

        self.table = self.p.tables[1]
        return self.table

class Caching:
    def __init__(self, scraper):
        self.scraper = scraper

    def CheckIfUrlisCache(self):
        if len(self.scraper.plan) <= 5:
            print("Url of site was not cached")
            self.scraper.GetPLanUrl()
            print(f"Now cached : {self.scraper.plan}")
        if len(self.scraper.plan_path) <= 5:
            print("Url of site was not cached")
            self.scraper.GetClassReference()
            print(f"Now cached : {self.scraper.plan_path}")

times = 0
scrap = scraping()
app = Flask(__name__)

@app.route("/")
def home():
    if checkifdatawasscraped("1I"):
        print("test")
        return jsonify(cachedata[0]["1I"])
    start = time.perf_counter()
    data = scrap.GetClassPlan("1I")
    if data is None:
        return "Not found"
    elapsed = time.perf_counter() - start
    global times
    times += 1
    print(f"time for execution {elapsed:.4f}")
    return jsonify(cachedata[0]["1I"])

@app.route("/<item_id>")
def home_with_id(item_id: str):
    global times

    if item_id == "about":
        return (
            {
                "author": "Trabage",
                "Maintainer": "Trabage",
                "Suggestion": "k2gemer",
            }
        )
    elif item_id == "info":
        return (
            {
                "version": "Python 3.12.5",
                "modules": "requests, bs4, flask, urllib, time, html_table_parser, collections",
                "Maintainer": "Trabage"
            }
        )
    elif item_id == "data":
        return (
            {
                "cached_url": scrap.plan,
                "cached_path": scrap.plan_path,
                "main_url": scrap.url,
                "times": times,
            }

        )
    elif item_id == "cache":
        return cachedata[0]

    if checkifdatawasscraped(item_id):
        data = cachedata[0][item_id.upper()]
        return jsonify(data["data"])

    start = time.perf_counter()
    table = scrap.GetClassPlan(item_id.upper())
    if table is None:
        return f"Plan for class {item_id} not found"
    elapsed = time.perf_counter() - start
    times += 1
    addtocache(whichclass=item_id, data=table)
    return jsonify(table)



# Type is predefine to elimate problems with types
# I don't like dynamic typing

def addtocache(whichclass: str, data: dict):
    if whichclass.upper() not in classtoScrap:
        classtoScrap.append(whichclass.upper())
        print(classtoScrap)
    cachedata[0][str(whichclass).upper()] = {"data": data} # Adding to cache

def checkifdatawasscraped(klasaa: str) -> bool:
    return str(klasaa).upper() in cachedata[0] # Returing Boolean

def CheckIfClaasesAreUpToDate():
    while True:
        if len(classtoScrap) < 1:
            time.sleep(time_scheduler)
        else:
            for i in classtoScrap:
                table = scrap.GetClassPlan(i.upper())
                cachedata[0][str(i.upper())] = {"data": table}
                print(f"Updated class {i.upper()}")
                print(f"Next scheduler update in {time_scheduler} seconds")
                time.sleep(time_scheduler)
                time.sleep(10)
            print(f"Next scheduler update in {time_scheduler} seconds")
            time.sleep(time_scheduler)




if __name__ == "__main__":
    threading.Thread(target=CheckIfClaasesAreUpToDate, daemon=True).start() # Running async not blocking main thread
    app.run()