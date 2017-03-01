import itertools
import re


__all__ = ['find_start_bound', 'find_end_bound']

func_start = re.compile('(^|(?<=\W))(local\s+)?function(\s+[\w_]+)*\([^)]*\)')
end_pattern = re.compile('(^|(?<=\W))\s*end(?=($|\W))')
single_quote = re.compile(r"(?<=[^\\])'(?:\\.|[^'\\])*'")
double_quote = re.compile(r'(?<=[^\\])"(?:\\.|[^"\\])*"')
line_comment = re.compile(r'(?<=[^\\])--.*$')
block_comment_start = re.compile('--\[\[')
block_comment_end = re.compile('\]\]--')
if_start = re.compile('(^|(?<=\W))if.*\W+then(\s|$)')
do_start = re.compile('(^|(?<=\W))(for|while).*\W+do(\s|$)')
repeat_start = re.compile('(^|(?<=\W))repeat(\s|$)')
until_end = re.compile('(^|(?<=\W))\s*until\s.*$')

def sub_matched_with_space(match):
    return ' ' * (match.end(0)-match.start(0))

def find_start_bound(buf, cursor, include, only_func):
    """
    :param buf: vim.buf object
    :param cursor: (lnum, col) indicates the position of current cursor
    :param include: is include or not

    :return: (lnum, col) indicates bound position
    """
    lnum, col = cursor
    lnum -= 1
    cur_line = buf[lnum][:col]
    match, in_block_comment = find_start_bound_per_line(cur_line, only_func)
    while match is None:
        lnum -= 1
        if lnum < 0:
            return None
        match, still_in_block_comment = find_start_bound_per_line(
                buf[lnum], only_func, in_block_comment)
        if in_block_comment and still_in_block_comment:
            match = None
        in_block_comment = still_in_block_comment
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

def find_start_bound_per_line(line, only_func, in_block_comment=False):
    if in_block_comment:
        start_mark = block_comment_start.search(line)
        if not start_mark:
            return None, True
        else:
            line = line[:start_mark.start(0)]
            in_block_comment = False
    else:
        end_mark = block_comment_end.search(line)
        if end_mark:
            line = ' '*(end_mark.end(0)-1) + line[end_mark.end(0):]
            in_block_comment = True
    # use space as placeholder, so that we won't lose track of col
    line = line_comment.sub(sub_matched_with_space, line)
    line = single_quote.sub(sub_matched_with_space, line)
    line = double_quote.sub(sub_matched_with_space, line)
    found = None
    if only_func:
        for found in func_start.finditer(line): pass
    else:
        if_it = if_start.finditer(line)
        do_it = do_start.finditer(line)
        func_it = func_start.finditer(line)
        repeat_it = repeat_start.finditer(line)
        for groups in itertools.izip_longest(
                if_it, do_it, func_it, repeat_it, fillvalue=None):
            for found in groups:
                if found:
                    return (found, in_block_comment)
    return (found, in_block_comment)


def find_end_bound(buf, cursor, include, only_func):
    """
    :param buf: vim.buf object
    :param cursor: (lnum, col) indicates the position of current cursor
    :param include: is include or not

    :return: (lnum, col) indicates bound position
    """
    eof = len(buf)
    lnum, col = cursor
    lnum -= 1
    match, in_block_comment = find_end_bound_per_line(buf[lnum], only_func)
    if match and match.start(0) < col:
        match = None
    while match is None:
        lnum += 1
        if lnum >= eof:
            return None
        match, still_in_block_comment = find_end_bound_per_line(
                buf[lnum], only_func, in_block_comment)
        if in_block_comment and still_in_block_comment:
            match = None
        in_block_comment = still_in_block_comment
    if include:
        if  match.start(0) == 0:
            # start from the prev line if we match the start of line
            lnum -= 1
            start = len(buf[lnum])+1
        else:
            start = match.start(0)
    else:
        # remove extra line break or whitespace behind 'end'
        start = match.end(0)+1
    return (lnum+1, start)

def find_end_bound_per_line(line, only_func, in_block_comment=False):
    if in_block_comment:
        end_mark = block_comment_end.search(line)
        if not end_mark:
            return None, True
        else:
            line = ' '*(end_mark.end(0)-1) + line[end_mark.end(0):]
            in_block_comment = False
    else:
        start_mark = block_comment_start.search(line)
        if start_mark:
            line = line[:start_mark.start(0)]
            in_block_comment = True
    line = line_comment.sub(sub_matched_with_space, line)
    line = single_quote.sub(sub_matched_with_space, line)
    line = double_quote.sub(sub_matched_with_space, line)
    if only_func:
        return (end_pattern.search(line), in_block_comment)
    else:
        # end_bound may not match start bound if the syntax is incorrect
        found = until_end.search(line)
        if not found:
            found = end_pattern.search(line)
        return (found, in_block_comment)
