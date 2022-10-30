import csv
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
import click
from glob import glob
import os

pj = os.path.join


def load_json(path):
    """
    Load a JSON file
    :param path: Path to the JSON file
    :return: JSON object
    """
    paper = json.load(open(path, 'rb'))
    return paper


def get_authors(json_file):
    """
    Get the names of authors for the paper
    :param json_file: JSON file object
    :return: List of author names in a semicolon (;) delimited string
    """
    author_dict = json_file['metadata']['authors']
    authors = []
    for a in author_dict:
        name = f"{a['first']} {' '.join(a['middle'])} {a['last']}"
        name = " ".join(name.strip().split())
        authors.append(name)
    return "; ".join(authors)


def get_affiliations():
    return


def get_abstract(json_file, pmc):
    """
    Get the abstract of the paper
    :param json_file: JSON file object
    :param pmc: PMC papers have slightly different structure so needs additional processing
    :return: Return the abstarct of the paper, all paragraphs joined together by a line break
    """
    if pmc:
        abstract = []
        body_text = json_file["body_text"]
        for text in body_text:
            if text["section"].lower() == "abstract":
                abstract.append(text["text"])
    else:
        abstract_dict = json_file['abstract']
        abstract = [a['text'] for a in abstract_dict]

    return "\n".join(abstract)


def get_body_text(json_file):
    """
    Get the body text of the paper, if available. Different section headings are ignored for now
    :param json_file: JSON file object
    :return: Return the body text of the paper, all paragraphs joined together by a line break
    """
    body_dict = json_file['body_text']
    body_text = "\n".join([b['text'] for b in body_dict])
    return body_text


def parse_jsons(json_paths, paper_df, ignore_missing_titles, pmc):
    """
    Parse the JSONs and extract relevant data from them
    :param json_paths: A list of file paths
    :param paper_df: A CSV object to write the data to
    :param ignore_missing_titles: Whether to ignore the papers with missing titles
    :param pmc: PMC papers have slightly different structure so needs additional processing
    :return:
    """
    for p in tqdm(json_paths[0:5000]):
        paper = load_json(p)
        paper_id = paper['paper_id']
        title = paper["metadata"]["title"]

        if (not title) and ignore_missing_titles:
            continue

        authors = get_authors(paper)
        abstract = get_abstract(paper, pmc)
        body_text = get_body_text(paper)

        paper_df.writerow([paper_id, title, authors, abstract, body_text])


@click.command()
@click.argument('path', nargs=1, type=click.Path(exists=True))
@click.option('-i', '--ignore-missing-titles', default=True, required=False, type=bool,
              help="Whether to ignore the papers with missing titles")
def main(path, ignore_missing_titles):
    """
    Expected directory structure
    path
      |___ json_schema.txt
      |___ metadata.csv
      |___ document_parses
            |___ pdf_json
            |___ pmc_json

    :param ignore_missing_titles:
    :param path: Path to the folder where the file is unzipped
    :return:
    """
    # Initiliaze a CSV write object. Using pandas dataframe is note a good idea because the dataset size is huge and
    # may not fit in the machine memory
    paper_df = csv.writer(open(path + "parsed_papers.csv", 'w'))
    paper_df.writerow(["paper_id", "title", "authors", "abstract", "body_text"])

    print("Fetching list of file paths")
    pdf_paths = glob(pj(path, "document_parses/pdf_json/*.json"))
    pmc_paths = glob(pj(path, "document_parses/pmc_json/*.json"))

    print("Loading metadata csv file")
    metadata = pd.read_csv("metadata.csv")

    parse_jsons(pdf_paths, paper_df, ignore_missing_titles, pmc=False)
    parse_jsons(pmc_paths, paper_df, ignore_missing_titles, pmc=True)


if __name__ == '__main__':
    main()
