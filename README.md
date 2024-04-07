# [RDFFrames: Knowledge Graph Access for Machine Learning Tools](https://arxiv.org/abs/2002.03614)
An open source python framework for efficient and scalable processing of knowledge graphs. 
It enables data scientists to extract data from knowledge graphs encoded in [RDF](https://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/) format in familiar tabular formats using procedural Python API calls.
RDFFrames is integrated in the Python PyData software stack. It provides an easy-to-use, efficient, and scalable API for users who are familiar with the PyData (Python for Data) ecosystem but are not experts in [SPARQL](https://www.w3.org/TR/sparql11-query/).
The API calls are internally converted into optimized SPARQL queries, which are then executed on a local RDF engine or a remote SPARQL endpoint.
RDFFRames returns results in a tabular format, such as a pandas dataframe.

RDFframes processes and exports datasets from KG databases 2x faster than the state-of-the-art alternative. The project was published in [VLDBJ 2022](https://link.springer.com/article/10.1007/s00778-021-00690-5). A Demo was Published in [VLDB 2020](https://dl.acm.org/doi/pdf/10.14778/3415478.3415501). 

## Requirement to Use RDFframes

1. We assume knowledge graohs are stored in an RDF database engine. One database can store one or more RDF knowledge graphs (e.g., Virtuoso). Users should have access to a local KG database or a SPARQL endpoint providing access to such a knowledge graphs. RDFframes handles all communication and integration issues with the engine or SPARQL endpoint. 

2. Install the RDFframes library via pip by using:
   ```
   $ pip install RDFframes
   ```   


## Getting started
Import RDFframes in your code 
```python
from rdfframes.client.http_client import HttpClientDataFormat, HttpClient
from rdfframes.knowledge_graph import KnowledgeGraph
```

First create a ``KnowledgeGraph`` to specify any namespaces (prefixes) that will be used in the API calls and optionally the graph name and URI.
By default, a ``KnowledgeGraph`` is initialized to be able to query [dbpedia](http://dbpedia.org) and [dblp](http://dblp.l3s.de).
For example, to initialize a graph that can query dblp with the following prefixes, we use the following API call:
```python
graph = KnowledgeGraph(prefixes={
                               "swrc": "http://swrc.ontoware.org/ontology#",
                               "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                               "dc": "http://purl.org/dc/elements/1.1/",
                           })
```

Then create a ``Dataset`` using one of our API functions. All the API functions are methods in the
```KnowledgeGraph``` class. 
For example, to retrieves all papers in the dblp graph, we retrieve all instances of the class ``swrc:InProceedings``:

```python
dataset = graph.entities(class_name='swrc:InProceedings',
                             entities_col_name='paper')
```

There are two types of datasets in RDFframes: ``ExpandableDataset`` and ``GroupedDataset``. 
An ``ExpandableDataset`` represents a simple flat table, while a ``GroupedDataset`` is a table split into groups as a result of a group-by operation.
The ``entities`` methods returns an ``ExpandableDataset``.

After instantiating a dataset, you can use the API calls to process the data and perform operations on it. 
For example, the following code retrieves all authors and titles of conference papers:
```python
dataset = dataset.expand(src_col_name='paper', predicate_list=[
        RDFPredicate('dc:title', 'title'),
        RDFPredicate('dc:creator', 'author'),
        RDFPredicate('swrc:series', 'conference')])\
```

Using a ``group_by`` operation to group papers by author results in a ``GroupedDataset``:
```python
grouped_dataset = dataset.group_by(['author'])
```

Aggregation operation can be done on both ``ExpandableDataset`` and ``GroupedDataset`` datasets.
For example, the following code counts the number of papers per author and keeps only the authors that have more than 20 papers:
```python
grouped_dataset = grouped_dataset.count(aggregation_fn_data=[AggregationData('paper', 'papers_count')])\
        .filter(conditions_dict={'papers_count': ['>= 20']})
```

## Convenience Functions to Create an Initial Dataset

To create an initial ```Dataset```, you need to use one of the convenience functions. The API 
provides convenience functions that can be used by most of the machine learning and data analytics tasks. 
The convenience functions on the ``KnowledgeGraph`` return an ``ExpandableDataset``.
Some of the funcions included are:

```python
KnowledgeGraph.classes_and_freq()
```
This function retrieves all the classes in the graph and all the number of instances of each class.
It returns a table of two columns, the first one contains the name of the class and the second one
contains the name of the frequency of the clases.
```python
KnowledgeGraph.features_and_freq(class_name)
```
Retrieves all the features of the instances of the class ```class_name``` and how many instances have each features.
This is critical for many machine learning tasks as knowing how many observed features of entities helps us decide 
on which features to use for.
```python
KnowledgeGraph.entities(class_name)
```
Retrieves all the instances of the class ```class_name```. This is the starting point for most machine 
learning models. The return dataset contains one column of the entities of the specified class and can be
expanded to add features of the instances.
```python
KnowledgeGraph.features(class_name)
```
Retrieves all the features of the class ```class_name```. This function can be used to explore the dataset and learn
what features are available in the data for a specific class.
```python
KnowledgeGraph.entities_and_features(class_name, features, )
```
Retrieves all instances of the class ```class_name``` and the features of the instances specified in the list 
```features```.
```python
KnowledgeGraph.num_entities(class_name)
```
Returns the number of instances of the class ```class_name``` in the dataset.
```python
KnowledgeGraph.feature_domain_range(feature)
```
Returieves the domain (subjects) and the range (objects) of the predicate ```feature``` occuring in the dataset.
```python
KnowledgeGraph.describe_entity(entity)
```
Returns the class and features of the entity.
## Example Applications
Multiple case studies using RDFFrames are in the [case_studies](https://github.com/aishahasmoh/RDFframes/tree/master/case_studies) folder.




