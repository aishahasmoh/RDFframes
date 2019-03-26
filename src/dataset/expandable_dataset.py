"""Represents a flat dataset
"""

from src.query_buffer.query_operators.expandable.seed_operator import SeedOperator
from src.query_buffer.query_operators.expandable.aggregation_operator import AggregationOperator
from src.query_buffer.query_operators.shared.expansion_operator import ExpansionOperator
from src.query_buffer.query_operators.shared.filter_operator import FilterOperator
from src.query_buffer.query_operators.shared.groupby_operator import GroupByOperator
from src.query_buffer.query_operators.shared.select_operator import SelectOperator
from src.dataset.dataset import Dataset
from src.dataset.grouped_dataset import GroupedDataset
from src.utils.constants import JoinType, AggregationFunction

__author__ = """
Abdurrahman Ghanem <abghanem@hbku.edu.qa>
Aisha Mohamed <ahmohamed@qf.org.qa>
Ghadeer Abuoda <gabuoda@hbku.edu.qa>
"""


class ExpandableDataset(Dataset):
    """
    The ExpandableDataset class is a representation of a flat table filled by entities obtained by following
    a particular path in the Knowledge Graph
    """

    def __init__(self, graph, dataset_name, seed_uri_list, seed_col_name):
        """
        Initializes a new dataset whose data is derived from a graph
        :param graph: KnowledgeGraph object representing the graph(s) from where the dataset is derived
        :param dataset_name: the name of the created dataset
        :param seed_uri_list: list of uris to initialize the first column of the dataset with
        :param seed_col_name: the name of the seed column
        """
        super(ExpandableDataset, self).__init__(graph, dataset_name)

        # creating and appending the root node to the query tree
        seed_node = SeedOperator(dataset_name, seed_uri_list, seed_col_name)
        self.query_queue.append_node(seed_node)
        self.columns.append(seed_col_name)

    def expand(self, src_col_name, predicate_list):
        """
        Expand the dataset from the source column based on the given predicates. Each entry in the predicate list
        should have a predicate URI, the new column name which will be used to name the new dataset column and a flag to
        indicate whether the expansion is ingoing or outgoing from the source column
        :param src_col_name: the starting column name
        :param predicate_list: list of RDFPredicate objects
        :return: the same dataset object, but logically a new column is appended. Actually a new node representing the
        operation is added to the query_buffer
        """
        for predicate in predicate_list:
            node = ExpansionOperator(self.name, src_col_name, predicate.uri, predicate.new_col_name,
                                     predicate.direction, is_optional=predicate.optional)
            self.query_queue.append_node(node)
            self.add_column(predicate.new_col_name)
            self.add_column(predicate.uri)

        return self

    def join(self, other_dataset, join_col_name, other_dataset_join_col_name=None, join_type=JoinType.InnerJoin):
        """
        Join the self dataset with the passed dataset based on a common column holding the same name
        :param other_dataset: the other dataset to merge with
        :param join_col_name: the join column of the self dataset
        :param other_dataset_join_col_name: the join column in the other dataset, if None use join_col_name
        :param join_type: the join operation type: inner, left outer, right outer, by default inner join is performed
        :return: the same dataset object, but logically with the columns from other_dataset appended to myself.
        """
        pass

    def filter(self, conditions_dict):
        """
        Apply the given filters on the corresponding columns in the dataset.
        :param conditions_dict: mapping from column name to a list of predicates to apply on the column. Format:
        {'col_name': [pred1, pred2 ... etc], ...}
        :return: the same dataset object logically with the filtered column.
        """
        for col, conditions in conditions_dict.items():
            for cond in conditions:
                filter_node = FilterOperator(self.name, col, cond)
                self.query_queue.append_node(filter_node)
        return self

    def select_cols(self, col_list):
        """
        Select the columns of interest from the returned dataset when executing the SPARQL query
        :param col_list: list of column names to return
        :return: the same dataset
        """
        select_node = SelectOperator(self.name, col_list)
        self.query_queue.append_node(select_node)

        return self

    def group_by(self, groupby_cols_list):
        """
        Group the table by the column names passed in groupby_cols_list
        :param groupby_cols_list: list of column names to group the table by
        :return: GroupedDataset object derived from self dataset with groupby_cols_list as grouping columns
        """
        groupby_ds_name = GroupedDataset.generated_grouped_ds_name(self.name, groupby_cols_list)
        groupby_node = GroupByOperator(self.name, groupby_cols_list, groupby_ds_name)

        grouped_ds = GroupedDataset(self, groupby_cols_list, groupby_node, groupby_ds_name)
        groupby_node.grouped_dataset = grouped_ds
        self.query_queue.append_node(groupby_node)

        return grouped_ds

    # aggregate functions

    def sum(self, aggregation_fn_data):
        """
        Runs sum aggregate function on the pass src columns list and returns the summation of the passed columns as
        a list of scalar values
        :param aggregation_fn_data: list of AggregationData class holding the aggregation functions' information
        :return: the same dataset object
        """
        for agg_fn_data in aggregation_fn_data:
            agg_col = agg_fn_data.src_col_name
            tag = agg_fn_data.new_col_name
            param = agg_fn_data.agg_parameter
            agg_node = AggregationOperator(self.name, agg_col, AggregationFunction.SUM, tag, param)
            self.query_queue.append_node(agg_node)
        return self

    def avg(self, aggregation_fn_data):
        """
        Runs average aggregate function on the pass src columns list and returns the average of the passed columns as
        a list of scalar values
        :param aggregation_fn_data: list of AggregationData class holding the aggregation functions' information
        :return: the same dataset object
        """
        for agg_fn_data in aggregation_fn_data:
            agg_col = agg_fn_data.src_col_name
            tag = agg_fn_data.new_col_name
            param = agg_fn_data.agg_parameter
            agg_node = AggregationOperator(self.name, agg_col, AggregationFunction.AVG, tag, param)
            self.query_queue.append_node(agg_node)
        return self

    def min(self, aggregation_fn_data):
        """
        Runs min aggregate function on the pass src columns list and returns the min of the passed columns as
        a list of scalar values
        :param aggregation_fn_data: list of AggregationData class holding the aggregation functions' information
        :return: the same dataset
        """
        for agg_fn_data in aggregation_fn_data:
            agg_col = agg_fn_data.src_col_name
            tag = agg_fn_data.new_col_name
            param = agg_fn_data.agg_parameter
            agg_node = AggregationOperator(self.name, agg_col, AggregationFunction.MIN, tag, param)
            self.query_queue.append_node(agg_node)
        return self

    def max(self, aggregation_fn_data):
        """
        Runs max aggregate function on the pass src columns list and returns the max of the passed columns as
        a list of scalar values
        :param aggregation_fn_data:  list of AggregationData class holding the aggregation functions' information
        :return: the same dataset object
        """
        for agg_fn_data in aggregation_fn_data:
            agg_col = agg_fn_data.src_col_name
            tag = agg_fn_data.new_col_name
            param = agg_fn_data.agg_parameter
            agg_node = AggregationOperator(self.name, agg_col, AggregationFunction.MAX, tag, param)
            self.query_queue.append_node(agg_node)
        return self

    def count(self, aggregation_fn_data):
        """
        Runs count aggregate function on the pass src columns list and returns the count of the passed columns as
        a list of scalar values
        :param aggregation_fn_data: list of AggregationData class holding the aggregation functions' information
        :return: the same dataset and appends Aggregation node to the query tree
        """
        for agg_fn_data in aggregation_fn_data:
            agg_col = agg_fn_data.src_col_name
            tag = agg_fn_data.new_col_name
            param = agg_fn_data.agg_parameter

            agg_node = AggregationOperator(self.name, agg_col, AggregationFunction.COUNT, tag, param)
            self.query_queue.append_node(agg_node)
        return self

    def type(self):
        """
        return the type of the dataset as string
        :return: dataset type as string
        """
        return "ExpandableDataset"
