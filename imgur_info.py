""" Brian Goldsberry beg12 """
from __future__ import print_function
import requests, re

#function gathers all comments from user, sorts them, and prints out top 5
def get_comments():
    counter = 0
    commentList = []
    username = raw_input("Enter Username: ")
    user_page = requests.get("http://imgur.com/user/" + username)
    #check if web page exists
    if user_page.status_code != 200:
        print("User does not exist.")
        return
    #run loop until an empty page 
    while True:
        comment_page = requests.get("http://imgur.com/user/" + username + "/index/newest/page/" + str(counter) +"/hit.json?scrolling")
        if not comment_page.text:
            if counter == 0:
                print ("User has no comments")
                return
            break
        hashes = re.findall(r"\"hash\":\"([0-9a-zA-Z]+)\",\"caption", comment_page.text)
        points = re.findall(r"\"points\":(-?[0-9]*),\"datetime\"", comment_page.text)
        titles = re.findall(r"\"title\":\"(.+?)\",\"platform\"", comment_page.text)
        dates = re.findall(r"\"datetime\":\"([0-9-]+ [0-9:]+)\",\"parent_id", comment_page.text)
        for i in range(len(hashes)):
            comment = {"hash":str(hashes[i]), "points":int(str(points[i])), "title":str(titles[i]), "date":str(dates[i])}
            commentList.append(comment)
        counter+=1
    commentList.sort(cmp_comments)
    for i in range(5):
        print(str(i+1) + ". " + commentList[i]["hash"])
        print("Points: " + str(commentList[i]["points"]))
        print("Title: " + commentList[i]["title"])
        print("Date: " + commentList[i]["date"] + '\n')
        if i+1 >= len(commentList):
            break
#comparison for comments, used in sort function
def cmp_comments(a, b):
    if a["points"] > b["points"]:
        return -1
    elif a["points"] == b["points"]:
        if a["hash"].lower() > b["hash"].lower():
            return 1
        else:
            return -1
    else:
        return 1
if __name__ == "__main__":
    get_comments()

