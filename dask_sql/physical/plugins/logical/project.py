import dask.dataframe as dd

from dask_sql.physical.ral import convert_ral_to_df
from dask_sql.physical.rex import apply_rex_call


class LogicalProjectPlugin:
    class_name = "org.apache.calcite.rel.logical.LogicalProject"

    def __call__(self, ral, tables):
        input_ral = ral.getInput()
        df = convert_ral_to_df(input_ral, tables)

        named_projects = ral.getNamedProjects()

        new_columns = {}
        for expr, key in named_projects:
            new_columns[str(key)] = apply_rex_call(expr, df)

        df = df.drop(columns=list(df.columns)).assign(**new_columns)

        column_names = list(new_columns.keys())
        return df[column_names]