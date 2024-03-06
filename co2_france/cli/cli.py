import time
from pathlib import Path
from typing import List, Optional

import typer
from loguru import logger

from co2_france.const import settings
from co2_france.formatter.france import France
from co2_france.utils.fr import DEPARTMENTS

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def format(
    department: Optional[str] = typer.Option(
        "74",
        "-d",
        "--department",
        help="What department do want to format",  # 74 as default value
    ),
    force: Optional[bool] = typer.Option(
        False, "-f", "--force", help="Remove confirmation"
    ),
    limit: Optional[str] = typer.Option(
        "50",
        "-l",
        "--limit",
        help="How many cities per department do you want to import ?",
    ),
    path: Optional[Path] = typer.Option(
        Path("co2-output"),
        "-p",
        "--path",
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=False,
        resolve_path=True,
        help="Where do you want to save the output file ?",
    ),
    names: Optional[List[str]] = typer.Option(
        [],
        "--name",
        help="Name of cities you only want. Separate using space.",
    ),
):
    if not path.exists():
        do_create = force
        if not do_create:
            do_create = typer.confirm(
                f"Do you want to create and use an '{path.as_posix()}' folder ?"
            )
        if do_create:
            path.mkdir()
            logger.info("Directory created with success")
        else:
            logger.info("Please set an '--path' in order to be able to use our script")
            raise typer.Abort()

    do_overwrite = force
    if not do_overwrite:
        do_overwrite = typer.confirm(
            "All the files already existing with same name in the directory will be erased are you sure you want to continue ?"
        )
    if not do_overwrite:
        raise typer.Abort()

    if not DEPARTMENTS.get(department):
        logger.error("This department does not exist")
        raise typer.Abort()

    for name, account in France.accounts.items():
        account.to_csv(
            path / settings.ACCOUNT_SET_NAMING.format(name=name), index=False
        )

    def get_department_date(department):
        department_path = path / department
        if not department_path.exists():
            department_path.mkdir()

        importer = France(limit=limit, department=department, names=names)
        logger.info(f"Starting department of '{DEPARTMENTS.get(department)}'")

        importer.account_move.to_csv(department_path / "accounting.csv", index=False)

    start_time = time.perf_counter()
    if isinstance(DEPARTMENTS.get(department), int):
        for id, name in DEPARTMENTS:
            if isinstance(name, int):
                continue

            get_department_date(id)
    else:
        get_department_date(department)
    end_time = time.perf_counter()

    final_time = end_time - start_time

    logger.info(
        f"Retrieving and formatting took {final_time} secondes / {final_time / 60} minutes to execute"
    )
