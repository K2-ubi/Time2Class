import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import urllib.request
from html_table_parser.parser import HTMLTableParser


class scraping:
    def __init__(self):
        self.soup = None
        self.response = None
        self.content_div = None
        self.url = ""
        self.plan = ""

    def GetPLanUrl(self):
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

        for a in self.soup.find_all("a", href=True):
            if a.find("img", alt="Plan lekcji") or a.find("span", string="Plan lekcji"):
                self.plan = a["href"]
                print(a["href"])
                return self.plan

    def GetClassReference(self):
        planurl = scrap.GetPLanUrl()

        self.response = requests.get(planurl)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        self.content_div = self.soup.find('a', string="Oddziały")
        if self.content_div["href"]:
            return f"{planurl + "/" + self.content_div["href"]}"

    def GetClassPlan(self, whichclass):
        planurl = scrap.GetClassReference()

        self.response = requests.get(planurl)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        self.content_div = self.soup.find('a', string=whichclass)

        if self.content_div and self.content_div.get("href"):
            href = self.content_div["href"]
            full_url = f"{self.plan}/{href}"
            print(full_url)
            format = Format()
            format.Formatdata(fulurl=full_url)
            return format.Formatdata(fulurl=full_url)
        else:
            print(
                f"Class {whichclass} don't exist in this system"
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

scrap = scraping()
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
        return f"Plan for {id} class not found"
    return jsonify(full_url.table)

if __name__ == "__main__":
    app.run()