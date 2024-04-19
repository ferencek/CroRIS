import requests
import json
import bibtexparser
import xmltodict
import copy
import locale
from argparse import ArgumentParser

import configuration as cfg

# For correct author name sorting
locale.setlocale(locale.LC_COLLATE, "hr_HR.UTF-8")

# --------------------------------------------------
# Known journals
journals = cfg.journals
issn     = cfg.issn
# --------------------------------------------------


def get_list_of_papers(list_of_papers):
    with open(list_of_papers) as f:
        temp = f.read()

    return bibtexparser.loads(temp)


def get_exclusion_list(list_of_DOIs):
    exclusion_list = []

    with open(list_of_DOIs) as f:
        lines = f.read().splitlines()
        for line in lines:
            # Skip comment lines
            stripped_line = line.strip()
            if stripped_line.startswith('#'):
                continue
            exclusion_list.append(stripped_line.lower())

    return exclusion_list


def get_title_and_abstract(eprint):
    # Fetch paper data from arXiv in XML format locally converted to a Python dictionary
    # More info at: https://info.arxiv.org/help/api/basics.html
    #               https://info.arxiv.org/help/api/user-manual.html
    url = 'http://export.arxiv.org/api/query?id_list={}'.format(eprint)
    paper_data = xmltodict.parse(requests.get(url).content)

    title = paper_data['feed']['entry']['title'].strip().replace('\n ', '')
    abstract = paper_data['feed']['entry']['summary'].strip().replace('\n', ' ')

    return [title, abstract]


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


def prepare_input(list_of_papers, output_file, configuration, exclusion_list):
    # --------------------------------------------------
    # Configuration
    collaboration = cfg.cfg_sets[configuration]['collaboration']
    keywords      = cfg.cfg_sets[configuration]['keywords']
    authors       = cfg.authors
    pub_common    = cfg.pub_common
    inst_dict     = cfg.inst_dict
    proj_dict     = cfg.proj_dict
    # --------------------------------------------------

    dois  = []
    data  = []
    error = []

    counter = 0
    counter_skip = 0
    counter_error = 0

    # Loop over all papers which are stored in bib
    for n, p in enumerate(list_of_papers.entries, 1):

        print('------------------------------------------------')
        print('Paper:', n)

        # DOI
        doi = p['doi']
        doi_lower = doi.lower()
        # Skip excluded DOIs
        if doi_lower in exclusion_list:
            counter_skip += 1
            print('\nINFO: This paper with DOI:{} is excluded and will be skipped.'.format(doi))
            continue
        # Skip any duplicates
        if doi_lower in dois:
            counter_skip += 1
            print('\nWARNING: This paper with DOI:{} is a duplicate and will be skipped.'.format(doi))
            continue
        else:
            dois.append(doi_lower)

        # Get the arXiv paper id (if defined)
        eprint = (p['eprint'] if 'eprint' in p else '')
    
        # Fetch paper data from Inspire HEP in JSON format
        # More info at: https://github.com/inspirehep/rest-api-doc
        url = 'https://inspirehep.net/api/doi/{}'.format(doi)
        paper_data = requests.get(url).json()

        # Get title and abstract from the first available source but give priority to arXiv
        title    = ''
        for t in paper_data['metadata']['titles']:
            source = (t['source'].strip().lower() if 'source' in t else '')
            if title == '' or source == 'arxiv':
                title = t['title'].strip()
        arXiv_found = False
        abstract = ''
        for a in paper_data['metadata']['abstracts']:
            source = (a['source'].strip().lower() if 'source' in a else '')
            if abstract == '' or source == 'arxiv':
                abstract = a['value'].strip()
                if source == 'arxiv':
                    arXiv_found = True

        # If arXiv source is not found on Inspire HEP but e-Print exists, fetch title
        # and abstract directly from arXiv
        if eprint and not arXiv_found:
            title, abstract = get_title_and_abstract(eprint)

        # Authors
        all_authors = paper_data['metadata']['authors']
        all_author_names = []

        # Switch for storing the full author list
        fullAuthorList = False
        # Check if the switch is defined in the used configuration set
        if 'fullAuthorList' in cfg.cfg_sets[configuration].keys():
            fullAuthorList = cfg.cfg_sets[configuration]['fullAuthorList']

        # List that contains CroRIS IDs for found authors from Croatian institutions
        autori = []
        author_dict = {
            "croris_id": None,
            "oib": None,
            "mbz": None
        }

        # Set that contains author institutions' CroRIS IDs
        inst_ids = set()

        # List that contains full names for found authors from Croatian institutions
        authors_pretty = []
        # List that contains indices in the list of all authors for found authors from Croatian institutions
        authors_idx = []

        # All authors
        for idx, author in enumerate(all_authors):
            author_name = author['full_name']
            if fullAuthorList:
                all_author_names.append(author_name)
            # Authors from Croatian institutions
            for a in authors:
                a_pretty = authors[a][0]

                if a in author_name:
                    authors_pretty.append(a_pretty)
                    authors_idx.append(idx)
                    if authors[a][1] is not None:
                        a_dict = copy.deepcopy(author_dict)
                        a_dict['croris_id'] = authors[a][1]
                        autori.append(a_dict)
                    if authors[a][2] is not None:
                        inst_ids.add(authors[a][2])
                    break

        # Check if any authors are found
        if len(authors_pretty)==0:
            counter_skip += 1
            print('\nWARNING: No authors found for this paper with DOI:{}. Skipping.'.format(doi))
            continue

        # Any authors at the start (first two places) or at the end (last two places) of the full author list?
        authorsAtStartOrEnd = (authors_idx[0]<2 or authors_idx[-1]>(len(all_authors)-3))

        # Switch for sorting authors from Croatian institutions
        sortAuthors = False
        # Check if the switch is defined in the used configuration set
        if 'sortAuthors' in cfg.cfg_sets[configuration].keys():
            # Allow sorting only if there are no authors at the start or at the end of the full author list
            if not authorsAtStartOrEnd:
                sortAuthors = cfg.cfg_sets[configuration]['sortAuthors']
            else:
                print('\nWARNING: Some authors appear at the start or at the end of the full author list. Sorting will be disabled.')

        # Now build the authors string
        # Full author list
        if fullAuthorList:
            authors_string = ' ; '.join(all_author_names)
        # Pruned author list
        else:
            # Authors not at the start or at the end of the full author list
            if not authorsAtStartOrEnd:
                # First author
                author_names = [all_authors[0]['full_name']]
                # Ellipsis
                author_names += ['...']
                # Authors from Croatian institutions
                author_names += (sorted(authors_pretty, key=locale.strxfrm) if sortAuthors else authors_pretty)
                # Ellipsis
                author_names += ['...']
                # Last author
                author_names += [all_authors[-1]['full_name']]
            # More complicated case when authors appear at the start or at the end of the full author list
            else:
                author_names = []
                insertedEllipsis = False
                # Loop over author indices and check various possibilities
                for i, a_idx in enumerate(authors_idx):
                    # First found author
                    if i==0:
                        # If also first in the full author list
                        if a_idx==0:
                            # Author
                            author_names += [authors_pretty[i]]
                        else:
                            # First author
                            author_names += [all_authors[0]['full_name']]
                            # If second in the full author list
                            if a_idx==1:
                                # Author
                                author_names += [authors_pretty[i]]
                            else:
                                # Ellipsis
                                author_names += ['...']
                                insertedEllipsis = True
                                # Author
                                author_names += [authors_pretty[i]]
                    else:
                        idx_diff = (a_idx - authors_idx[i-1])
                        # Consecutive found authors not consecutive in the full author list
                        if idx_diff>1 and not insertedEllipsis:
                            # Ellipsis
                            author_names += ['...']
                            insertedEllipsis = True
                            # Author
                            author_names += [authors_pretty[i]]
                        else:
                            # Author
                            author_names += [authors_pretty[i]]
                # Finally, deal with the end of the author list
                # Last found author not at the end of the full author list
                if not (authors_idx[-1]>(len(all_authors)-3)):
                    # Ellipsis
                    author_names += ['...']
                    # Last author
                    author_names += [all_authors[-1]['full_name']]
                else:
                    # Check if additional ellipsis needs to be inserted
                    # Reversed list of author indices
                    authors_idx_r = authors_idx[::-1]
                    for i, a_idx in enumerate(authors_idx_r):
                        # Break the loop once the last element is reached
                        if i==(len(authors_idx)-1):
                            break
                        idx_diff = (a_idx - authors_idx_r[i+1])
                        n_idx = (len(author_names)-2-i)
                        # Consecutive found authors not consecutive in the full author list
                        if idx_diff>1 and author_names[n_idx] != '...':
                            # Ellipsis
                            author_names.insert(n_idx+1, '...')
                            break
                    # Last found author second to last in the full author list
                    if authors_idx[-1]==(len(all_authors)-2):
                        # Last author
                        author_names += [all_authors[-1]['full_name']]

            authors_string = ' ; '.join(author_names)

        # Collaboration
        if collaboration != 'off':
            if collaboration == 'auto':
                _collaboration = ((p['collaboration'] + ' Collaboration')  if 'collaboration' in p else '')
            else:
                _collaboration = collaboration + ' Collaboration'
        else:
            _collaboration = ''

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
        _keywords = copy.deepcopy(keywords)
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
                    _keywords.append(k_text)
                else:
                    break

        # Page info validity counter
        # Need to make sure that either the article number and the total number of pages
        # or the first and the last page of the article are specified
        validity_counter = [0, 0]

        # Save output
        _temp = {}
        _temp.update(copy.deepcopy(pub_common))
        if 'ppg' in cfg.cfg_sets[configuration].keys():
            _temp['ppg'] = cfg.cfg_sets[configuration]['ppg']
        _temp['doi']             = doi
        #_temp['poveznice'][0]['url'] += doi # commented out to avoid duplicate links since CroRIS automatically adds DOI links
        _temp['autor_string']    = authors_string
        _temp['autori']    = autori
        if _collaboration:
            _temp['kolaboracija'] = _collaboration
        _temp['godina']          = year
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

        ml = [
            {
                "jezik": "en",
                "trans": "o",
                "naslov": title,
                "sazetak": abstract,
                "kljucne_rijeci": ' ; '.join(_keywords)
            }
        ]
        _temp['ml'] = ml

        ustanove = []
        for i_id in inst_ids:
            i_dict = copy.deepcopy(inst_dict)
            i_dict['croris_id'] = i_id
            ustanove.append(i_dict)
        _temp['ustanove'] = ustanove

        projekti = []
        if 'projects' in p:
            for proj in p['projects'].split(','):
                p_dict = copy.deepcopy(proj_dict)
                p_dict['croris_id'] = int(proj.strip())
                projekti.append(p_dict)
            _temp['projekti'] = projekti

        # Catch articles with unknown journal or invalid page info status
        if 'Unknown journal' in journal or (validity_counter[0] < 2 and validity_counter[1] < 2):
          error.append(_temp)
          counter_error += 1
        else:
          data.append(_temp)
          counter += 1

        print('\nDOI:', doi)
        print('arXiv:', (eprint if eprint != '' else 'N/A'))
        print('Title:', title)
        print('Authors:', authors_string)
        print('Collaboration:', (_collaboration if _collaboration else 'N/A'))
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
        print('\nKeywords:', ' ; '.join(_keywords))

    print('------------------------------------------------')

    print('\n%i paper(s) prepared for upload\n' % counter)
    if counter_skip > 0:
        print('%i paper(s) skipped\n' % counter_skip)
    if counter_error > 0:
        print('%i paper(s) with unknown journal(s)\n' % counter_error)

    # Output file, i.e. input for CroRIS
    if counter > 0:
        with open(output_file, 'w', encoding='utf8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)

    # Output file for papers with unknown journals
    if counter_error > 0:
        with open(output_file.rstrip('.json')+'_error.json', 'w', encoding='utf8') as outfile:
            json.dump(error, outfile, ensure_ascii=False, indent=2)

# --------------------------------------------------

if __name__ == '__main__':
    # Usage example
    Description = "Example: %(prog)s -c cms -i list_of_papers.bib -o CroRIS_input.json"
    
    # Input arguments
    parser = ArgumentParser(description=Description)

    parser.add_argument("-c", "--configuration", dest="configuration",
                      help="Configuration set to use (case-insensitive). Options: {}".format(', '.join(cfg.cfg_sets.keys())),
                      metavar="CONFIGURATION",
                      required=True)

    parser.add_argument("-i", "--input", dest="input",
                      help="Input BibTeX file",
                      metavar="INPUT",
                      required=True)
    
    parser.add_argument("-o", "--output", dest="output",
                      help="Output JSON file",
                      metavar="OUTPUT",
                      required=True)

    parser.add_argument("-e", "--exclude", dest="exclude",
                      help="List of DOIs to exclude",
                      metavar="EXCLUDE")

    (options, args) = parser.parse_known_args()

    # Load list of papers from a BibTeX file
    list_of_papers = get_list_of_papers(options.input)

    # Optional exclusion list
    exclusion_list = []
    if options.exclude:
        exclusion_list = get_exclusion_list(options.exclude)

    # Create input for CroRIS
    prepare_input(list_of_papers, options.output, options.configuration.lower(), exclusion_list)
