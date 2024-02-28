import typer

cli = typer.Typer(no_args_is_help=True)

@cli.command()
def hello():
    print("Hello from mycityco2")
    
@cli.command()
def goodbye():
    print("Goodbye from mycityco2")