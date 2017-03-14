# vim-textobj-lua - Provide text objects for Lua code

[![Build Status](https://travis-ci.org/spacewander/vim-textobj-lua.png)](https://travis-ci.org/spacewander/vim-textobj-lua)

## Requirement

[vim-textobj-user](https://github.com/kana/vim-textobj-user)

## Usage

This plugin add following key mappings defined in Visual mode and Operator-pending mode.

#### \<Plug\>(textobj-lua-block-a)
Default:
```
omap <buffer> al <Plug>(textobj-lua-block-a)
xmap <buffer> al <Plug>(textobj-lua-block-a)
```

Select a Lua block. More precisely, it selects lines
belong to:
- for...do...end block
- if...then...end block
- while...do...end block
- repeat...until... block
- function...end block

#### \<Plug\>(textobj-lua-block-i)
Default:
```
omap <buffer> il <Plug>(textobj-lua-block-i)
xmap <buffer> il <Plug>(textobj-lua-block-i)
```

Like `<Plug>(textobj-lua-block-a)`, but it doesn't
include start and end marks.

#### \<Plug\>(textobj-lua-function-a)
Default:
```
omap <buffer> af <Plug>(textobj-lua-function-a)
xmap <buffer> af <Plug>(textobj-lua-function-a)
```

Select a Lua function.

#### \<Plug\>(textobj-lua-function-i)
Default:
```
omap <buffer> if <Plug>(textobj-lua-function-i)
xmap <buffer> if <Plug>(textobj-lua-function-i)
```

Like `<Plug>(textobj-lua-function-a)`, but it doesn't
include function definition and end mark.

#### \<Plug\>(textobj-lua-condition-a)
Default:
```
omap <buffer> ac <Plug>(textobj-lua-condition-a)
xmap <buffer> ac <Plug>(textobj-lua-condition-a)
```

Select a Lua condition region. More precisely, it selects
words contains:
- for...do
- if...then
- while...do

#### \<Plug\>(textobj-lua-condition-i)
Default:
```
omap <buffer> ic <Plug>(textobj-lua-condition-i)
xmap <buffer> ic <Plug>(textobj-lua-condition-i)
```

Like `<Plug>(textobj-lua-condition-a)`, but it doesn't
include start and end marks like 'for', 'if' and so on.

For further reading, please `:vert help textobj-lua`.
