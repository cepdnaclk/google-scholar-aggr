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
        if request.form.get("submit_url"):
            url = request.form['url1']
            return redirect(url_for("output", key=get_key(url)))
        elif request.form.get("view_all"):
            return redirect(url_for("default_output"))
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
    'https://scholar.google.com/citations?view_op=view_org&hl=en&org=1702257947625510955'
]


@app.route('/default')
def default_output():
    message = ""
    for institution in institutions:
        message += print_total_citations(institution)
    return render_template('output.html', output=message)


@app.route('/csv/<key>')
def generate_csv(key):
    filename = print_total_citations_csv(INSTITUTE_URL_PORTION+key)
    return send_file(filename, as_attachment=True, cache_timeout=0)


def get_key(url):
    s = url.split("=")
    return s[-1]


def get_soup(url):

    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    return soup


def get_nextpage(homepage_url, soup, num):

    key = soup.find('button', class_=NEXTPAGE_BUTTON_CLASSNAME).get(
        'onclick').split('\\')[9]
    next_url = homepage_url+'&after_author='+key[3:]+'&astart='+str(num)
    nextpage_soup = get_soup(next_url)
    return nextpage_soup


def get_citations(soup, file=None):

    if file is None:
        citation_count = 0
        citations = soup.find_all('div', class_=CITATION_CLASSNAME)

        for citation in citations:
            citation_count += int(citation.text.split()[-1])
        return citation_count

    else:
        citations = soup.find_all('div', class_=PROFILE_CARD_CLASSNAME)

        for citation in citations:
            name = citation.find('h3').text
            url = 'https://scholar.google.com'+citation.find('a').get('href')
            email = citation.find(
                'div', class_=EMAIL_CLASSNAME).text.split()[-1]
            cit = citation.find(
                'div', class_=CITATION_CLASSNAME).text.split()[-1]
            file.writerow((name, email, cit, url))


def is_lastpage(soup):

    if soup.find('div', class_=CITATION_CLASSNAME).text:
        return False
    else:
        return True


def print_total_citations(url):

    page1 = get_soup(url)
    result = ""
    try:
        list_ = page1.find('h2').text.split()
        institution = ' '.join(list_[0:-2])
        result = 'Institution &ensp; &ensp; : '+institution+'<br>'

        # SKIPPING THE FIRST 20 ENTRIES (FIRST 2 PAGES)
        page2 = get_nextpage(url, page1, 10)
        page3 = get_nextpage(url, page2, 20)

        currentpage = page3
        total_citation_count = 0

        # FROM THE ENTRY 21 TO 210
        for index in range(30, 31, 10):  # 211
            if is_lastpage(currentpage):
                break
            total_citation_count += get_citations(currentpage)
            currentpage = get_nextpage(url, currentpage, index)

        result += "Total citations : "+str(total_citation_count)+"<br><br>"

    except Exception:
        pass
    return result


def print_total_citations_csv(url):

    page1 = get_soup(url)
    filename = ""
    try:
        list_ = page1.find('h2').text.split()
        institution = ' '.join(list_[0:-2])

        filename = '_'.join(institution.split())+'_Google_Scholar.csv'
        file = csv.writer(open(filename, 'w', newline=''))
        file.writerow([institution])
        file.writerow(['Profile', 'Verified Email', 'Citations', 'URL'])

        currentpage = page1
        index = 10

        while (True):
            get_citations(currentpage, file)
            currentpage = get_nextpage(url, currentpage, index)
            index += 10

    except Exception:
        pass

    return filename


if __name__ == "__main__":
    app.run(debug=True)
