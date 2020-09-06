from typing import Dict

import dask.dataframe as dd

from dask_sql.physical.rex import RexConverter
from dask_sql.physical.rel.base import BaseRelPlugin
from dask_sql.datacontainer import DataContainer


class LogicalFilterPlugin(BaseRelPlugin):
    """
    LogicalFilter is used on WHERE clauses.
    We just evaluate the filter (which is of type RexNode) and apply it
    """

    class_name = "org.apache.calcite.rel.logical.LogicalFilter"

    def convert(
        self, rel: "org.apache.calcite.rel.RelNode", tables: Dict[str, DataContainer]
    ) -> DataContainer:
        (dc,) = self.assert_inputs(rel, 1, tables)
        df = dc.df
        cc = dc.column_container

        condition = rel.getCondition()
        df_condition = RexConverter.convert(condition, dc)
        df = df[df_condition]

        cc = self.fix_column_to_row_type(cc, rel.getRowType())
        return DataContainer(df, cc)
