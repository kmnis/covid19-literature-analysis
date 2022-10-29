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


def get_abstract(json_file):
    """
    Get the abstract of the paper
    :param json_file: JSON file object
    :return: Return the abstarct of the paper, all paragraphs joined together by a line break
    """
    abstract_dict = json_file['abstract']
    abstract = "\n".join([a['text'] for a in abstract_dict])
    return abstract


def get_body_text(json_file):
    """
    Get the body text of the paper, if available. Different section headings are ignored for now
    :param json_file: JSON file object
    :return: Return the body text of the paper, all paragraphs joined together by a line break
    """
    body_dict = json_file['body_text']
    body_text = "\n".join([b['text'] for b in body_dict])
    return body_text


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
    json_paths = glob(pj(path, "document_parses/**/*.json"))

    df_data = []
    for p in tqdm(json_paths):
        paper = load_json(p)
        paper_id = paper['paper_id']
        title = paper["metadata"]["title"]

        if (not title) and ignore_missing_titles:
            continue

        authors = get_authors(paper)
        abstract = get_abstract(paper)
        body_text = get_body_text(paper)
        df_data.append([paper_id, title, authors, abstract, body_text])

    paper_df = pd.DataFrame(data=df_data, columns=["paper_id", "title", "authors", "abstract", "body_text"])
    paper_df.to_csv(path + "parsed_data.csv", index=False)
    print(paper_df.shape, paper_df.paper_id.unique().shape)


if __name__ == '__main__':
    main()
