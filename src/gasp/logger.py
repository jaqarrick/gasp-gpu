from rich.console import Console
from rich.table import Table


class Logger:
    def __init__(self, verbose: bool = False):
        self.err = Console(stderr=True)
        self.out = Console()
        # currently info only prints in verbose mode, but could change later
        self.verbose = verbose 

    def info(self, msg: str):
        if self.verbose:
            self.err.print(f"[blue]ℹnfo[/] {msg}")

    def success(self, msg: str):
        self.out.print(f"[green]success[/] {msg}")

    def error(self, msg: str):
        self.err.print(f"[red]error[/] {msg}")

    def warn(self, msg: str):
        self.err.print(f"[yellow]warn[/] {msg}")

    def table(self, title: str, columns: list[str], rows: list[list[str]], force=False):
        t = Table(title=title)
        for col in columns:
            t.add_column(col)
        for row in rows:
            t.add_row(*row)

        if self.verbose:
            self.out.print(t)