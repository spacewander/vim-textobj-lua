let s:lua_text_bound_path = expand('<sfile>:p:h')

function! textobj#lua#block(is_include, obj_type) abort
python << EOF
import sys
import vim
plugin_path = vim.eval('s:lua_text_bound_path')
sys.path.append(plugin_path)
import lua_text_bound


inc = vim.eval('a:is_include') == 'i'
ot = vim.eval('a:obj_type')
cb = vim.current.buffer
cc = vim.current.window.cursor
try:
    start_pos = lua_text_bound.find_start_bound(cb, cc, inc, ot)
    if start_pos is None:
        raise Exception
    start_pos_str = "[0, %d, %d, 0]" % start_pos
    end_pos = lua_text_bound.find_end_bound(cb, cc, inc, ot)
    if end_pos is None:
        raise Exception
    end_pos_str = "[0, %d, %d, 0]" % end_pos
    vim.command("let pos = ['v', %s, %s]" % (start_pos_str, end_pos_str))
except:
    vim.command("let pos = 0")
EOF
    return pos
endfunction

function! textobj#lua#a_block() abort
    return textobj#lua#block('a', 'block')
endfunction

function! textobj#lua#i_block() abort
    return textobj#lua#block('i', 'block')
endfunction

function! textobj#lua#a_func() abort
    return textobj#lua#block('a', 'function')
endfunction

function! textobj#lua#i_func() abort
    return textobj#lua#block('i', 'function')
endfunction

function! textobj#lua#a_cond() abort
    return textobj#lua#block('a', 'condition')
endfunction

function! textobj#lua#i_cond() abort
    return textobj#lua#block('i', 'condition')
endfunction
