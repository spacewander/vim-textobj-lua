if !has('python')
    echo "Error: vim-textobj-lua requires vim compiled with python support"
    finish
endif

let g:textobj_lua_no_default_key_mappings = 1

call textobj#user#plugin('lua', {
      \ 'block': {
      \   'select-a': 'al',
      \   'select-a-function': 'textobj#lua#a_block',
      \   'select-i': 'il',
      \   'select-i-function': 'textobj#lua#i_block',
      \ },
      \ 'function': {
      \   'select-a': 'af',
      \   'select-a-function': 'textobj#lua#a_func',
      \   'select-i': 'if',
      \   'select-i-function': 'textobj#lua#i_func',
      \ },
\ })
