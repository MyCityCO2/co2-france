from typing import Dict, List

import pandas
import requests
import typer
from co2.formatter import AbstractFormatter
from loguru import logger

from co2_france.const import settings

CITIES_URL: str = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-france-commune&q=&sort=com_name&rows={}&start={}&refine.dep_code={}"

CHART_OF_ACCOUNT_URL: str = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=economicref-france-nomenclature-actes-budgetaires-nature-comptes-millesime&q=&rows=-1&refine.plan_comptable={}"


class France(AbstractFormatter):
    def __init__(
        self,
        limit: int = 50,
        offset: int = 0,
        department: int = 74,
        names: List[str] = [],
    ):
        super().__init__()
        self.rename_fields: dict = {"com_name": "name", "com_siren_code": "identifier"}
        self._city_count: int = 0
        self._department = department
        self._names = names

        if self._names:
            limit = -1
            offset = 0

        self.url: str = CITIES_URL.format(limit, offset, department)

        self.account_move_dataframe = pandas.DataFrame()

    @classmethod
    def get_department_size(department: int = 74):
        cities_list = (
            requests.get(CITIES_URL.format(-1, 0, department), allow_redirects=False)
            .json()
            .get("records")
        )
        return len(cities_list)

    @property
    def currency_name(self):
        return "EUR"

    def get_cities(self):
        data = requests.get(self.url, allow_redirects=False).json().get("records")

        final_data = []

        for city in data:
            city = city.get("fields")
            if self._names and city.get("com_name") not in self._names:
                continue
            logger.info(f"Retrieving {city.get('com_name')}")

            cities_data = self.get_account_move_data(siren=city.get("com_siren_code"))

            nomens = set(map(lambda x: x.get("nomen"), cities_data))

            for nomen in nomens:
                if nomen in settings.FRANCE_NOMENCLATURE:
                    city_value = {v: city.get(k) for k, v in self.rename_fields.items()}
                    city_value |= {
                        "name": city.get(k)
                        for k, v in self.rename_fields.items()
                        if v == "name"
                    }
                    city_value |= {
                        "chart_of_account": nomen,
                    }
                    final_data.append(city_value)

        self._city_count += len(final_data)

        if not self._city_count:
            logger.error("No city found with this scope")
            raise typer.Abort()
        self._cities = final_data
        return final_data

    def get_account_move_data(
        self,
        year: int = None,
        siren: str = None,
    ):
        data = None
        if not year:
            for current_year in settings.YEARS:
                data = self.get_account_move_data(
                    year=current_year,
                    siren=siren,
                )
        else:
            url = "https://data.economie.gouv.fr/api/v2/catalog/datasets/balances-comptables-des-communes-en-{}/exports/json?offset=0&timezone=UTC"

            # Hardcoded year because the API change filter type on 2015
            refine_parameter = (
                "&refine=budget:BP" if year <= 2015 else "&refine=cbudg:1"
            )

            siren_parameter = f"&refine=siren%3A{siren}"
            limit_parameter = "&limit={}"

            url_with_parameter = (
                url.format(str(year))
                + limit_parameter.format(-1)
                + siren_parameter
                + refine_parameter
            )
            data = requests.get(
                url_with_parameter,
                allow_redirects=False,
            ).json()
        return data

    @classmethod
    def gen_account_account_data(self):
        final_accounts = {}

        for nomen in settings.FRANCE_NOMENCLATURE:
            existing_account = []
            logger.info(f"Retrieving {nomen}'s france chart of account")
            final_accounts[nomen] = []
            for parameter in settings.FRANCE_NOMENCLATURE_PARAMS[nomen]:
                res = requests.get(
                    CHART_OF_ACCOUNT_URL.format(parameter), allow_redirects=False
                )
                content = res.json()

                accounts = content.get("records")

                for account in accounts:
                    account = account.get("fields")

                    if account.get("code_nature_cpte") not in existing_account:
                        final_accounts[nomen].append(
                            {
                                "name": account.get("libelle_nature_cpte"),
                                "code": account.get("code_nature_cpte"),
                            }
                        )
                        existing_account.append(account.get("code_nature_cpte"))
        return final_accounts

    @classmethod
    @property
    def accounts(self) -> Dict[str, pandas.DataFrame]:
        accounts = {}
        for name, account in France.gen_account_account_data().items():
            accounts[name] = pandas.DataFrame(account)
        return accounts

    def get_account_move(self):
        final_data = []
        if not self._cities:
            self.get_cities()
        for city in self._cities:
            name = city.get("name")
            identifier = city.get("identifier")
            nomen = city.get("chart_of_account")

            sum_credit = 0
            sum_debit = 0

            for year in settings.YEARS:
                city_data_year = []
                date = f"{year}-12-31"  # YEAR / MONTH / DAY

                logger.info(f"Retrieving accounting set for {name} in {year}")

                city_data = self.get_account_move_data(siren=identifier, year=year)

                for aml in city_data:  # aml = account_move_line
                    account_account = str(aml.get("compte"))

                    debit = aml.get("obnetdeb") + aml.get("onbdeb")
                    sum_debit += debit

                    credit = aml.get("obnetcre") + aml.get("onbcre")
                    sum_credit += credit

                    currency = self.currency_name

                    city_data_year.append(
                        dict(
                            city=name,
                            chart_of_account=nomen,
                            identifier=identifier,
                            account=account_account,
                            currency=currency,
                            date=date,
                            debit=debit,
                            credit=credit,
                        )
                    )

                difference = sum_credit - sum_debit

                if round(difference, 2) != 0:
                    logger.error(f"The city {name} has an accounting error in {year}")
                    continue

                final_data.extend(city_data_year)

        self._accounting_data = final_data
        return final_data
