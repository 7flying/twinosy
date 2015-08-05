# -*- coding: utf-8 -*-

from prettytable import PrettyTable
from colorama import Fore, Style

def to_table(header, rows):
    """Displays info in a table.
    :header list: list of header names
    :rows list: list of rows
    """
    table = PrettyTable(header)
    table.align = 'l'
    for row in rows:
        table.add_row(row)
    return table

def p_info(text, level=1):
    print ("~" * level) + " " + text

def p_error(text, level=1):
    print (Fore.RED + ("*" * level) + " " + text + " " + ("*" * level))
    print Style.RESET_ALL
