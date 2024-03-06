from pathlib import Path

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

    ACCOUNT_SET_NAMING: str = "account-{name}.csv"


settings: Settings = Settings()
