# GOOGLE SCHOLAR CITATIONS AGGREGATOR
# WEB CONSULTATION TEAM - UOP
# PREREQUISITES:    1)Python 3.x   2)INSTALL LIBRARIES requests, lxml AND beautifulsoup4

import sys
import requests
from bs4 import BeautifulSoup

NEXTPAGE_BUTTON_CLASSNAME = 'gs_btnPR gs_in_ib gs_btn_half gs_btn_lsb gs_btn_srt gsc_pgn_pnx'
CITATION_CLASSNAME = 'gs_ai_cby'


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


def get_citations(soup):

    citation_count = 0
    citations = soup.find_all('div', class_=CITATION_CLASSNAME)

    for citation in citations:
        citation_count += int(citation.text.split()[-1])
    return citation_count


def is_lastpage(soup):

    if soup.find('div', class_=CITATION_CLASSNAME).text:
        return False
    else:
        return True


def print_total_citations(url):

    page1 = get_soup(url)
    list_ = page1.find('h2').text.split()
    institution = ' '.join(list_[0:-2])
    print('Institution\t: '+institution)

    # SKIPPING FIRST 20 ENTRIES (FIRST 2 PAGES)
    page2 = get_nextpage(url, page1, 10)
    page3 = get_nextpage(url, page2, 20)

    currentpage = page3
    total_citation_count = 0

    # FROM THE ENTRY 21 TO 210
    for index in range(30, 211, 10):
        if is_lastpage(currentpage):
            break

        # UNCOMMENT THE FOLLOWING LINE TO SEE THE URLS WHICH ARE BEING SCRAPED
        # print(currentpage)

        total_citation_count += get_citations(currentpage)
        currentpage = get_nextpage(url, currentpage, index)
    print("Total citations :", total_citation_count, end='\n\n')


def get_url():

    print('--------------------------------------------------')
    print('Usage: Input -1 to exit and 0 for default output')
    print('URL\t\t:', end=' ')
    url = input()
    return url


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

# MAIN PROGRAM
print('\n\tGoogle Scholar citations aggregator')
url = get_url()

while (True):
    try:
        if (int(url) == -1):
            sys.exit(0)
        elif (int(url) == 0):
            for institution in institutions:
                print_total_citations(institution)
        else:
            print('Wrong Input! Try Again.')
    except ValueError:
        try:
            print_total_citations(url)
        except requests.exceptions.MissingSchema:
            print('URL Not Found! Try Again.')
        except Exception as e:
            print('Unexpected Error!', e.__class__)
            sys.exit(0)
    except requests.exceptions.ConnectionError:
        print('Connection Error! Try Again.')
    except Exception as e:
        print('Unexpected Error!', e.__class__)
        sys.exit(0)
    url = get_url()
