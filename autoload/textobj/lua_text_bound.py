import itertools
import re


__all__ = ['find_start_bound', 'find_end_bound']

_func_start = '(local\s+)?function(\s+\w+)?\([^)]*\)'
func_start = re.compile('(^|(?<=\W))%s' % _func_start)
# keep a space before end pattern
_block_end = '\s*end(?=($|\W))'
func_end = re.compile('(^|(?<=\W))%s' % _block_end)
single_quote = re.compile(r"(?<=[^\\])'(?:\\.|[^'\\])*'")
double_quote = re.compile(r'(?<=[^\\])"(?:\\.|[^"\\])*"')
line_comment = re.compile(r'(?<=[^\\])--.*$')
block_comment_start = re.compile('--\[=*\[')
block_comment_end = re.compile('\]=*\]--')
_if_start = 'if\W+.*\W+then(\s|$)'
_do_start = '(for|while)\W+.*\W+do(\s|$)'
_repeat_start = 'repeat(\s|$)'
block_start = re.compile('(^|(?<=\W))(%s|%s|%s|%s)' % (_func_start, _if_start,
                                                       _do_start, _repeat_start))
_until_end = '\s*until\s.*$'
block_end = re.compile('(^|(?<=\W))(%s|%s)' % (_until_end, _block_end))

cond_start = re.compile(r'(^|(?<=\W))(if|for|while)(\s|$|(?=\W))')
cond_end = re.compile(r'(^|(?<=\W))(then|do)(?=\W|$)')

def sub_matched_with_space(match):
    return ' ' * (match.end(0)-match.start(0))

def find_start_bound(buf, cursor, include, obj_type):
    """
    :param buf: vim.buf object
    :param cursor: (lnum, col) indicates the position of current cursor
    :param include: is include or not

    :return: (lnum, col) indicates bound position
    """
    lnum, col = cursor
    lnum -= 1
    cur_line = buf[lnum][:col]
    # 0 <- found!
    # if .. then
    #   1
    #   if then -1
    #       2 if then 3 end 2 +0
    #   end     +1
    #   1 <- start from here
    match, in_block_comment, level = find_start_bound_per_line(cur_line, obj_type, level=1)
    while level > 0:
        lnum -= 1
        if lnum < 0:
            return None
        if obj_type == 'function' and level > 1:
            obj_type = 'block'
        match, in_block_comment, level = find_start_bound_per_line(
                buf[lnum], obj_type, in_block_comment, level)
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

def find_start_bound_per_line(line, obj_type, in_block_comment=False, level=1):
    if in_block_comment:
        start_mark = block_comment_start.search(line)
        if not start_mark:
            # still in block comment, ignore anything
            return None, True, level
        else:
            # blah blah --[[ blah blah
            padding = ' '*(len(line)-start_mark.start(0)+1)
            line = line[:start_mark.start(0)] + padding
            in_block_comment = False
    else:
        end_mark = block_comment_end.search(line)
        if end_mark:
            # blah blah ]]-- blah blah
            line = ' '*end_mark.end(0) + line[end_mark.end(0):]
            in_block_comment = True
    # use space as placeholder, so that we won't lose track of col
    line = line_comment.sub(sub_matched_with_space, line)
    line = single_quote.sub(sub_matched_with_space, line)
    line = double_quote.sub(sub_matched_with_space, line)

    if obj_type == 'condition':
        cond_start_it = reversed([match for match in cond_start.finditer(line)])
        try:
            cond_found = cond_start_it.next()
        except StopIteration:
            cond_found = None
        # Don't support nest condtion
        return (cond_found, in_block_comment, level if cond_found is None else 0)

    # we need to iterate from right to left
    start_it = reversed([match for match in block_start.finditer(line)])
    end_it = reversed([match for match in block_end.finditer(line)])
    for pair in itertools.izip_longest(start_it, end_it):
        start_found, end_found = pair
        if not start_found:
            level += 1
        elif not end_found:
            level -= 1
            if level <= 0:
                # find the first function start mark when level <= 0
                if (obj_type != 'function') or (start_found.group(0)[-1] == ')'):
                    return (start_found, in_block_comment, 0)
    return (None, in_block_comment, level)


def find_end_bound(buf, cursor, include, obj_type):
    """
    :param buf: vim.buf object
    :param cursor: (lnum, col) indicates the position of current cursor
    :param include: is include or not

    :return: (lnum, col) indicates bound position
    """
    eof = len(buf)
    lnum, col = cursor
    lnum -= 1
    #   1 <- start from here
    #   if then +1
    #      2  if then 3 end 2
    #   end -1
    # end -1
    # 0 <- found!
    match, in_block_comment, level = find_end_bound_per_line(buf[lnum],
            obj_type, start_col=col, level=1)
    while level > 0:
        lnum += 1
        if lnum >= eof:
            return None
        if obj_type == 'function' and level > 1:
            obj_type = 'block'
        match, in_block_comment, level = find_end_bound_per_line(
                buf[lnum], obj_type,
                in_block_comment, level=level)
    if include:
        if  match.start(0) == 0:
            # start from the prev line if we match the start of line
            lnum -= 1
            end = len(buf[lnum])+1
        else:
            end = match.start(0)
    else:
        # remove extra line break or whitespace behind 'end'
        end = match.end(0)+1
    return (lnum+1, end)

# mirror of find_start_bound_per_line
def find_end_bound_per_line(line, obj_type, in_block_comment=False,
        start_col=0, level=1):
    if in_block_comment:
        end_mark = block_comment_end.search(line)
        if not end_mark:
            return None, True, level
        else:
            line = ' '*end_mark.end(0) + line[end_mark.end(0):]
            in_block_comment = False
    else:
        start_mark = block_comment_start.search(line)
        if start_mark:
            padding = ' '*(len(line)-start_mark.start(0)+1)
            line = line[:start_mark.start(0)] + padding
            in_block_comment = True
    line = line_comment.sub(sub_matched_with_space, line)
    line = single_quote.sub(sub_matched_with_space, line)
    line = double_quote.sub(sub_matched_with_space, line)
    if start_col != 0:
        line = ' '*start_col +  line[start_col:]

    if obj_type == 'condition':
        cond_found = cond_end.search(line)
        return (cond_found, in_block_comment, level if cond_found is None else 0)

    start_it = block_start.finditer(line)
    end_it = block_end.finditer(line)
    for pair in itertools.izip_longest(start_it, end_it):
        start_found, end_found = pair
        if not start_found:
            level -= 1
            if level <= 0:
                if obj_type == 'function':
                    match = end_found.group(0).lstrip()
                    # match '\s*until'?
                    if match[0] == 'u':
                        continue
                return (end_found, in_block_comment, 0)
        elif not end_found:
            level += 1
    return (None, in_block_comment, level)
