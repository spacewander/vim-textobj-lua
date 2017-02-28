import re

start_pattern = re.compile('(^|(?<=\W))(local\s+)?function(\s+[\w_]+)*\([^)]*\)')
end_pattern = re.compile('(^|(?<=\W))end(?=($|\W))')
single_quote = re.compile(r"(?<=[^\\])'(?:\\.|[^'\\])*'")
double_quote = re.compile(r'(?<=[^\\])"(?:\\.|[^"\\])*"')
line_comment = re.compile(r'(?<=[^\\])--.*$')

def sub_matched_with_space(match):
    return ' ' * (match.end(0)-match.start(0))

def find_start_bound(buf, cursor, include):
    """
    :param buf: vim.buf object
    :param cursor: (lnum, col) indicates the position of current cursor
    :param include: is include or not

    :return: (lnum, col) indicates bound position
    """
    lnum, col = cursor
    lnum -= 1
    cur_line = buf[lnum][:col]
    match = find_start_bound_per_line(cur_line)
    while match is None:
        lnum -= 1
        if lnum < 0:
            return None
        match = find_start_bound_per_line(buf[lnum])
    if include:
        if match.end(0) == len(buf[lnum]):
            # start from the next line if we match the end of line
            col = 1
            lnum += 1
        else:
            col = match.end(0)+1
        return (lnum+1, col)
    else:
        col = match.start(0)+1
    return (lnum+1, col)

def find_start_bound_per_line(line):
    # use space as placeholder, so that we won't lose track of col
    line = line_comment.sub(sub_matched_with_space, line)
    line = single_quote.sub(sub_matched_with_space, line)
    line = double_quote.sub(sub_matched_with_space, line)
    return start_pattern.search(line)


def find_end_bound(buf, cursor, include):
    """
    :param buf: vim.buf object
    :param cursor: (lnum, col) indicates the position of current cursor
    :param include: is include or not

    :return: (lnum, col) indicates bound position
    """
    eof = len(buf)
    lnum, col = cursor
    lnum -= 1
    match = find_end_bound_per_line(buf[lnum])
    if match and match.start(0) < col:
        match = None
    while match is None:
        lnum += 1
        if lnum >= eof:
            return None
        match = find_end_bound_per_line(buf[lnum])
    if include:
        if  match.start(0) == 0:
            # start from the prev line if we match the start of line
            lnum -= 1
            start = len(buf[lnum])+1
        else:
            # remain a space between start_bound and end_bound
            start = match.start(0)
    else:
        # remove extra line break or whitespace behind 'end'
        start = match.end(0)+1
    return (lnum+1, start)

def find_end_bound_per_line(line):
    line = line_comment.sub(sub_matched_with_space, line)
    line = single_quote.sub(sub_matched_with_space, line)
    line = double_quote.sub(sub_matched_with_space, line)
    return end_pattern.search(line)
