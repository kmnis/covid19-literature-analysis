import csv
import json
import os

import click
import pandas as pd
from tqdm import tqdm

pj = os.path.join


def load_json(path: str):
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
    """
    TODO: Implement later if needed
    :return:
    """
    pass


def get_abstract(json_file, pmc: bool):
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


def parse_json(json_path: str, pmc: bool):
    """
    Parse the JSONs and extract relevant data from them
    :param json_path: File path to the JSON file
    :param pmc: PMC papers have slightly different structure so needs additional processing
    :return: A list with fetched data
    """
    paper = load_json(json_path)
    paper_id = paper['paper_id']
    title = paper["metadata"]["title"]
    authors = get_authors(paper)
    abstract = get_abstract(paper, pmc)
    body_text = get_body_text(paper)

    return [paper_id, title, authors, abstract, body_text]


def handle_pmc_json(metadata: pd.DataFrame, index: int, pmc_path: str, path: str):
    """
    If PMC json is available, parse it and try to get as many details as possible
    :param metadata: The metadata CSV file
    :param index: Index of the row to process
    :param pmc_path: Path to the PMC json file
    :param path: Top level data directory
    :return: A list of features extracted from the JSONs
    """
    pmc_data = parse_json(pmc_path, pmc=True)
    if len(pmc_data) > 0:

        # Handle the missing title cases
        if not pmc_data[1]:
            if not pd.isna(metadata.title[index]):
                pmc_data[1] = metadata.title[index]

        # Handle the missing abstract cases
        if not pmc_data[3] and not pd.isna(metadata.abstract[index]):
            pmc_data[3] = metadata.abstract[index]
        else:
            pdf_paths = metadata.pdf_json_files[index]
            if not pd.isna(pdf_paths):
                pdf_paths = [x.strip() for x in pdf_paths.split(";")]
                for p in pdf_paths:
                    p = pj(path, p)
                    pdf_data = parse_json(p, pmc=False)
                    if pdf_data[3]:
                        pmc_data[3] = pdf_data[3]
                        break

    return pmc_data


def handle_pdf_json(metadata: pd.DataFrame, index: int, pdf_path: str):
    """
    If pdf json is available, parse it and try to get as many details as possible
    :param metadata: The metadata CSV file
    :param index: Index of the row to process
    :param pdf_path: Path to the pdf json file
    :return: A list of features extracted from the JSONs
    """
    pdf_data = parse_json(pdf_path, pmc=False)
    if len(pdf_data) > 0:

        # Handle the missing title cases
        if not pdf_data[1]:
            if not pd.isna(metadata.title[index]):
                pdf_data[1] = metadata.title[index]

        # Handle the missing abstract cases
        if not pdf_data[3] and not pd.isna(metadata.abstract[index]):
            pdf_data[3] = metadata.abstract[index]

    return pdf_data


@click.command()
@click.argument('path', nargs=1, type=click.Path(exists=True))
# @click.option('-i', '--ignore-missing-titles', default=True, required=False, type=bool,
#               help="Whether to ignore the papers with missing titles")
def main(path):
    """
    Expected directory structure
    path
      |___ json_schema.txt
      |___ metadata.csv
      |___ document_parses
            |___ pdf_json
            |___ pmc_json

    :param path: Path to the folder where the file is unzipped
    :return:
    """

    # Initiliaze a CSV write object. Using pandas dataframe is note a good idea because the dataset size is huge and
    # may not fit in the machine memory
    paper_df = csv.writer(open(path + "parsed_papers.csv", 'w'))
    paper_df.writerow(["paper_id", "title", "authors", "abstract", "body_text", "publish_time", "journal"])

    print("Loading metadata csv file")
    metadata = pd.read_csv(pj(path, "metadata.csv"))

    paper_count = 0
    for index in tqdm(range(len(metadata))):
        pmc_path = metadata.pmc_json_files[index]
        pdf_path = metadata.pdf_json_files[index]
        if not pd.isna(pmc_path):
            pmc_path = pj(path, pmc_path)
            data = handle_pmc_json(metadata, index, pmc_path, path)
        elif not pd.isna(pdf_path):
            pdf_paths = [x.strip() for x in pdf_path.split(";")]
            pdf_path = pj(path, pdf_paths[0])
            data = handle_pdf_json(metadata, index, pdf_path)
        else:
            data = []

        if len(data) and data[1]:
            publish_time = metadata.publish_time[index]
            journal = metadata.journal[index]

            if pd.isna(publish_time):
                publish_time = ""

            if pd.isna(journal):
                journal = ""

            data.append(publish_time)
            data.append(journal)
            paper_df.writerow(data)

            paper_count += 1

    print("Total papers fetched:", paper_count)


if __name__ == '__main__':
    main()
