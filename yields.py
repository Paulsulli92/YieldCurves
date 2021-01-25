import csv, time, sys, pprint, shutil, json

from botocore.vendored import requests
import xml.etree.ElementTree as ET

from datetime import datetime, date, timedelta


class YieldData(object):
    def __init__(self):
        self.days = {}

    
    def pullData(self, url):
        response = requests.get(url, stream=True)
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()
        for properties in root.findall('{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}content/{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties'):
            items = [prop.text for prop in properties.iter()]
            date = items[2]
            yields = []
            for line in items[3:-1]:
                if line != None:
                    yields.append(float((line)))
                else:
                    yields.append(None)
            self.days[date] = yields

    def getDate(self, date):
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_str = date.strftime("%Y-%m-%dT%H:%M:%S")

        # Try exact date first. If that fails, try previous day.
        if date_str in self.days:
           return self.days.get(date_str)
        date_str = (date - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        if date_str in self.days:
           return self.days.get(date_str)
        date_str = (date - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")
        if date_str in self.days:
           return self.days.get(date_str)
        date_str = (date - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
        if date_str in self.days:
           return self.days.get(date_str)
        date_str = (date - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%S")
        if date_str in self.days:
           return self.days.get(date_str)
        return None

    def queryData(self):
        # Get dates
        now = datetime.today()
        pacific = now - timedelta(hours=8)
        #central = now - timedelta(hours=6)
        #eastern = now - timedelta(hours=5)
        now = pacific
        curves = [
            ['Today'] + self.getDate(now),
            ['Yesterday'] + self.getDate(now - timedelta(days=1)),
            ['Last Week'] + self.getDate(now - timedelta(days=7)),
            ['Last Month'] + self.getDate(now - timedelta(days=30)),
            ['Three Months'] + self.getDate(now - timedelta(days=90)),
            ['Six Months'] + self.getDate(now - timedelta(days=182)),
            ['Nine Months'] + self.getDate(now - timedelta(days=270)),
            ['Twelve Months'] + self.getDate(now - timedelta(days=365)),
            ['Fifteen Months'] + self.getDate(now - timedelta(days=455)),
        ]
        return curves

    def higharts(self, curves):
        ret = []
        for day in curves:
            ret.append({"name": day[0], "data": day[1:]})
        return ret

def lambda_handler(event, context):
    year = datetime.today().year
    y = YieldData()
    #y.pullData('http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?$filter=year(NEW_DATE)%20eq%202018')
    y.pullData(f'http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?$filter=year(NEW_DATE)%20eq%20{year-2}')
    y.pullData(f'http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?$filter=year(NEW_DATE)%20eq%20{year-1}')
    y.pullData(f'http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?$filter=year(NEW_DATE)%20eq%20{year}')
    curves = y.queryData()
    data = y.higharts(curves)
    print(data)
    response = {
        'statusCode': 200,
        'body': json.dumps(data)
    }
    response["headers"] = {
        'Content-Type': 'application/json', 
        'Access-Control-Allow-Origin': '*' 
    }
    
    return response