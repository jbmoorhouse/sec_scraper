import re
from w3lib.html import remove_tags
from bs4 import BeautifulSoup

from scrapy.loader.processors import Compose, MapCompose

from unidecode import unidecode


def _get_documents(complete_submission_file):
    """
    An SEC complete submission text file (e.g.
    https://www.sec.gov/Archives/edgar/data/1090872/000089161802000185/0000891618-02-000185-index.htm) contains all
    form types (FORM 10-K, EXHIBIT 10.7, EXHIBIT 10.13 etc.). _get_documents extracts all <document> tags from the
    complete submission, returning a list of all submissions

    Parameters
    ----------
    complete_submission_file : str
        complete submission response .txt file (e.g.
        https://www.sec.gov/Archives/edgar/data/1090872/ 000089161802000185/0000891618-02-000185.txt)


    Returns
    -------
    documents : list of str
        list of all <document> content found in document_txt


    Examples
    --------
    >>> documents = ["<DOCUMENT><TYPE>10-K ... </BODY></HTML></TEXT></DOCUMENT>",
                     "<DOCUMENT><TYPE>EX-10.7 ... </TEXT></DOCUMENT>"]
    """

    complete_submission_file = complete_submission_file.lower()
    documents =  re.findall(r'<document>(.*?)</document>', complete_submission_file, re.DOTALL)

    return documents

def _get_document_type(document):
    """
    complete_submission_file contains one or more submission document. Each document includes a type tag to denote
    the submission type (e.g. <TYPE>10-K , <TYPE>EX-10.7). _get_document_type return the document type as a string.
    lowercased

    Parameters
    ----------
    document : str
        The document string

    Returns
    -------
    document_type : str
        The document type lowercased

    Examples
    --------

    >>> document_type = _get_document_type("<DOCUMENT><TYPE>10-K ... </BODY></HTML></TEXT></DOCUMENT>")
    >>> document_type

    "10-k"

    >>> document_type = _get_document_type(""<DOCUMENT><TYPE>EX-10.7 ... </TEXT></DOCUMENT>")
    >>> document_type

    "ex-10.7"
    """

    tag = "<type>"
    pattern = re.compile(r'{}[^\n]+'.format(tag))
    m = pattern.search(document_tag)

    try:
        document_type = m.group()
    except AttributeError as e:
        print(e, "Invalid tag")

    return remove_tags(document_type)


def get_ten_k(complete_submission_file):
    """
    complete_submission_file contains a single document of interest (10-K and all other forms of 10-K). get_ten_k must
    account for all types of 10-K document, such as late submissions (10-k405) and submission amendments (10-k/a).

    Parameters
    ----------
    complete_submission_file : str
        complete submission response .txt file (e.g.
        https://www.sec.gov/Archives/edgar/data/1090872/ 000089161802000185/0000891618-02-000185.txt)

    Returns
    -------
    text : str
        text contains all relevant content from complete_submission_file for storage and/or natural langauge processing.
    """

    documents = _get_documents(complete_submission_file)

    for doc in documents:
        document_type = _get_document_type(doc)

        if "10-k" in document_type.strip():
            soup = BeautifulSoup(doc, "html.parser")
            text = unidecode(soup.get_text())

            return text