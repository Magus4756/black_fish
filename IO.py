import csv
from page_detect import page_detect
from black_download import black_download
from black_match import black_match
from url_model import URLmodel

def url_write(result,str,word):
    if result==1:
        formal = open('formal.csv', 'a', newline='')
        formal_writer = csv.writer(formal)
        formal_writer.writerow([str])
        formal.close()
    elif result==0:
        phishweb = open('phishweb.csv', 'a', newline='')
        phishweb_writer = csv.writer(phishweb)
        phishweb_writer.writerow([str])
        phishweb.close()
    elif result==0.5:
        doubt = open('new_doubt.csv', 'a', newline='')
        doubt_writer = csv.writer(doubt)
        doubt_writer.writerow([str,word])
        doubt.close()
    else:
        print("Wrong url result write in!!!\n")


def page_write(result,str):
    if result==1:
        formal = open('formal.csv', 'a', newline='')
        formal_writer = csv.writer(formal)
        formal_writer.writerow([str])
        formal.close()
    elif result==-1:
        phishweb = open('phishweb.csv', 'a', newline='')
        phishweb_writer = csv.writer(phishweb)
        phishweb_writer.writerow([str])
        phishweb.close()
    else:
        print("Wrong url result write in!!!\n")

def detect(url,urlM):
        result = black_match(url)
        if result == 1 or result == -1:
            return result,1
        elif result == 0:
            print(url, "is detecting URL...")
            result, word = urlM.url_predict(url)
            if result == 0:
                urlM.append_sus(word)
                return -1,2
            elif result == 1:
                return result,2
            elif result == 0.5:
                print(url, "is detecting page...")
                result = page_detect(url)
                if result == 1:
                    return result,3
                elif result == -1:
                    urlM.append_sus(word)
                    return result,3
                else:
                    print("Page detect error!")
            else:
                print("URL detect error!")
        else:
            print("Black match error!")
        return -2,0

