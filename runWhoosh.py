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
    # uncomment when submit
    # populate_whoosh(text_dir, whoosh_dir)
    titles = ['(analysis.RegexTokenizer())',
              '(analysis.RegexTokenizer() | analysis.LowercaseFilter())',
              '(analysis.RegexTokenizer() | analysis.LowercaseFilter() | analysis.StopFilter())',
              '(analysis.StemmingAnalyzer())']
              # '(analysis.LowercaseFilter())']
    results = []
    for i in range(4):
        whoosh_dir_current = whoosh_dir + str(i) + '/'
        current_set = print_top_terms(
            whoosh_dir_current, titles[i])
        results.append(current_set)

    results_sets = []
    for i in range(4):
        results_sets.append(set(results[i]))

    intersection = results_sets[0]
    intersection &= results_sets[1]
    intersection &= results_sets[2]
    print_header(
        'Intersecton of RegexTokenizer + LowercaseFilter + StopFilter')
    if intersection:
        print(intersection)

    # 'de' also occurs in stemming
    pipeline_numbers = []
    for i in range(3):
        if 'de' in results_sets[i]:
            print_header("'de' occurs in:" + titles[i])
            pipeline_numbers.append(i)

    for i in pipeline_numbers:
        whoosh_dir_current = whoosh_dir + str(i) + '/'
        query_whoosh(whoosh_dir_current, ["de"], scoring.BM25F())

    queries = ["new york", "empire state building"]
    set_TF_IDF = query_whoosh(whoosh_dir + '3/', queries, scoring.TF_IDF, 20)
    set_TF_Frequency = query_whoosh(whoosh_dir + '3/', queries, scoring.Frequency, 20)
    set_BM25F = query_whoosh(whoosh_dir + '3/', queries, scoring.BM25F, 20)

    for i, q in enumerate(queries):
        intersection=set_TF_IDF[i] & set_BM25F[i] & set_TF_Frequency[i]
        print_header(
            'intersection for '+q)
        if intersection:
            print('\t'+'\n\n\t'.join(intersection)+'\n')  

def populate_whoosh(text_dir, whoosh_dir):
    loaded = 0

    # Create analyzer used for tokenizing and normalizing tokens
    # 000, 001, 010, 011,
    my_analyzers = [
        (analysis.RegexTokenizer()),
        (analysis.RegexTokenizer() | analysis.LowercaseFilter()),
        (analysis.RegexTokenizer() | analysis.LowercaseFilter() | analysis.StopFilter()),
        (analysis.StemmingAnalyzer())
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
    result_set = []
    for term, score in searcher.key_terms(searcher.document_numbers(),
                                          'body', numterms=num_terms):
        print(term, score, sep="\t")
        result_set.append(term)
    return result_set


def query_whoosh(whoosh_dir, queries, weighting=scoring.BM25F(), num_results=50):
    res_sets = []
    # Weighting used for ranking documents
    ix = index.open_dir(whoosh_dir)

    # Examine effect of scoring on queries for key terms (and key terms themselves)

    # Highlight search term in results by making them UPPER CASE
    formatter = UppercaseFormatter()

    # Run queries and print results
    for q in queries:  # "new york", "empire state building", "oculus",
        cur = []
        with ix.searcher(weighting=weighting) as searcher:
            query = QueryParser("body", ix.schema).parse(q)
            results = searcher.search(query, limit=num_results)
            results.formatter = formatter
            print_header(
                    "Query:   {}   returned {} results for {}".format(
                        q, len(results), str(weighting)))
            # if print_results:
            for i, result in enumerate(results):
                cur.append(result['url'].replace('index.txt', ''))
                print_result(i, result)
                print()
        res_sets.append(set(cur))
    return res_sets
    

def print_header(title):
    print("\n\n")
    print("*" * 80)
    print(title)
    print("*" * 80)
    print("\n")


def print_result(i, result, max_length=222):
    print("Url #", i+1, ":", result['url'].replace('index.txt', ''))
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
