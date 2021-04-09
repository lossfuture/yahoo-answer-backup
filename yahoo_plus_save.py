'''
Yahoo Plus Saver
Copyright 2021 LossFuture
Public Version 1.0 9/4/2021
'''
import requests
import json
import re
import time
import sys
import sqlite3
from bs4 import BeautifulSoup
import urllib.request
from itertools import cycle

#https://github.com/lossfuture/yahoo-answer-backup


#add your perferred proxies here
proxies=[

"127.0.0.1:1000",
"127.0.1.2:4000"

]

proxy_pool = cycle(proxies)

class yahoo:
    def __init__(self,logfile_name,dbpath):
        dbpath='''file:{}?mode=rw'''.format(dbpath)
        self.conn = sqlite3.connect(dbpath,uri=True)
        self.c = self.conn.cursor()
        self.logfile_name="yahoo_plus.log"
        self.requests_cnt=0
        self.https_proxy=proxies[0]

    @staticmethod
    def convert_tf(d):
        if d is True:
            return 1
        else:
            return 0
    @staticmethod
    def _curtime():
        return time.strftime("%d/%m/%Y %H:%M:%S")

    def printtext(self,string,wt=False): #wt =withtime
        '''Print text to screen and log file'''
        if wt is True:
            str1="{0} : {1}".format(self._curtime(),string)
            try:
                print(str1)
            except UnicodeEncodeError:
                print("{0} : UnicodeEncodeError, String Contains Non-BMP character".format(self._curtime()))
            #print("{0} : {1}".format(time.strftime("%d/%m/%Y %H:%M:%S"),string),file= open(self.logfile_name, "a"))
            print(str1,file= open(self.logfile_name, "a",encoding="utf8"))
        else:
            try:
                print(string)
            except UnicodeEncodeError:
                print("{0} : UnicodeEncodeError, String Contains Non-BMP character".format(self._curtime()))

            print(string,file= open(self.logfile_name, "a",encoding="utf8"))

    def printtolog(self,string,wt=False): #wt =withtime
        '''Print text to log file only'''
        if wt is True:
            print("{0} : {1}".format(time.strftime("%d/%m/%Y %H:%M:%S"),string),file= open(self.logfile_name, "a",encoding="utf8"))
        else:
            print(string,file= open(self.logfile_name, "a",encoding="utf8"))

    def fetchdata_nomapping(self, sql,arg=None):
        '''Get data from database, return a list without column name'''
        if arg is None:
            self.c.execute(sql)
        else:
            self.c.execute(sql,arg)
        b=self.c.fetchall()
        return b

    def parse_file(self,file):
        a_file = open(file, "r",encoding="utf8")
        list_of_lists = []
        for line in a_file:
            stripped_line = line.strip()
            if stripped_line[0] =="#": #skip with sharp symbol
                continue
            if len(stripped_line)==0:
                continue
            line_list = stripped_line.split(",")
            list_of_lists.append(line_list)
        a_file.close()
        return list_of_lists

    def remove_preferences_page(self,soup):
        self.printtext("I hate this!!!",wt=True)
        calcal=soup.find(id='pref')
        calcal=calcal.find(class_='left')
        calcal=calcal.find("a").get("href")
        #calcal=
        return calcal


    def new_request(self,url):
        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}

        print("Current proxies",self.https_proxy,"used for",self.requests_cnt,"times")

        if self.requests_cnt>22000:
            self.https_proxy=next(proxy_pool)
            self.printtext("Using proxy {}".format(self.https_proxy),wt=True)
            self.requests_cnt=0
        while True:
            try:
                proxyDict = {"http"  : self.https_proxy, "https" : self.https_proxy}
                response = requests.get(url,allow_redirects=True,proxies=proxyDict)
                self.requests_cnt+=1
                break
            except TimeoutError:
                self.printtext("TimeoutError: Connection Timeout",wt=True)
                time.sleep(10)
            except requests.exceptions.ProxyError as err:
                #OSError: Tunnel connection failed: 504 Couldn't connect: Connection refused
                self.printtext(("Proxy Error:", err),wt=True)
                self.printtext("Proxy {} used for {} times".format(self.https_proxy,self.requests_cnt),wt=True)
                time.sleep(10)
                self.https_proxy=next(proxy_pool)
                self.printtext("Using next proxy:{}".format(self.https_proxy),wt=True)
                self.requests_cnt=0
            except requests.exceptions.SSLError as err:
                self.printtext(("SSL Error:", err),wt=True)
                self.https_proxy=next(proxy_pool)
                self.printtext("Using next proxy:{}".format(self.https_proxy),wt=True)
                self.requests_cnt=0

        if response.status_code == 404:
            self.printtext("Error 404 for: {}".format(url),wt=True)
            return None

        if response.status_code != 200:
            self.printtext("HTTP Error {} ".format(response.status_code),wt=True)
            print(url,file= open("yahoo_error_url.txt", "a",encoding="utf8"))
            return None
        #response.raise_for_status()
        for resp in response.history:
            print(resp.status_code, resp.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def insert_category_data(self,data):
        data=data["itemListElement"]
        flevel=data[0]["item"]
        cat_url00=re.split('\/|\?|\=|\&',flevel)
        cat_id00=cat_url00[6]
        for i in data:
            cat_url=re.split('\/|\?|\=|\&',i["item"])
            cat_id=cat_url[6]
            #print(cat_id)
            level=i["position"]
            if level ==1:
                self.c.execute('''INSERT OR IGNORE INTO category (catid,level,catname) VALUES(?,?,?)''',(cat_id,level,i["name"]))
            else:
                self.c.execute('''INSERT OR IGNORE INTO category (catid,level,cat_parentid,catname) VALUES(?,?,?,?)''',(cat_id,level,cat_id00,i["name"]))

        self.conn.commit()
        return data[-1]["item"]

    def insert_data(self,oldqid,newqid,cat_id,data,user_url):
        try:
            data=data["mainEntity"]
        except KeyError:
            return

        title=data["name"]
        content=data["text"]
        ansc=data["answerCount"]
        date=data["dateCreated"]
        author_t=data["author"]["@type"]
        author_n=data["author"]["name"]

        if not oldqid:
            self.printtext("Insert {}, question:{}".format(newqid,title),wt=True)
        else:
            self.printtext("Insert {}/{}, question:{}".format(newqid,oldqid,title),wt=True)

        self.c.execute('''INSERT OR REPLACE INTO question (newqid,oldqid,category_id,title,content,answercount,datecreated,author_type,author_name,author_link) VALUES(?,?,?,?,?,?,?,?,?,?)''',(newqid,oldqid,cat_id,title,content,ansc,date,author_t,author_n,user_url[0]))

        user_urlpos=1

        if "acceptedAnswer" in data:
            data2=data["acceptedAnswer"]
            content2=data2["text"]
            date2=data2["dateCreated"]
            author_t2=data2["author"]["@type"]
            author_n2=data2["author"]["name"]
            upvote_c2=data2["upvoteCount"]

            rows2=self.fetchdata_nomapping("SELECT 1 FROM answers WHERE answer=? AND author_name=? AND datecreated=? LIMIT 1",(content2,author_n2,date2))
            if len(rows2)==1:
                pass
            else:
                self.c.execute('''INSERT OR IGNORE INTO answers (question_id,is_accepted,answer,datecreated,author_type,author_name,author_link,upvotecount) VALUES(?,?,?,?,?,?,?,?)''',(newqid,1,content2,date2,author_t2,author_n2,user_url[user_urlpos],upvote_c2))
            user_urlpos+=1;

        if data["suggestedAnswer"]:
            for i in data["suggestedAnswer"]:
                content2=i["text"]
                date2=i["dateCreated"]
                author_t2=i["author"]["@type"]
                author_n2=i["author"]["name"]
                upvote_c2=i["upvoteCount"]

                rows2=self.fetchdata_nomapping("SELECT 1 FROM answers WHERE answer=? AND author_name=? AND datecreated=? LIMIT 1",(content2,author_n2,date2))
                if len(rows2)==1:
                    user_urlpos+=1;
                    continue

                self.c.execute('''INSERT OR IGNORE INTO answers (question_id,is_accepted,answer,datecreated,author_type,author_name,author_link,upvotecount) VALUES (?,?,?,?,?,?,?,?)''',(newqid,0,content2,date2,author_t2,author_n2,user_url[user_urlpos],upvote_c2))
                user_urlpos+=1;

        self.conn.commit()
        self.printtext("Answer Count: {}".format(ansc),wt=True)
        #self.printtext("Insert {} completed".format(newqid),wt=True)
        return

    def parsing_area(self,link):
        #https://hk.answers.yahoo.com/question/index?qid=20210405072002AAPcNek
        self.printtext(link,wt=True)

        spilited_url=re.split('\/|\?|\=|\&',link)
        questionid=spilited_url[6]
        rows2=self.fetchdata_nomapping("SELECT 1 FROM question WHERE newqid=? LIMIT 1",(questionid,))
        rows3=self.fetchdata_nomapping("SELECT 1 FROM question WHERE oldqid=? LIMIT 1",(questionid,))
        if len(rows2)>0 or len(rows3)>0:
            self.printtext("Already fetched, skip request",wt=True)
            return

        soup=self.new_request(link)
        if soup is None:

            return


        #print response into a html
        #print(soup.prettify(),file= open(questionid+".html", "w",encoding="utf8"))
        script = soup.find_all('script', type=["application/ld+json"])
        new_qid=soup.find("meta",  property="og:url")
        #print(new_qid["content"] if new_qid else "No meta url given")
        spilited_url=re.split('\/|\?|\=|\&',new_qid["content"])
        new_questionid=spilited_url[6]

        if questionid==new_questionid:
            questionid=None

        user_url_soup=soup.find_all("div", class_="UserProfile__avatar___2gI-3")
        user_url=[]
        for k in user_url_soup:
            try:
                p=k.find("a").get("href")
                spilited_url=re.split('\/|\?|\=|\&',p)
                user_url.append(spilited_url[4])
                #print(k.find("a").get("href"))
            except AttributeError:
                user_url.append(None)







        json1=json.loads(script[0].contents[0])
        json2=json.loads(script[1].contents[0])

        #print(json1)

        #print(json2)

        cat_url=self.insert_category_data(json1)
        cat_url=re.split('\/|\?|\=|\&',cat_url)
        cat_id=cat_url[6]

        self.insert_data(questionid,new_questionid,cat_id,json2,user_url)
        time.sleep(3)
        return


    def mainloop(self,txt_file):
        #self.printtext("Start",wt=True)
        self.printtolog("\n{:=^60}".format("Python Start"))
        list_of_lists=self.parse_file(txt_file)
        #a_file = open(txt_file, "r")
        #list_of_lists = []
        #for line in a_file:
    #        stripped_line = line.strip()
    #        if stripped_line[0] =="#": #skip with sharp symbol
    #            continue
    #        if len(stripped_line)==0:
    #            continue
    #        line_list = stripped_line.split()
    #        list_of_lists.append(line_list)
    #    a_file.close()

        for i in list_of_lists:
            self.parsing_area(i[0])

        self.printtext("Insert Complete",wt=True)
        return


    def search(self,line):
        keyword=line[0]
        try:
            start_pos=int(line[1])*10-9
            batch=int(line[1])-1
        except:
            start_pos=0
            batch=0

        self.printtolog("Keyword :{}".format(keyword))

        url="https://hk.knowledge.search.yahoo.com/search?ei=UTF-8&vm=r&rd=r1&fr=FP-tab-web-t&p={}&b={}".format(urllib.parse.quote_plus(keyword),start_pos)
        #print(url)



        while True:
            if batch>=102: #unkwown error for cannot browse page 102
                break
            batch+=1
            self.printtext("Batch {}:{}".format(batch,url),wt=True)

            soup=self.new_request(url)

            results=soup.find(id='web')
            if results is None:
                url=self.remove_preferences_page(soup)
                batch-=1
                continue
            results=results.find('ol')
            results=results.find_all("li")
            for i in results:
                link=i.find("a").get("href")
                self.parsing_area(link)

            next_page=soup.find("ol",class_='searchBottom')
            try:
                url=next_page.find("a",class_='next').get("href")
            except AttributeError:#no next page
                break

        #self.printtext("Searching completed")
        self.printtolog("\n{:=^60}".format("Searching {} completed".format(keyword)))
        return

    def search_loop(self,keywordstxt):
        self.printtolog("\n{:=^60}".format("Python Start"))
        keywords=self.parse_file(keywordstxt)
        #print(keywords)
        for i in keywords:
            self.search(i)
            time.sleep(20)


def start():
    #db file here
    yahoo1=yahoo("<your_db_file_here>") #dont remove this line
    #yahoo1.mainloop("yahoo_url_list1.txt")
    yahoo1.search_loop("keywords.txt")


if __name__ == '__main__':
    start()
