import requests
import json
import bibtexparser
from argparse import ArgumentParser

import configuration as cfg

# --------------------------------------------------
# Configuration

authors          = cfg.authors
journals         = cfg.journals
issn             = cfg.issn
keywords         = cfg.keywords

# --------------------------------------------------


def get_list_of_papers(list_of_papers):
    with open(list_of_papers) as f:
      temp = f.read()

    return bibtexparser.loads(temp)


# In the past the Inspire HEP database used to include the journal series letter
# in the volume number instead of keeping it in the journal name. Below is a list
# affected journals and the journal_name(...) function that addresses this. In the
# meantime this seems to have been fixed but keeping the function for backward
# compatibility
incomplete_journal_names = ['Eur. Phys. J.', 'Phys. Lett.', 'Phys. Rev.']

def get_name(name, volume):
    if name in incomplete_journal_names:
        name = name + ' ' + volume[0]

    return name


def get_volume(name, volume):
    if name in incomplete_journal_names:
      return volume[1:]
    else:
      return volume


def get_journal(name):
    if name not in journals.keys():
        return "*** Unknown journal '" + name + "' encountered! Please put it in the list of known journals or remove this article from the input list. ***"

    return journals[name]


def get_issn(name):
    if name not in issn.keys():
        return ['', '']

    return issn[name]


def prepare_input(list_of_papers, output_file):
    data  = []
    error = []

    counter = 0
    counter_skip = 0

    # Loop over all papers which are stored in bib
    for n, p in enumerate(list_of_papers.entries, 1):

        print('------------------------------------------------')
        print('Paper:', n)

        # DOI
        doi = p['doi']

        # Get the arXiv paper id (if defined)
        eprint = (p['eprint'] if 'eprint' in p else '')
    
        # Fetch paper data from INSPIRE in JSON format
        # More info at: https://github.com/inspirehep/rest-api-doc
        url = 'https://inspirehep.net/api/doi/{}'.format(doi)
        paper_data = requests.get(url).json()

        # Get title and abstract from the first available source but give priority to arXiv
        title    = ''
        for t in paper_data['metadata']['titles']:
            source = (t['source'].strip().lower() if 'source' in t else '')
            if title == '' or source == 'arxiv':
                title = t['title'].strip()
        abstract = ''
        for a in paper_data['metadata']['abstracts']:
            source = (a['source'].strip().lower() if 'source' in a else '')
            if abstract == '' or source == 'arxiv':
                abstract = a['value'].strip()

        # Authors
        all_authors = paper_data['metadata']['authors']

        authors_pretty = []

        # All authors
        for author in all_authors:
            # Cro authors
            for a, a_pretty in authors.items():

                author_text = author['full_name']
                if a in author_text:
                    authors_pretty.append(a_pretty)
                    break

        # First author
        authors_string = all_authors[0]['full_name'] + '; ...'

        # Sorted authors from Croatian institutions
        authors_pretty.sort()
        for a_pretty in authors_pretty:
            authors_string += ' ; ' + a_pretty

        # Last author
        authors_string += ' ; ... ; ' + all_authors[len(all_authors)-1]['full_name']

        # Collaboration
        collaboration = ((p['collaboration'] + ' Collaboration')  if 'collaboration' in p else '')

        # Year
        year = p['year']

        # Get fixed journal name (see more detailed description above)
        journal_name = get_name(p['journal'], p['volume'])

        # Volume
        volume = get_volume(p['journal'], p['volume'])

        # Journal (according to CroRIS nomenclature)
        journal = get_journal(journal_name)

        # ISSN
        issn = get_issn(journal_name)

        # Number
        number = (p['number'] if 'number' in p else '')

        # Pages
        page_first = ''
        page_last = ''
        page_tot = ''
        pages = p['pages']

        # Article number
        article_no = ''

        # Quite often the pages field corresponds to the article number (DOI string often ends with it as well), not a page numbers range
        # If we have a page numbers range
        if '-' in pages:
            pages = pages.split('-')
            page_first = pages[0]
            page_last = pages[-1] # this works even if the page range uses double hyphen '--'
        else:
            article_no = pages
            page_tot = str(paper_data['metadata']['number_of_pages'])

        # Keywords
        # CROSBI had a limit of 500 characters on the maximum length of the keyword string
        # Here imposing the limit with some safety margin
        keywords_length = 0
        keywords_lower = []
        for k in keywords:
            if (keywords_length + len(k) + 2) < 480:
                keywords_length += (len(k) + 2)
                keywords_lower.append(k.strip().lower())
            else:
                break

        for k in paper_data['metadata']['keywords']:
            k_text = k['value'].strip()
            if not k_text.lower() in keywords_lower:
                if (keywords_length + len(k_text) + 2) < 480:
                    keywords_length += (len(k_text) + 2)
                    keywords.append(k_text)
                else:
                    break

        # Page info validity counter
        # Need to make sure that either the article number and the total number of pages
        # or the first and the last page of the article are specified
        validity_counter = [0, 0]

        # Save output
        _temp = {}
        _temp['doi']             = doi
        _temp['autor_string']    = authors_string
        _temp['naslov']          = title
        if collaboration:
            _temp['kolaboracija']    = collaboration
        _temp['godina']          = year
        _temp['casopis']         = journal
        _temp['issn']            = issn[0]
        _temp['e-issn']          = issn[1]
        _temp['volumen']         = volume
        if number:
            _temp['svescic']         = number
        if page_first:
            _temp['stranica_prva']   = page_first
            validity_counter[0] += 1
        if page_last:
            _temp['stranica_zadnja'] = page_last
            validity_counter[0] += 1
        if article_no:
            _temp['broj_rada']       = article_no
            validity_counter[1] += 1
        if page_tot:
            _temp['ukupno_stranica'] = page_tot
            validity_counter[1] += 1
        _temp['sazetak']         = abstract
        _temp['kljucne_rijeci']  = '; '.join(keywords)

        # Catch articles with unknown journal or invalid page info status
        if 'Unknown journal' in journal or (validity_counter[0] < 2 and validity_counter[1] < 2):
          error.append(_temp)
          counter_skip += 1
        else:
          data.append(_temp)
          counter += 1

        print('\nDOI:', doi)
        print('arXiv:', (eprint if eprint != '' else 'N/A'))
        print('Title:', title)
        print('Authors:', authors_string)
        print('Collaboration:', (collaboration if collaboration != '' else 'N/A'))
        print('Year:', year)
        print('Journal:', journal)
        print('ISSN:', issn[0])
        print('e-ISSN:', issn[1])
        print('Volume:', volume)
        print('Number:', (number if number != '' else 'N/A'))
        print('First page:', (page_first if page_first != '' else 'N/A'))
        print('Last page:', (page_last if page_last != '' else 'N/A'))
        print('Article number:', (article_no if article_no != '' else 'N/A'))
        print('Total pages:', (page_tot if page_tot != '' else 'N/A'))
        print('\nAbstract:', abstract)
        print('\nKeywords:', keywords)

    print('------------------------------------------------')

    print('\n%i papers prepared for upload\n' % counter)
    if counter_skip > 0:
        print('%i papers skipped\n' % counter_skip)

    # Output file, i.e. input for CroRIS
    with open(output_file, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)

    if len(error) > 0:
        with open(output_file.rstrip('.json')+'_error.json', 'w', encoding='utf8') as outfile:
            json.dump(error, outfile, ensure_ascii=False, indent=2)

# --------------------------------------------------

if __name__ == '__main__':
    # Usage example
    Description = "Example: %(prog)s -i list_of_papers.bib -o CroRIS_input.json"
    
    # Input arguments
    parser = ArgumentParser(description=Description)

    parser.add_argument("-i", "--input", dest="input",
                      help="Input BibTeX file",
                      metavar="INPUT",
                      required=True)
    
    parser.add_argument("-o", "--output", dest="output",
                      help="Output JSON file",
                      metavar="OUTPUT",
                      required=True)

    (options, args) = parser.parse_known_args()


    # Load list of papers from a BibTeX file
    list_of_papers = get_list_of_papers(options.input)

    # Create input for CroRIS
    prepare_input(list_of_papers, options.output)
