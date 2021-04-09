# yahoo-answer-backup
#### Yahoo 知識+備份

A python 3.6 code to scraping yahoo answers before it closed using proixy

## Usage

* 1.install requirments.txt (Flask,requests,Beautifulsoup)
* 2.Create sqlite3 db file via create_db.py
* 3.Move db file to your desired prosition
* 4.Modify the program (near the end) to let program know what is the location of database file
  * Note that you may provided a full path, otherwise it will have unknown error
  * ```  yahoo1=yahoo("<your_db_file_here>")``` 
* 5.Find approtate proxies (see below)
* 6.Create a file call yahoo_url_list1.txt (you can download sample)
* 7.Create a file call keyword.txt (you can download sample)
* 8.Run Program

## About Proxies
You can found proxies via different websites

* http://www.freeproxylists.net/
* https://free-proxy-list.net/
* https://spys.one/en/
* https://www.proxy-list.download/HTTPS
* http://spys.me/proxy.txt

and many others....

You must definied at least one proxy in the code,
Proxies stored in list, edit your prefered peoxies.
``` 
proxies=[
"127.0.0.1:1000"
]
``` 

## Others
If you found any bug, please open a issue, thanks!

A flask UI will be provided soon!
