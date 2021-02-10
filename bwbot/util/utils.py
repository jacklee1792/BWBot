def prop_str(x, y):
    prop = '?' if (not x or not y) else f'{100 * x / (x + y) :.2f}'
    x = '?' if x is None else x
    y = '?' if y is None else y
    return f'{prop}%({x}/{y})'


def ratio_str(x, y):
    ratio = '?' if (x is None or y is None or y == 0) else f'{x / y :.2f}'
    x = '?' if x is None else x
    y = '?' if y is None else y
    return f'{ratio}({x}/{y})'


def tabulate(lst):
    """
    Convert a list of a lists into a str which represents a table in Discord's
    multi-line code block format

    :param lst: list of rows of the table
    :return: table as a str, in multiple line code block format
    """
    tbl_rows = ['```py']
    col_ct = len(lst[0])
    col_widths = [2] + [0] * col_ct
    for row in lst:
        for i, item in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(item)))
    for i, row in enumerate(lst):
        words = [('#' if i == 0 else f'{i}.').ljust(2)]
        for j, item in enumerate(row):
            if item is None:
                item = '?'
            words.append(str(item).ljust(col_widths[j]))
        tbl_rows.append('  '.join(words))
        tbl_rows.append('—' * len(tbl_rows[-1]))
    tbl_rows.append('```')
    return '\n'.join(tbl_rows)


