# GOOGLE SCHOLAR PROFILE DETAIL EXTRACTOR
# WEB CONSULTATION TEAM - UOP
# PREREQUISITES:
#   1) Python 3.x
#   2) INSTALL LIBRARIES requests, lxml AND beautifulsoup4
#   3) INSTALL Flask WEB FRAMEWORK

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
LABEL_CLASSNAME = 'gs_ai_one_int'
PAPER_CLASSNAME = 'gsc_a_at'
BACKGROUND_CLASSNAME = 'gsh_csp'
PAPER_LINK_CLASSNAME = 'gsc_oci_title_link'
ABSTRACT_CLASSNAME = 'gsh_small'

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
            # return redirect(url_for("default_output"))
            return redirect(url_for("test"))

        # OPTION 3 : PROFILE DETAILS FILE GENERATION
        elif request.form.get("download_csv"):
            url = request.form['url2']
            return redirect(url_for("generate_csv", key=get_key(url)))

        # OPTION 4 : ARTICLE DETAILS FILE GENERATION
        else:
            url = request.form['url3']
            return redirect(url_for("generate_csv_all", key=get_key(url)))

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


@app.route('/test')
def test():
    message = "test : "
    message += test_method()
    return render_template('output.html', output=message)


@app.route('/csv/<key>')
def generate_csv(key):

    # GENERATES THE CSV FILE AND SENDS IT TO THE CLIENT

    filename = print_total_citations_csv(INSTITUTE_URL_PORTION+key)
    return send_file(filename, as_attachment=True, cache_timeout=0)


@app.route('/csv_all/<key>')
def generate_csv_all(key):

    # GENERATES THE CSV FILE AND SENDS IT TO THE CLIENT

    filename = get_paper_details_csv(INSTITUTE_URL_PORTION+key)
    return send_file(filename, as_attachment=True, cache_timeout=0)


def get_key(url):

    # RETURNS THE LAST POSTION OF THE URL; i.e. 12610868586512439209 FOR;
    # https://scholar.google.com/citations?view_op=view_org&hl=en&org=12610868586512439209

    s = url.split("=")
    return s[-1]


def get_soup(url):

    try:
        html_text = requests.get(url).text
    except requests.exceptions.ConnectionError:
        print('Connection error')
        sys.exit(0)

    soup = BeautifulSoup(html_text, 'lxml')
    return soup


def get_nextpage(homepage_url, soup, num):

    key = soup.find('button', class_=NEXTPAGE_BUTTON_CLASSNAME).get(
        'onclick').split('\\')[9]

    # GETS THE ID OF THE LAST SCHOLAR OF THE PAGE; i.e. CkZeALfx__8J FOR;
    # https://scholar.google.com/citations?view_op=view_org&hl=en&org=12610868586512439209&after_author=CkZeALfx__8J&astart=10

    next_url = homepage_url+'&after_author='+key[3:]+'&astart='+str(num)
    # print(next_url)
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


def get_paper_details(soup, file):

    citations = soup.find_all('div', class_=PROFILE_CARD_CLASSNAME)

    # FOR EACH PROFILE CARD...
    for citation in citations:

        name = citation.find('h3').text
        # print(name)
        url = 'https://scholar.google.com'+citation.find('a').get('href')

        user_page = get_soup(url)

        paper_url_tags = user_page.find_all('a', class_=PAPER_CLASSNAME) # 20 paper urls

        for paper_url_tag in paper_url_tags:
        
            paper_page = get_soup('https://scholar.google.com' + paper_url_tag.get('href'))
            # abstract = paper_page.find_all('div', class_=BACKGROUND_CLASSNAME)

            title = ''
            paper_link = ''
            abstract = ''
            try:
                title = paper_page.find('a', class_=PAPER_LINK_CLASSNAME).text
                # print(title)
                paper_link = paper_page.find('a', class_=PAPER_LINK_CLASSNAME).get('href')
                abstract = paper_page.find('div', class_=ABSTRACT_CLASSNAME).text
            except AttributeError:
                pass

            file.writerow((name, url, title, abstract, paper_link))


""" def is_lastpage(soup):

    if soup.find('div', class_=CITATION_CLASSNAME).text:
        return False
    else:
        return True """


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

    try:
        # FROM ENTRY 21 TO 210
        for index in range(30, 231, 10): #211
            """ if is_lastpage(currentpage):
                break """
            total_citation_count += get_citations(currentpage)
            currentpage = get_nextpage(url, currentpage, index)

    # WHEN THE CITATIONS ARE NOT DISPLAYED...
    except IndexError:
        pass

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


def get_paper_details_csv(url):

    page1 = get_soup(url)
    filename = ""
    list_ = page1.find('h2').text.split()
    institution = ' '.join(list_[0:-2])

    filename = '_'.join(institution.split())+'_Google_Scholar_Papers.csv'
    f = open(filename, 'w', newline='', encoding="utf-8")
    file = csv.writer(f)

    file.writerow([institution])
    file.writerow(['Author', 'Profile URL', 'Title', 'Abstract', 'Paper URL'])

    currentpage = page1

    get_paper_details(currentpage, file)
    currentpage = get_nextpage(url, currentpage, index)

    return filename


def get_citations_test(soup):

    citations = soup.find_all('div', class_=PROFILE_CARD_CLASSNAME)
    arr = [1]
    label = 'temp'
    # FOR EACH PROFILE CARD...
    for citation in citations:
        # name = citation.find('h3').text
        try:
            cit = citation.find(
                'div', class_=CITATION_CLASSNAME).text.split()[-1]
        # WHEN THE CITATIONS ARE NOT DISPLAYED...
        except IndexError:
            cit = '0'
        try:
            label = citation.find_all('a', class_=LABEL_CLASSNAME)
        except Exception as e:
            print('Unexpected Error!', e.__class__)

        # arr.append(label[0])
        try:
            print(label[0].text)
        except IndexError:
            pass
    return arr


def test_method():
    s = ""
    url = 'https://scholar.google.com/citations?view_op=view_org&hl=en&org=12610868586512439209'
    page1 = get_soup(url)
    """ list_ = page1.find('h2').text.split()
    institution = ' '.join(list_[0:-2]) """
    currentpage = page1
    # index = 10
    arr = get_citations_test(currentpage)
    """ currentpage = get_nextpage(url, currentpage, index)
    index += 10 """
    for x in arr:
        s += str(x)+' '
    return s


if __name__ == "__main__":
    app.run(debug=True)
