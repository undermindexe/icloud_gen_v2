from rich.prompt import Prompt
from rich.console import Console
from rich.columns import Columns
from rich.table import Table, box, Column
from typing import Union, List


class Interface:
    def __init__(self):
        self.console = Console()

    def ask(self, prompt: str, default: str = "") -> str:
        return Prompt.ask(prompt, default=default)

    def print(self, message: Union[str, List[str]]):
        if isinstance(message, list):
            for msg in message:
                self.console.print(msg)
        else:
            self.console.print(message)

    def print_columns(self, items: List[str]):
        self.console.print(Columns(items))

    def print_table(self, title: str, columns: List[str], rows: List[List[str]]):
        table = Table(title=title, box=box.SIMPLE)

        for col in columns:
            table.add_column(col, justify="center")

        for row in rows:
            table.add_row(*row)

        self.console.print(table)

ui = Interface()

ASK_ACTION = "\n\
[bold magenta]+-------------------+\n\
|ICloud Generator by|       https://t.me/expanse_crypto\n\
|  Expanse Crypto   |       https://t.me/expanse_chat\n\
+-------------------+\n \
*with emulation[/]\n \
\n \
[bold cyan]1.[/bold cyan] Add accounts\n \
[bold cyan]2.[/bold cyan] Generate emails\n \
[bold cyan]3.[/bold cyan] Export emails list\n \
\n\
[bold green]Select your action [cyan](Ctrl+C to exit)[reset]"