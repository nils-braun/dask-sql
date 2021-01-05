from mock import MagicMock

import pytest
from dask.datasets import timeseries


def check_trained_model(c):
    result_df = c.sql(
        """
        SELECT * FROM PREDICT(
            MODEL my_model,
            SELECT x, y FROM timeseries
        )
        """
    ).compute()

    assert "target" in result_df.columns
    assert result_df["target"].sum() > 0


@pytest.fixture()
def training_df(c):
    df = timeseries(freq="1d").reset_index(drop=True)
    c.create_table("timeseries", df, persist=True)

    return training_df


def test_training_and_prediction(c, training_df):
    c.sql(
        """
        CREATE MODEL my_model WITH (
            model_class = 'sklearn.ensemble.GradientBoostingClassifier',
            wrap_predict = True,
            target_column = 'target'
        ) AS (
            SELECT x, y, x*y > 0 AS target
            FROM timeseries
            LIMIT 100
        )
    """
    )

    check_trained_model(c)


def test_clustering_and_prediction(c, training_df):
    c.sql(
        """
        CREATE MODEL my_model WITH (
            model_class = 'dask_ml.cluster.KMeans'
        ) AS (
            SELECT x, y
            FROM timeseries
            LIMIT 100
        )
    """
    )

    check_trained_model(c)


def test_iterative_and_prediction(c, training_df):
    c.sql(
        """
        CREATE MODEL my_model WITH (
            model_class = 'sklearn.linear_model.SGDClassifier',
            wrap_fit = True,
            target_column = 'target',
            fit_kwargs = ( classes = ARRAY [0, 1] )
        ) AS (
            SELECT x, y, x*y > 0 AS target
            FROM timeseries
            LIMIT 100
        )
    """
    )

    check_trained_model(c)


def test_wrong_training_or_prediction(c, training_df):
    with pytest.raises(KeyError):
        c.sql(
            """
            SELECT * FROM PREDICT(
            MODEL my_model,
            SELECT x, y FROM timeseries
        )
        """
        )

    with pytest.raises(ValueError):
        c.sql(
            """
            CREATE MODEL my_model WITH (
                target_column = 'target'
            ) AS (
                SELECT x, y, x*y > 0 AS target
                FROM timeseries
                LIMIT 100
            )
        """
        )

    with pytest.raises(ValueError):
        c.sql(
            """
            CREATE MODEL my_model WITH (
                model_class = 'that.is.not.a.python.class',
                target_column = 'target'
            ) AS (
                SELECT x, y, x*y > 0 AS target
                FROM timeseries
                LIMIT 100
            )
        """
        )


def test_correct_argument_passing(c, training_df):
    c.sql(
        """
        CREATE MODEL my_model WITH (
            model_class = 'mock.MagicMock',
            target_column = 'target',
            fit_kwargs = (
                first_arg = 3,
                second_arg = ARRAY [ 1, 2 ],
                third_arg = MAP [ 'a', 1 ]
            )
        ) AS (
            SELECT x, y, x*y > 0 AS target
            FROM timeseries
            LIMIT 100
        )
    """
    )

    mocked_model = c.models["my_model"]
    fit_function = mocked_model.fit

    fit_function.assert_called_once()
    call_kwargs = fit_function.call_args.kwargs
    assert call_kwargs == dict(first_arg=3, second_arg=[1, 2], third_arg={"a": 1})
