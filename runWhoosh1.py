#!/usr/bin/python3

""" Insert text of html pages into whoosh search engine and query it
"""

import os
import re

from whoosh import analysis, index, scoring, writing
from whoosh.fields import Schema, TEXT, ID
from whoosh.highlight import UppercaseFormatter
from whoosh.qparser import QueryParser

data_dir = "data/"
text_dir = os.path.join(data_dir, "pageText/")
whoosh_dir = os.path.join(data_dir, "whoosh/")
whoosh_dir1 = whoosh_dir+"1/"
whoosh_dir2 = whoosh_dir+"2/"
whoosh_dir3 = whoosh_dir+"3/"


def main():
    populate_whoosh(text_dir, whoosh_dir)
    print_top_terms(whoosh_dir1)
    print_top_terms(whoosh_dir2)
    print_top_terms(whoosh_dir3)
    # query_whoosh(whoosh_dir1)
    # query_whoosh(whoosh_dir2)
    # query_whoosh(whoosh_dir3)


def populate_whoosh(text_dir, whoosh_dir):
    loaded = 0

    # Created 3 analyzers used for tokenizing and normalizing tokens
    my_analyzer1 = (analysis.RegexTokenizer())

    my_analyzer2 = (analysis.RegexTokenizer()
                    | analysis.LowercaseFilter())

    my_analyzer3 = (analysis.StemmingAnalyzer()
                    | analysis.LowercaseFilter()
                    | analysis.StopFilter())

    # Created 3 schemas
    schema1 = Schema(url=ID(stored=True), body=TEXT(
        stored=True, analyzer=my_analyzer1))
    schema2 = Schema(url=ID(stored=True), body=TEXT(
        stored=True, analyzer=my_analyzer2))
    schema3 = Schema(url=ID(stored=True), body=TEXT(
        stored=True, analyzer=my_analyzer3))

    # Setup index
    os.makedirs(whoosh_dir, exist_ok=True)
    ix1 = index.create_in(whoosh_dir1, schema1)
    ix2 = index.create_in(whoosh_dir2, schema2)
    ix3 = index.create_in(whoosh_dir3, schema3)

    # Clear index
    writer1 = ix1.writer()
    writer1.commit(mergetype=writing.CLEAR)
    writer2 = ix2.writer()
    writer2.commit(mergetype=writing.CLEAR)
    writer3 = ix3.writer()
    writer3.commit(mergetype=writing.CLEAR)

    # Index documents
    writer1 = ix1.writer()
    writer2 = ix2.writer()
    writer3 = ix3.writer()
    for root, dirs, files in os.walk(text_dir, topdown=False):
        for name in files:
            text_file = os.path.join(root, name)
            print('.', end='')
            with open(text_file) as tf:
                body = tf.read()
                url = text_file.replace(text_dir, "")
                writer1.add_document(url=url, body=body)
                writer2.add_document(url=url, body=body)
                writer3.add_document(url=url, body=body)
                print("Added", url)
                loaded += 1

    writer1.commit()
    writer2.commit()
    writer3.commit()
    print("\n\nLoaded", loaded, "documents")


def print_top_terms(whoosh_dir, num_terms=20):
    ix = index.open_dir(whoosh_dir)
    searcher = ix.searcher()
    print_header("Top {} terms".format(num_terms))
    for term, score in searcher.key_terms(searcher.document_numbers(),
                                          'body', numterms=num_terms):
        print(term, score, sep="\t")


def query_whoosh(whoosh_dir, num_results=5):
    ix = index.open_dir(whoosh_dir)

    # Examine effect of scoring on queries for key terms (and key terms themselves)

    # Highlight search term in results by making them UPPER CASE
    formatter = UppercaseFormatter()

    # Weighting used for ranking documents
    weighting = scoring.BM25F()

    # Run queries and print results
    for q in ["new york", "empire state building", "oculus"]:
        with ix.searcher(weighting=weighting) as searcher:
            query = QueryParser("body", ix.schema).parse(q)
            results = searcher.search(query, limit=num_results)
            results.formatter = formatter
            print_header(
                "Query:   {}   returned {} results".format(q, len(results)))
            for result in results:
                print_result(result)
                print()


def print_header(title):
    print("\n\n")
    print("*" * 60)
    print(title)
    print("*" * 60)
    print("\n")


def print_result(result, max_length=222):
    print("Url:", result['url'].replace('index.txt', ''))
    print("Highlight:", result.highlights("body"))
    print()


if __name__ == '__main__':
    main()

# # maybe? printing out analysis.RegexTokenizer() based on 20 terms
# tokenizer = RegexTokenizer()
# for token in tokenizer(term):  # term?
#     print(token.text)

# # printing out analysis.StopFilter()
# for token in LowercaseFilter(tokenizer()):
# ... print(token.text)

# # printing out analysis.LowercaseFilter()
# stopper = StopFilter()
# for token in stopper(LowercaseFilter(tokenizer(u"term"))):
#     print(token.text)
