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


def main():
    populate_whoosh(text_dir, whoosh_dir)
    pipelines = ['pipeline 1','pipeline 2','pipeline 3','pipeline 4','pipeline 5','pipeline 6','pipeline 7','pipeline 8']

    for i in range(8):
        whoosh_dir_current = whoosh_dir + str(i) + '/'
        print_top_terms(whoosh_dir_current, pipelines[i])


def populate_whoosh(text_dir, whoosh_dir):
    loaded = 0

    # Create analyzer used for tokenizing and normalizing tokens
    # 000, 001, 010, 011, 
    my_analyzers = [ 
        (analysis.RegexTokenizer()),
        (analysis.RegexTokenizer() | analysis.LowercaseFilter()),
        (analysis.RegexTokenizer() | analysis.StopFilter()),
        (analysis.RegexTokenizer() | analysis.LowercaseFilter() | analysis.StopFilter()),

        (analysis.StemmingAnalyzer() | analysis.StopFilter()),
        (analysis.StemmingAnalyzer()),
        (analysis.StemmingAnalyzer() | analysis.LowercaseFilter()),
        (analysis.StemmingAnalyzer() | analysis.LowercaseFilter() | analysis.StopFilter())
    ]
    # Create schemas
    schemas = []
    for my_analyzer in my_analyzers:
        schema = Schema(url=ID(stored=True), body=TEXT(
            stored=True, analyzer=my_analyzer))
        schemas.append(schema)

    # Setup index
    ixs = []
    for i, my_analyzer in enumerate(my_analyzers):
        whoosh_dir_current = whoosh_dir + str(i) + '/'
        os.makedirs(whoosh_dir_current, exist_ok=True)
        ix = index.create_in(whoosh_dir_current, schemas[i])
        ixs.append(ix)
    

    # Clear index
    writers = []
    for i, my_analyzer in enumerate(my_analyzer):
        writer = ixs[i].writer()
        writer.commit(mergetype=writing.CLEAR)
        writer = ixs[i].writer()
        writers.append(writer)
        

    # Index documents
    for root, dirs, files in os.walk(text_dir, topdown=False):
        for name in files:
            text_file = os.path.join(root, name)
            print('.', end='')
            with open(text_file) as tf:
                body = tf.read()
                url = text_file.replace(text_dir, "")
                for writer in writers:
                    writer.add_document(url=url, body=body)
                # print("Added", url)
                loaded += 1
      
    for writer in writers:
        writer.commit()
    
    print("\n\nLoaded", loaded, "documents")


def print_top_terms(whoosh_dir, pipeline, num_terms=20):
    ix = index.open_dir(whoosh_dir)
    searcher = ix.searcher()
    print_header("Top {} terms for {}".format(num_terms, pipeline))
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
