from pathlib import Path
from typing import Tuple

from co2.const import Settings as SettingsInherit

_path = Path(__file__).absolute().parent


class Settings(SettingsInherit):
    # YEARS: list = list(range(2010, 2023))

    YEARS: list = [2010]

    FRANCE_NOMENCLATURE_PARAMS: dict = {
        "M14": ["M14-M14_COM_SUP3500", "M14-M14_COM_INF500", "M14-M14_COM_500_3500"],
        "M14A": ["M14-M14_COM_SUP3500", "M14-M14_COM_INF500", "M14-M14_COM_500_3500"],
        "M57": ["M57-M57", "M57-M57_A", "M57-M57_D"],
        "M57A": ["M57-M57", "M57-M57_A", "M57-M57_D"],
    }
    FRANCE_NOMENCLATURE: list = list(FRANCE_NOMENCLATURE_PARAMS.keys())

    FRANCE_PATH: Path = _path

    COA_SET_NAMING: str = "coa-{name}.csv"
    ACCOUNT_SET_NAMING: str = "account-{department}.csv"

    FRANCE_COA_CONDITION_PATH: Path = _path / "data" / "coa_condition.csv"

    FRANCE_MAPPING_COA_CARBON_PATH: Path = _path / "data" / "mapping_coa_carbon.csv"

    FRANCE_FILE_TO_EXPORT: Tuple[Tuple[Path, str], ...] = (
        (_path / "data" / "coa_categories.csv", "coa_categories.csv"),
        (_path / "data" / "coa_condition.csv", "coa_condition.csv"),
    )


settings: Settings = Settings()
