import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import urllib.request
from html_table_parser.parser import HTMLTableParser

# Required becasue libraly htmlparser have problems
import collections.abc
collections.Callable = collections.abc.Callable

class scraping:
    def __init__(self):
        self.soup = None
        self.response = None
        self.content_div = None
        self.url = ""
        self.plan = ""
        self.plan_path = ""

    def GetPLanUrl(self):
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

        for a in self.soup.find_all("a", href=True):
            if a.find("img", alt="Plan lekcji") or a.find("span", string="Plan lekcji"):
                self.plan = a["href"]
                print(a["href"])
                return self.plan

    def GetClassReference(self):
        self.response = requests.get(self.plan)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        self.content_div = self.soup.find('a', string="Oddziały")
        if self.content_div["href"]:
            result = f"{self.plan + "/" + self.content_div["href"]}"
            self.plan_path = result
            return result

    def GetClassPlan(self, whichclass):
        if len(self.url) < 1:
            return None
        cache.CheckIfUrlisCache()
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
    def CheckIfUrlisCache(self):
        if len(scrap.plan) <= 5:
            print("Url of site was not cached")
            scrap.GetPLanUrl()
            print(f"Now cached : {scrap.plan}")
        if len(scrap.plan_path) <= 5:
            print("Url of site was not cached")
            scrap.GetClassReference()
            print(f"Now cached : {scrap.plan_path}")

scrap = scraping()
cache = Caching()
app = Flask(__name__)
@app.route("/")
def home():
    data = scrap.GetClassPlan("1I")
    if data is None:
        return "Not found"
    return jsonify(data.table)

@app.route("/<id>")
def home_with_id(id):
    full_url = scrap.GetClassPlan(str(id).upper())
    if full_url is None:
        return f"Plan for class {id} not found"
    return jsonify(full_url.table)

if __name__ == "__main__":
    app.run()