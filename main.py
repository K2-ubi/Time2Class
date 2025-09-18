import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import urllib.request
import time
from html_table_parser.parser import HTMLTableParser

# Required becasue libraly htmlparser have problems
import collections.abc
collections.Callable = collections.abc.Callable

class scraping:
    def __init__(self):
        self.soup = None
        self.response = None
        self.content_div = None
        self.url = "https://tk.krakow.pl/"
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
                print(f"fdsfsdf : {self.plan}")
                return self.plan


    def GetClassReference(self):
        self.response = requests.get(self.plan)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        self.content_div = self.soup.find('a', string="Oddziały")

        if self.content_div["href"]:
            result = f"{self.plan}/{self.content_div['href']}"
            self.plan_path = result
            return result

    def GetClassPlan(self, whichclass):
        if len(self.url) < 1:
            print("url is empty")
            return None
        self.cache.CheckIfUrlisCache()
        planurl = self.plan_path
        if planurl == None:
            return None

        self.response = requests.get(planurl)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        self.content_div = self.soup.find('a', string=whichclass)
        if self.content_div and self.content_div.get("href"):
            href = self.content_div["href"]
            full_url = f"{self.plan}/{href}"
            format = Format()
            return format.Formatdata(fulurl=full_url)
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

    def Formatdata(self,fulurl):

        def url_get_contents(url):
            req = urllib.request.Request(url=url)
            f = urllib.request.urlopen(req)
            return f.read()

        self.xhtml = url_get_contents(fulurl).decode('utf-8')
        self.p = HTMLTableParser()
        self.p.feed(self.xhtml)

        self.table = self.p.tables[1]
        return self

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
    start = time.perf_counter()
    data = scrap.GetClassPlan("1I")
    if data is None:
        return "Not found"
    elapsed = time.perf_counter() - start
    global times
    times += 1
    print(f"time for execution {elapsed:.4f}")
    return jsonify(data.table)

@app.route("/<id>")
def home_with_id(id):
    global times
    if id == "about":
        return (
            {
                "author": "Trabage",
                "Maintainer": "Trabage",
                "Suggestion": "k2gemer",
            }
        )
    elif id == "info":
        return (
            {
                "version": "Python 3.12.5",
                "modules": "requests, bs4, flask, urllib, time, html_table_parser, collections",
                "Maintainer": "Trabage"
            }
        )
    elif id == "data":
        return (
            {
                "cached_url": scrap.plan,
                "cached_path": scrap.plan_path,
                "main_url": scrap.url,
                "times": times,
            }

        )

    start = time.perf_counter()

    full_url = scrap.GetClassPlan(str(id).upper())
    print(scrap.plan_path)
    print(scrap.plan)

    elapsed = time.perf_counter() - start
    print(f"time for execution {elapsed:.4f}")

    if full_url is None:
        return f"Plan for class {id} not found"
    times =+ 1
    return jsonify(full_url.table)

if __name__ == "__main__":
    app.run()