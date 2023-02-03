# COVID-19 Literature Analysis using Machine Learning and Deep Learning

## Description
The coronavirus pandemic caused enormous health, economic, environmental, and social challenges to the entire human population. The entire research community worked tirelessly for a vaccine but could we help speeding up these efforts even more?

In response to the COVID-19 pandemic, the White House and a coalition of leading research groups prepared a COVID-19 Open Research Dataset (CORD-19). It is a resource of over 1 million scholarly articles, including over 400,000 with full text, about COVID-19, SARS-CoV-2, and related coronaviruses. This freely available dataset was provided to the global research community to apply recent advances in natural language processing and other AI techniques to generate new insights in support of the ongoing fight against this infectious disease.

This project aims to help researchers navigate this fast-growing body of coronavirus literature to efficiently find relevant and up-to-date information. This is done by using various topic modeling algorithms to cluster similar papers together. We leverage Hadoop for data storage management and PySpark for building ML and DL pipelines.

## Dataset
Dataset consists of JSON and CSV files. Each paper is saved in a nested JSON file while some additional metadata is available in a CSV file. A detailed description is available [here](https://www.kaggle.com/datasets/allen-institute-for-ai/CORD-19-research-challenge). Below image summarizes the data preprocessing pipeline.

![Data Preprocessing](https://user-images.githubusercontent.com/20987291/216574085-e5849b84-7cb3-4c17-8513-9b4350f45d85.png)

## Methodology

![Methodology](https://user-images.githubusercontent.com/20987291/216576252-e610853d-8b0c-4652-9ce8-114b065e0bd8.png)

## Graph Database
- Graph databases provide a way to generate and visualize relationships between entities
- Both Pyspark GraphFrame and neo4j can achieve graph-based data storage. We explored both the tools
- Each author, paper, and journal acts as a node
- All nodes are connected as per relationships – “has_published” or “has_paper”
- Data was prepared using python to make it ready to import to neo4j
- Docker was used to install the neo4j (neo4j version 5.2.0)
- Bash script (start_neo4j.sh) starts the docker container, neo4j server and imports the data

![sample-graph](https://user-images.githubusercontent.com/20987291/216580912-fe993dec-c20d-4c3e-b401-ac8d314967ca.png)

![graph](https://user-images.githubusercontent.com/20987291/216578879-aa094287-ddc6-48d4-8fcb-3f3bb903c766.png)


## Results
Below are a few sample results of topic modeling

![Topic 1](https://user-images.githubusercontent.com/20987291/216571859-4ff168ed-322c-4b01-ba38-350d7e6fe91d.png) ![Topic 2](https://user-images.githubusercontent.com/20987291/216572189-38a6532f-9896-48df-af9f-bb92fec4a981.png) ![Topic 3](https://user-images.githubusercontent.com/20987291/216572743-0493ae58-28da-48cf-9efd-b9332b0db24e.png)

- Topic 1 seem to be concerned with immune response and antibodies
- Topic 2 seem to be talking about effects of pandemic on society, mental health (stress, anxiety) and work environment (behavior, support)
- Topic 3 papers could be related to infection detection, antibody sequencing and virus itself
