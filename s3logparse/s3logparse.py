from itertools import takewhile, chain
from datetime import datetime
import csv


def raw_fields(line):
    """
    Iterate through the raw text of each field in a log line
    """
    line_chars = (c for c in line)
    while True:
        try:
            first_char = next(line_chars)
        except StopIteration:
            break
        if first_char == '[':
            yield ''.join(takewhile(lambda c: c != ']', line_chars))
            next(line_chars)
        elif first_char == '"':
            yield ''.join(takewhile(lambda c: c != '"', line_chars))
            next(line_chars)
        else:
            yield first_char + ''.join(
                list(takewhile(lambda c: c != ' ', line_chars))
            )


def shift_string_fields(fields, n):
    for _ in range(n):
        s = next(fields)
        yield None if s == '-' else s


def shift_int_fields(fields, n):
    for _ in range(n):
        i = next(fields)
        yield 0 if i == '-' else int(i)


def shift_date_fields(fields, n):
    for _ in range(n):
        d = next(fields)
        yield datetime.strptime(d, '%d/%b/%Y:%H:%M:%S %z')


def typed_fields(field_iter):
    """
    An iterator over each field converted to relevant python type
    """
    return chain.from_iterable([
        shift_string_fields(field_iter, 2),
        shift_date_fields(field_iter, 1),
        shift_string_fields(field_iter, 6),
        shift_int_fields(field_iter, 1),
        shift_string_fields(field_iter, 1),
        shift_int_fields(field_iter, 4),
        shift_string_fields(field_iter, 3)
    ])


def get_line_parser():
    """
    Return a function that can parse a single log line and return a tuple of
    log line elements of the correct type
    """

    def consume_line(line):
        # define a generator that inflates each field
        return tuple(typed_fields(raw_fields(line)))

    return consume_line


def tsv_outputter(output_stream):
    """
    Return a function that serializes a tuple of log line fields
    """
    csv_writer = csv.writer(output_stream, dialect=csv.excel_tab)

    def write_output(log_fields):
        # convert datetime field to iso format
        fields = list(log_fields)
        fields[2] = fields[2].isoformat()
        csv_writer.writerow(fields)

    return write_output
