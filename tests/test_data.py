"""Tests for plotnine_extra.data datasets."""

import pandas as pd

from plotnine_extra.data import ToothGrowth, flights, iris, penguins, wine


class TestToothGrowth:
    """Tests for the ToothGrowth dataset."""

    def test_shape(self):
        assert ToothGrowth.shape == (60, 3)

    def test_columns(self):
        assert list(ToothGrowth.columns) == ["len", "supp", "dose"]

    def test_dtypes(self):
        assert ToothGrowth["len"].dtype == "float64"
        assert ToothGrowth["supp"].dtype.name == "category"
        assert ToothGrowth["dose"].dtype == "float64"

    def test_supp_categories(self):
        assert set(ToothGrowth["supp"].cat.categories) == {"OJ", "VC"}

    def test_dose_values(self):
        assert set(ToothGrowth["dose"].unique()) == {0.5, 1.0, 2.0}

    def test_is_dataframe(self):
        assert isinstance(ToothGrowth, pd.DataFrame)


class TestPenguins:
    """Tests for the Palmer Penguins dataset."""

    def test_shape(self):
        assert penguins.shape == (344, 8)

    def test_columns(self):
        assert list(penguins.columns) == [
            "species",
            "island",
            "bill_length_mm",
            "bill_depth_mm",
            "flipper_length_mm",
            "body_mass_g",
            "sex",
            "year",
        ]

    def test_dtypes(self):
        assert penguins["species"].dtype.name == "category"
        assert penguins["island"].dtype.name == "category"
        assert penguins["bill_length_mm"].dtype == "float64"
        assert penguins["bill_depth_mm"].dtype == "float64"
        assert penguins["flipper_length_mm"].dtype == "float64"
        assert penguins["body_mass_g"].dtype == "float64"
        assert penguins["sex"].dtype.name == "category"
        assert penguins["year"].dtype == "int64"

    def test_species_categories(self):
        assert set(penguins["species"].cat.categories) == {
            "Adelie",
            "Chinstrap",
            "Gentoo",
        }

    def test_island_categories(self):
        assert set(penguins["island"].cat.categories) == {
            "Biscoe",
            "Dream",
            "Torgersen",
        }

    def test_is_dataframe(self):
        assert isinstance(penguins, pd.DataFrame)


class TestIris:
    """Tests for the Iris dataset."""

    def test_shape(self):
        assert iris.shape == (150, 5)

    def test_columns(self):
        assert list(iris.columns) == [
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
            "species",
        ]

    def test_dtypes(self):
        assert iris["sepal_length"].dtype == "float64"
        assert iris["sepal_width"].dtype == "float64"
        assert iris["petal_length"].dtype == "float64"
        assert iris["petal_width"].dtype == "float64"
        assert iris["species"].dtype.name == "category"

    def test_species_categories(self):
        assert list(iris["species"].cat.categories) == [
            "setosa",
            "versicolor",
            "virginica",
        ]

    def test_species_counts(self):
        counts = iris["species"].value_counts()
        assert all(counts == 50)

    def test_is_dataframe(self):
        assert isinstance(iris, pd.DataFrame)


class TestWine:
    """Tests for the UCI Wine dataset."""

    def test_shape(self):
        assert wine.shape == (178, 14)

    def test_first_column(self):
        assert wine.columns[0] == "class_label"

    def test_class_values(self):
        assert set(wine["class_label"].unique()) == {0, 1, 2}

    def test_dtypes(self):
        assert wine["class_label"].dtype == "int64"
        # All feature columns should be float64
        for col in wine.columns[1:]:
            assert wine[col].dtype == "float64", f"{col} is not float64"

    def test_no_missing(self):
        assert not wine.isnull().any().any()

    def test_is_dataframe(self):
        assert isinstance(wine, pd.DataFrame)


class TestFlights:
    """Tests for the Flights dataset."""

    def test_shape(self):
        assert flights.shape == (144, 3)

    def test_columns(self):
        assert list(flights.columns) == ["year", "month", "passengers"]

    def test_dtypes(self):
        assert flights["year"].dtype == "int64"
        assert flights["month"].dtype.name == "category"
        assert flights["passengers"].dtype == "int64"

    def test_month_categories(self):
        expected = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        assert list(flights["month"].cat.categories) == expected

    def test_month_ordered(self):
        assert flights["month"].cat.ordered is True

    def test_year_range(self):
        assert flights["year"].min() == 1949
        assert flights["year"].max() == 1960

    def test_is_dataframe(self):
        assert isinstance(flights, pd.DataFrame)
