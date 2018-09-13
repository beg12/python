""" Brian Goldsberry beg12 """
from __future__ import print_function
import re, requests

url = "http://www.cs.fsu.edu/department/faculty/"
#collects links from main site
def get_links():
    links = []
    main_page = requests.get(url)
    allLinks = re.findall(r"<td style=\"text-align: center;\"><a href=(.+)><img", main_page.text)
    for i in range(len(allLinks)):
        allLinks[i] = str(allLinks[i])
    return allLinks
#find info about a faculty member given their link
def print_info(link):
    link = link.replace('"', '')
    faculty_page = requests.get(link)
    name = re.search(r"<h1 class=\"(main_title\">|js-quickedit-page-title page-header\"><span>)(.+)</(h1>|span>)", faculty_page.text)
    if name:
        print ("Name: " + name.group(2))
    else:
        print ("Name: N/A")

    office = re.search(r"<(td><strong>Office:</strong></td>\n<td>|div class=\"field field--name-field-office-location field--type-string field--label-hidden field--item\">)(.+)</(td>|div>)", faculty_page.text, re.M)
    if office:
        print ("Office: " + office.group(2))
    else:
        print ("Office: N/A")

    phone = re.search("(<td><strong>Telephone:</strong></td>\n<td>|Phone</div>\\n              <div class=\"field--item\">)(.+)</(td>|div>)", faculty_page.text, re.M)
    if phone:
        print ("Telephone: " + phone.group(2))
    else:
        print ("Telephone: N/A")

    email = re.search("<((td valign=\"top\"><strong>E-Mail:</strong></td>\n<td>)|(div class=\"field field--name-field-email field--type-email field--label-hidden field--item\"><a href=\"mailto:))(.+?)(\">|</)", faculty_page.text, re.M)
    if email:
        print ("E-Mail: " + email.group(4))
    else:
        print ("E-Mail: N/A")

    print ("****************************************")

if __name__ == "__main__":
    faculty = get_links()
    for i in faculty:
        print_info(i)
