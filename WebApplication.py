# GOOGLE SCHOLAR PROFILE DETAIL EXTRACTOR
# WEB CONSULTATION TEAM - UOP
# PREREQUISITES:
#   1) Python 3.x
#   2) INSTALL LIBRARIES requests, lxml AND beautifulsoup4
#   3) INSTALL Flask web framework

from flask import Flask, render_template, request, redirect, url_for, send_file
import sys
import requests
from bs4 import BeautifulSoup
import csv

NEXTPAGE_BUTTON_CLASSNAME = 'gs_btnPR gs_in_ib gs_btn_half gs_btn_lsb gs_btn_srt gsc_pgn_pnx'
CITATION_CLASSNAME = 'gs_ai_cby'
INSTITUTE_URL_PORTION = "https://scholar.google.com/citations?view_op=view_org&hl=en&org="
PROFILE_CARD_CLASSNAME = 'gs_ai_t'
EMAIL_CLASSNAME = 'gs_ai_eml'

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        # OPTION 1 : SINGLE OUTPUT
        if request.form.get("submit_url"):
            url = request.form['url1']
            return redirect(url_for("output", key=get_key(url)))

        # OPTION 2 : DEFAULT OUTPUT
        elif request.form.get("view_all"):
            return redirect(url_for("default_output"))

        # OPTION 3 : PROFILE DETAILS FILE GENERATION
        else:
            url = request.form['url2']
            return redirect(url_for("generate_csv", key=get_key(url)))

    else:
        return render_template('home.html')


@app.route('/output/<key>')
def output(key):

    message = print_total_citations(INSTITUTE_URL_PORTION+key)
    return render_template('output.html', output=message)


# INCLUDE ADDITIONAL INSTITUTIONS FOR THE DEFAULT OUTPUT, BY EXTENDING THE FOLLOWING LIST
institutions = [
    # University of Peradeniya
    'https://scholar.google.com/citations?view_op=view_org&hl=en&org=12610868586512439209',
    # University of Colombo
    'https://scholar.google.com/citations?view_op=view_org&hl=en&org=15232608093574943961',
    # University of Kelaniya
    'https://scholar.google.com/citations?view_op=view_org&hl=en&org=2389008742073115052',
    # University of Moratuwa
    'https://scholar.google.com/citations?view_op=view_org&hl=en&org=1702257947625510955',
    # University of Sri Jayewardenepura
    'https://scholar.google.com/citations?view_op=view_org&hl=en&org=4241313714207127809'
]


@app.route('/default')
def default_output():

    message = ""
    for institution in institutions:
        message += print_total_citations(institution)
    return render_template('output.html', output=message)


@app.route('/csv/<key>')
def generate_csv(key):

    # GENERATES THE CSV FILE AND SENDS IT TO THE CLIENT

    filename = print_total_citations_csv(INSTITUTE_URL_PORTION+key)
    return send_file(filename, as_attachment=True, cache_timeout=0)


def get_key(url):

    # RETURNS THE LAST POSTION OF THE URL; i.e. 12610868586512439209 FOR;
    # https://scholar.google.com/citations?view_op=view_org&hl=en&org=12610868586512439209

    s = url.split("=")
    return s[-1]


def get_soup(url):

    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    return soup


def get_nextpage(homepage_url, soup, num):

    key = soup.find('button', class_=NEXTPAGE_BUTTON_CLASSNAME).get(
        'onclick').split('\\')[9]

    # GETS THE ID OF THE LAST SCHOLAR OF THE PAGE; i.e. CkZeALfx__8J FOR;
    # https://scholar.google.com/citations?view_op=view_org&hl=en&org=12610868586512439209&after_author=CkZeALfx__8J&astart=10

    next_url = homepage_url+'&after_author='+key[3:]+'&astart='+str(num)
    nextpage_soup = get_soup(next_url)
    return nextpage_soup


def get_citations(soup, file=None):

    # SINCE PYTHON IS DYNAMICALLY TYPED, OPTIONAL ARGUMENTS CAN BE PASSED

    # OPTION 1 : SINGLE OUTPUT AND
    # OPTION 2 : DEFAULT OUTPUT
    if file is None:
        citation_count = 0
        citations = soup.find_all('div', class_=CITATION_CLASSNAME)

        for citation in citations:
            citation_count += int(citation.text.split()[-1])
        return citation_count

    # OPTION 3 : PROFILE DETAILS FILE GENERATION
    else:
        citations = soup.find_all('div', class_=PROFILE_CARD_CLASSNAME)

        # FOR EACH PROFILE CARD...
        for citation in citations:

            name = citation.find('h3').text
            url = 'https://scholar.google.com'+citation.find('a').get('href')
            email = citation.find(
                'div', class_=EMAIL_CLASSNAME).text.split()[-1]

            try:
                cit = citation.find(
                    'div', class_=CITATION_CLASSNAME).text.split()[-1]

            # WHEN THE CITATIONS ARE NOT DISPLAYED...
            except IndexError:
                cit = '0'

            file.writerow((name, email, cit, url))


def is_lastpage(soup):

    if soup.find('div', class_=CITATION_CLASSNAME).text:
        return False
    else:
        return True


def print_total_citations(url):

    page1 = get_soup(url)
    result = ""
    list_ = page1.find('h2').text.split()
    institution = ' '.join(list_[0:-2])
    result = 'Institution &ensp; &ensp; : '+institution+'<br>'

    # SKIPPING FIRST 20 ENTRIES (FIRST 2 PAGES)
    page2 = get_nextpage(url, page1, 10)
    page3 = get_nextpage(url, page2, 20)

    currentpage = page3
    total_citation_count = 0

    # FROM ENTRY 21 TO 210
    for index in range(30, 31, 10):  # 31 < 211
        if is_lastpage(currentpage):
            break
        total_citation_count += get_citations(currentpage)
        currentpage = get_nextpage(url, currentpage, index)

    result += "Total citations : "+str(total_citation_count)+"<br><br>"

    return result


def print_total_citations_csv(url):

    page1 = get_soup(url)
    filename = ""
    list_ = page1.find('h2').text.split()
    institution = ' '.join(list_[0:-2])

    filename = '_'.join(institution.split())+'_Google_Scholar.csv'
    f = open(filename, 'w', newline='', encoding="utf-8")
    file = csv.writer(f)

    file.writerow([institution])
    file.writerow(['Profile', 'Verified Email', 'Citations', 'URL'])

    currentpage = page1
    index = 10

    try:
        while (True):
            get_citations(currentpage, file)
            currentpage = get_nextpage(url, currentpage, index)
            index += 10

    # AFTER THE LAST ENTRY OF THE LAST PAGE...
    except AttributeError:
        f.close()

    return filename


if __name__ == "__main__":
    app.run(debug=True)
