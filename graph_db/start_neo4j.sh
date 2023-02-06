#!/bin/bash

docker rm -f neo4j

echo "Starting the container"
docker run -d -t\
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -v "$PWD/neo4j_data":/import \
    neo4j:5.2.0

sleep 5
echo "Importing data"
docker exec -t neo4j neo4j-admin database import full --overwrite-destination --nodes=author=/import/authors.csv --nodes=paper=/import/papers.csv --nodes=journal=/import/journals.csv --relationships=has_published=/import/author_paper_rel.csv --relationships=has_paper=/import/journal_paper_rel.csv neo4j

echo "Restarting the container"
docker restart neo4j
sleep 5
echo "Done..."
