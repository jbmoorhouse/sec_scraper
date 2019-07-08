import re
from w3lib.html import remove_tags
from bs4 import BeautifulSoup

from scrapy.loader.processors import Compose, MapCompose
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.datatypes import MergeDict
from scrapy.loader.common import wrap_loader_context

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize

import unicodedata


class MapComposeGen(MapCompose):

    def __call__(self, value, loader_context=None):

        values = arg_to_iter(value)

        if loader_context:
            context = MergeDict(loader_context, self.default_loader_context)
        else:
            context = self.default_loader_context

        wrapped_funcs = [wrap_loader_context(f, context) for f in self.functions]

        for func in wrapped_funcs:
            for v in values:
                try:
                    next_values = func(v)
                except Exception as e:
                    raise ValueError("Error in MapCompose with "
                                     "{} value={} error='{}: {}'".format(
                        (str(func), value, type(e).__name__, str(e))))

            values = next_values

        return list(values)


def _get_documents(document_txt):
    """
    Extract the <document> html tags from the text

    Parameters
    ----------
    text : str
        Raw 10-k scraped .txt file

    Returns
    -------
    documents : list of str
        The document strings found in `text`
    """

    return re.findall(r'<document>(.*?)</document>', document, re.DOTALL)

def _get_document_type(document_tag):

    """
    Return the document type lowercased

    Parameters
    ----------
    tag_document : str
        The document string

    Returns
    -------
    document_type : str
        The document type lowercased
    """

    tag = "<type>"
    pattern = re.compile(r'{}[^\n]+'.format(tag))
    m = pattern.search(tag_document))

    try:
        document_type = m.group()
    except AttributeError as e:
        print(e, "Invalid tag")

    return remove_tags(document_type)


def _lemmatize_words(document):
    """
    Lemmatize words

    Parameters
    ----------
    words : str

    Returns
    -------
    lemmatized_words : list of str
        List of lemmatized words
    """

    nltk.download('wordnet')
    wnl = WordNetLemmatizer()

    tokens = word_tokenize(document)

    return [wnl.lemmatize(t, pos='v') for t in tokens]


def get_ten_k(document_txt):
    """
    Yield all documents with type tag <type>10-k from the raw 10-k document. Function is
    to be used with MapComposeGen(). Function to be wrapped in MapComposeGen

    Parameters
    ----------
    document : str

    """

    documents = _get_documents(document_txt)

    for doc in documents:
        document_type = _get_document_type(doc)

        if document_type.strip().lower() == "10-k":
            soup = BeautifulSoup(doc, "html.parser").get_text()
            text = unicodedata.normalize('NFKD', soup)

            yield text.lower()





