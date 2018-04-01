"""
# STILL TESTING!!!!
DOI download from academic papers and put in a csv file for processing for meta analyses.
22-01-18, using threading
seem to work: 10 seconds for 23 references using 4 workers
      7 seconds for 23 references using 6 workers
      104 seconds for 363 references (from Vachon, 2014)

28-01-18: using google scholar, it doesn't work due to blocking. Gets blocked after a while. 
02-02-18: User_Agent added (line 33). Doesn't seem to make the difference...

"""


import time, logging, requests, re
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures

#Constants:
regex= r"""\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b"""            # regex string voor DOI
columns=['Meta_Doi','Title', 'Authors', 'Pub_Year', 'Journal', 'Downl_DOI' ]    # column names for dataframe
df=pd.DataFrame(columns=columns)                                                # and create the dataframe
csv_file="meta analyse extracted doi's.csv"
Error_list=[] # list for failed doi's to put in seperate file to review in person
Error_count=0 # counter to count failed dois for logging
output_file= 'C:\\Users\\Remy Hertogs\\Documents\\Python Scripts\\Parallel Programming\\DOI extract\\Vachon 2014.txt_DOI.txt'
with open (output_file,'r') as f:
    DOI_LIST= f.readlines()

# headers for webscraper (test)
USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
 

# classes and functions
class WebsiteDownException(Exception):
    pass
 
 
def Downl_doi(doi, timeout=20):
    """
    Check if a website is down. A website is considered down 
    if either the status_code >= 400 or if the timeout expires
     
    """
    global df, Error_list, Error_count
    
    try:
        doi=doi.strip()
        time.sleep(4.0) # added a second for waiting time, to see if that allows us to crawl google.scholar. It doesn't..
        url1="https://scholar.google.nl/scholar?hl=nl&as_sdt=0%2C5&q="  # eerste deel url wegens de %2
        url=url1+"%s&btnG=" % doi                                       # tweede deel url incl doi en deel wat erachter komt bij google
        page=requests.get(url,headers=USER_AGENT).text
        soup=BeautifulSoup(page, "html.parser")

        title= soup.find(class_='gs_rt').text
        citation= soup.find(class_='gs_a').text
        various=soup.find(class_='gs_rs').text

        # seperating authors, journal, year from citation string
        # example = N Eisenberg, PA Miller - Psychological bulletin, 1987 - doi.apa.org
        # divide citation up [0] for authors, [1[0]] journal, and [1[1]] year (second element of second element journal)
        citation=citation.split('-') # citation divided:

        # author
        try:
            author=citation[0].split(',')
            author[-1]=author[-1].replace(u'\xa0', u'') # get rid of the weird latin-unicode symbols, statement not always needed, but doesnt (seem) do harm
            author=', '.join(author)

            # journal (citation[1]) and year (citation[1[1]])
            journal=citation[1].split(',') # results: journal, year
            pub_year=journal[1].strip()
            journal=journal[0].strip()
            #journal[-1]=journal[-1].replace(u'\xa0', u'')
        
            df=df.append({'Meta_Doi': doi, 'Title': title, 'Authors': author, 'Pub_Year': pub_year, 'Journal': journal, 'Downl_DOI': "n/a"}, ignore_index=True)
            print("Append to dataframe with doi: {}".format(doi))
            df.to_csv(csv_file, encoding='utf-8')
        except IndexError as e:
            doi=doi.strip()
            doi= ("{} might contain problems while resolving author, journal, or publication year. \n".format(doi))
            Error_count += 1 
            Error_list.append(doi)
            pass
                        
    except requests.exceptions.RequestException:
        logging.warning("Timeout expired for website %s" % doi)
        raise WebsiteDownException()
            
    except AttributeError:
        doi="{} not found on google.scholar. \n".format(doi)
        Error_count += 1
        Error_list.append(doi)
        pass
    
          
def notify_owner(doi):
    """ 
    Send the owner of the address a notification that their website is down 
     
    wait 0.5 sec
    """
    logging.info("Notifying the owner of %s website" % doi)
    time.sleep(0.5)
    
 
def check_website(doi):
    """
    Utility function: check if a website is down, if so, send notification
    """
    try:
        Downl_doi(doi)
    except WebsiteDownException:
        logging.info("Website seems to be down. THEY ARE ON TO YOU!!")


###
###
### THREADING
###
###
from queue import Queue
from threading import Thread

NUM_WORKERS = 4  # NON-LINEAR!! Double the workers does not halve the time!
task_queue = Queue()
 
def worker():
    # Constantly check the queue for addresses
    while True:
        doi = task_queue.get()
        check_website(doi)
         
        # Mark the processed task as done
        task_queue.task_done()
 
start_time = time.time()
         
# Create the worker threads
threads = [Thread(target=worker) for _ in range(NUM_WORKERS)]
 
# Add the websites to the task queue
[task_queue.put(item) for item in DOI_LIST]
 
# Start all the workers
[thread.start() for thread in threads]
 
# Wait for all the tasks in the queue to be processed
task_queue.join()
 
         
end_time = time.time()        

#####
##### LOGGING
#####
logging.info("Time for ThreadedSquirrel: %ssecs" % (end_time - start_time))
logging.info("There were {} unresolved doi's \n".format(Error_count))
with open ("logfile.txt", "a", encoding="utf-8") as f:
    if (len(Error_list) > 0):
        for Error in Error_list:
            f.writelines(Error)
    else:
        f.writelines("No unresolved doi's \n")
    f.close()
print("Logfile created with {} doi's unresolved".format(Error_count))
        
