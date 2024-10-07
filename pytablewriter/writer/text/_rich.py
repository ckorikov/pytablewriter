import copy
import warnings
from typing import Any, List, Optional, Tuple, cast

from rich.console import Console
from rich.table import Table

from typepy import is_empty_sequence

import dataproperty
import typepy
from mbstrdecoder import MultiByteStrDecoder
from pathvalidate import replace_symbol

from ...error import EmptyTableDataError
from ...sanitizer import sanitize_python_var_name
from ...style import Align, FontStyle, FontWeight, Style, StylerInterface, VerticalAlign
from .._common import import_error_msg_template
from .._table_writer import AbstractTableWriter
from ._text_writer import TextTableWriter


class RichTableWriter(TextTableWriter):
    """
    A table writer class for Rich format.

        :Example:
            :ref:`example-rich-table-writer`
    """

    FORMAT_NAME = "rich"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return False

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.console = Console()
        self.table = Table(show_header=True, header_style="bold")

        self.is_padding = False
        self.indent_string = kwargs.get("indent_string", "    ")

        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)

        self.enable_ansi_escape = False

    def write_table(self, **kwargs: Any) -> None:
        """
        |write_table| with Rich table format.

        Args:

        Example:
            :ref:`example-rich-table-writer`

        .. note::
            - |None| values will be replaced with an empty value
        """

        with self._logger:
            try:
                self._verify_property()
            except EmptyTableDataError:
                self._logger.logger.debug("no tabular data found")
                return

            self._preprocess()

            self._write_header()
            self._write_body()

            self.console.print(self.table)
            

    def _write_header(self) -> None:
        if not self.is_write_header:
            return

        if is_empty_sequence(self._table_headers):
            raise ValueError("headers is empty")

        for header in self._table_headers:
            self.table.add_column(header, justify="center")

    def _write_body(self) -> None:
         for row_values in self._table_value_matrix:
            formatted_values = [
                str(value) if value is not None else "" for value in row_values
            ]
            self.table.add_row(*formatted_values)

