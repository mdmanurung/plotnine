"""
Extra datasets for plotnine_extra
=================================

Datasets included here complement those in ``plotnine.data`` and are
primarily useful for replicating examples from *ggpubr*.

Datasets
--------
ToothGrowth
    The Effect of Vitamin C on Tooth Growth in Guinea Pigs.

    The response is the length of odontoblasts (cells responsible
    for tooth growth) in 60 guinea pigs.  Each animal received one
    of three dose levels of vitamin C (0.5, 1, and 2 mg/day) by
    one of two delivery methods: orange juice (OJ) or ascorbic
    acid (VC).

    ========  ===========  ==========================================
    Column    Type         Description
    ========  ===========  ==========================================
    len       float64      Tooth length
    supp      category     Supplement type (OJ = orange juice,
                           VC = ascorbic acid)
    dose      float64      Dose in milligrams/day (0.5, 1.0, 2.0)
    ========  ===========  ==========================================

    **Shape:** 60 rows × 3 columns

    **Source:** C. I. Bliss (1952). *The Statistics of Bioassay*.
    Academic Press.

    **References:** McNeil, D. R. (1977). *Interactive Data
    Analysis*. Wiley.

penguins
    Palmer Archipelago (Antarctica) penguin data.

    Size measurements for three penguin species observed on three
    islands in the Palmer Archipelago, Antarctica. Collected by
    Dr. Kristen Gorman and the Palmer Station LTER.

    =================  ===========  ==========================================
    Column             Type         Description
    =================  ===========  ==========================================
    species            category     Penguin species (Adelie, Chinstrap,
                                    Gentoo)
    island             category     Island name (Biscoe, Dream, Torgersen)
    bill_length_mm     float64      Bill length in millimetres
    bill_depth_mm      float64      Bill depth in millimetres
    flipper_length_mm  float64      Flipper length in millimetres
    body_mass_g        float64      Body mass in grams
    sex                category     Sex (female, male)
    year               int64        Year of observation (2007-2009)
    =================  ===========  ==========================================

    **Shape:** 344 rows × 8 columns

    **Source:** Horst A. M., Hill A. P., Gorman K. B. (2020).
    *palmerpenguins: Palmer Archipelago (Antarctica) penguin data*.
    R package version 0.1.0.

iris
    Edgar Anderson's Iris data.

    Measurements (in centimetres) of sepal length and width, and
    petal length and width, for 50 flowers from each of three
    species of iris.

    ============  ===========  ==========================================
    Column        Type         Description
    ============  ===========  ==========================================
    sepal_length  float64      Sepal length in cm
    sepal_width   float64      Sepal width in cm
    petal_length  float64      Petal length in cm
    petal_width   float64      Petal width in cm
    species       category     Species (setosa, versicolor, virginica)
    ============  ===========  ==========================================

    **Shape:** 150 rows × 5 columns

    **Source:** Fisher, R. A. (1936). "The use of multiple
    measurements in taxonomic problems". *Annals of Eugenics*,
    7(2), 179-188.

    **References:** Anderson, E. (1935). "The irises of the Gaspe
    Peninsula". *Bulletin of the American Iris Society*, 59, 2-5.

wine
    UCI Wine recognition data.

    Results of a chemical analysis of wines grown in the same region
    in Italy but derived from three different cultivars. Thirteen
    continuous attributes were measured for 178 instances.

    ============================  ===========  ==============================
    Column                        Type         Description
    ============================  ===========  ==============================
    class_label                   int64        Cultivar class (0, 1, 2)
    alcohol                       float64      Alcohol content
    malic_acid                    float64      Malic acid
    ash                           float64      Ash
    alcalinity_of_ash             float64      Alcalinity of ash
    magnesium                     float64      Magnesium
    total_phenols                 float64      Total phenols
    flavanoids                    float64      Flavanoids
    nonflavanoid_phenols          float64      Non-flavanoid phenols
    proanthocyanins               float64      Proanthocyanins
    color_intensity               float64      Colour intensity
    hue                           float64      Hue
    od280/od315_of_diluted_wines  float64      OD280/OD315 of diluted wines
    proline                       float64      Proline
    ============================  ===========  ==============================

    **Shape:** 178 rows × 14 columns

    **Source:** Aeberhard, S., Coomans, D. and de Vel, O. (1992).
    UCI Machine Learning Repository. Irvine, CA: University of
    California, School of Information and Computer Science.

flights
    Monthly airline passenger numbers 1949-1960.

    ==========  ===========  ==========================================
    Column      Type         Description
    ==========  ===========  ==========================================
    year        int64        Year of observation
    month       category     Month name (Jan … Dec)
    passengers  int64        Number of airline passengers (thousands)
    ==========  ===========  ==========================================

    **Shape:** 144 rows × 3 columns

    **Source:** Box, G. E. P., Jenkins, G. M. and Reinsel, G. C.
    (1976). *Time Series Analysis, Forecasting and Control*.
    Third Edition. Holden-Day.
"""

from pathlib import Path

import pandas as pd

__all__ = (
    "ToothGrowth",
    "penguins",
    "iris",
    "wine",
    "flights",
)

_DATA_DIR = Path(__file__).parent

# -- ToothGrowth -------------------------------------------------------------
ToothGrowth = pd.read_csv(_DATA_DIR / "toothgrowth.csv")
ToothGrowth["supp"] = pd.Categorical(
    ToothGrowth["supp"], categories=["OJ", "VC"], ordered=False
)

# -- penguins -----------------------------------------------------------------
penguins = pd.read_csv(_DATA_DIR / "penguins.csv")
for _col in ("species", "island", "sex"):
    penguins[_col] = pd.Categorical(penguins[_col])

# -- iris ---------------------------------------------------------------------
iris = pd.read_csv(_DATA_DIR / "iris.csv")
iris["species"] = pd.Categorical(
    iris["species"],
    categories=["setosa", "versicolor", "virginica"],
    ordered=False,
)

# -- wine ---------------------------------------------------------------------
wine = pd.read_csv(_DATA_DIR / "wine.csv")

# -- flights ------------------------------------------------------------------
_MONTH_ORDER = [
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
flights = pd.read_csv(_DATA_DIR / "flights.csv")
flights["month"] = pd.Categorical(
    flights["month"], categories=_MONTH_ORDER, ordered=True
)
