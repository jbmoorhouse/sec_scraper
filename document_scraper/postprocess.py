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
                next_values = func(v)
            values = next_values

        return list(values)


def _get_documents(document):
    """
    Extract the <document> html tags from the text

    Parameters
    ----------
    text : str
        Raw 10-k scraped .txt file

    Returns
    -------
    extracted_docs : list of str
        The document strings found in `text`
    """

    return re.findall(r'<document>(.*?)</document>', document, re.DOTALL)

def _get_document_type(tag_document):

    """
    Return the document type lowercased

    Parameters
    ----------
    tag_document : str
        The document string

    Returns
    -------
    doc_type : str
        The document type lowercased
    """

    tag = "<type>"
    type_pattern = re.compile(r'{}[^\n]+'.format(tag))
    doc_type = "".join(type_pattern.findall(tag_document))[len(tag):]

    return doc_type.lower()


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


def get_ten_k(document):
    """
    Yield all documents with type tag <type>10-k from the raw 10-k document. Function is
    to be used with MapComposeGen().

    Parameters
    ----------
    document : str

    """

    documents = _get_documents(document)

    for doc in documents:
        doc_type = _get_document_type(doc)

        if doc_type == "10-k":
            doc = BeautifulSoup(doc, "html.parser").get_text()
            yield doc.lower()





