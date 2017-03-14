#!/usr/bin/env python
# coding: utf-8
import unittest
from lua_text_bound import find_start_bound as s_bound
from lua_text_bound import find_end_bound as e_bound


buf = {}
data = {}
buf['normal'] = """\
function ip.to_number(ip)
    local s = ""
    return common.get_ip_long(ip)
end""".splitlines()
data['normal'] = {
    "obj_type": "function",
    "cursor": (2, 2),
    "exclude": {
        "start": (1, 1),
        "end": (4, 4)
    },
    "include": {
        "start": (2, 1),
        "end": (3, 34)
    },
}

buf['keep_indent'] = """\
    function ip:to_number(ip)
        local s = ""
        return common.get_ip_long(ip)
    end""".splitlines()
data['keep_indent'] = {
    "obj_type": "function",
    "cursor": (2, 2),
    "exclude": {
        "start": (1, 5),
        "end": (4, 8)
    },
    "include": {
        "start": (2, 1),
        "end": (3, 38)
    },
}

buf['oneline'] = """\
 function ip_to_number(ip) return common.get_ip_long(ip) end  """.splitlines()
data['oneline'] = {
    "obj_type": "function",
    "cursor": (1, 30),
    "exclude": {
        "start": (1, 2),
        "end": (1, 61)
    },
    "include": {
        "start": (1, 27),
        "end": (1, 56)
    },
}


buf['not_found'] = """\
afunction ip_to_number(ip) return common.get_ip_long(ip)bend""".splitlines()
data['not_found'] = {
    "obj_type": "function",
    "cursor": (1, 30),
    "exclude": {
        "start": None,
        "end": None
    },
    "include": {
        "start": None,
        "end": None
    },
}

buf['local_func'] = """\
 local function ip_to_number(ip)
    local s = ""
    return common.get_ip_long(ip)
end""".splitlines()
data['local_func'] = {
    "obj_type": "function",
    "cursor": (2, 2),
    "exclude": {
        "start": (1, 2),
        "end": (4, 4)
    },
    "include": {
        "start": (2, 1),
        "end": (3, 34)
    },
}

buf['anonymous_func'] = """\
callback(function ip_to_number(ip)
    return common.get_ip_long(ip)
end)""".splitlines()
data['anonymous_func'] = {
    "obj_type": "function",
    "cursor": (2, 2),
    "exclude": {
        "start": (1, 10),
        "end": (3, 4)
    },
    "include": {
        "start": (2, 1),
        "end": (2, 34)
    },
}

buf['line_comment'] = """\
function ip_to_number(ip)
    local s = ""-- function ip_to_number(ip)
    return true -- function ip_to_number() return common.get_ip_long(ip) end
    -- end
\--end""".splitlines()
data['line_comment'] = {
    "obj_type": "function",
    "cursor": (3, 2),
    "exclude": {
        "start": (1, 1),
        "end": (5, 7)
    },
    "include": {
        "start": (2, 1),
        "end": (5, 3)
    },
}

buf['inside_str'] = r"""function ip_to_number(ip)
    local s = "function ip_to_number(ip)"
    s =  'function ip_to_number() return common.get_ip_long(ip) end'
    return \'end\' end""".splitlines()
data['inside_str'] = {
    "obj_type": "function",
    "cursor": (3, 2),
    "exclude": {
        "start": (1, 1),
        "end": (4, 17)
    },
    "include": {
        "start": (2, 1),
        "end": (4, 13)
    },
}

buf['find_nearest_match'] = """\
function ip_to_number(ip)
    function ip_to_number(ip)
    local s = 'function ip_to_number() return common.get_ip_long(ip) end'
    return s end
end""".splitlines()
data['find_nearest_match'] = {
    "obj_type": "function",
    "cursor": (3, 2),
    "exclude": {
        "start": (2, 5),
        "end": (4, 17)
    },
    "include": {
        "start": (3, 1),
        "end": (4, 13)
    },
}

# Don't deal with the case that cursor is inside a block comment
buf['bypass_block_comment'] = """\
function ip_to_number(ip)
    --[===[
    function ip_to_number(ip)
    ]===]-- local s = 'function ip_to_number() return common.get_ip_long(ip) end'
    --[[
    return s end]]--
end""".splitlines()
data['bypass_block_comment'] = {
    "obj_type": "function",
    "cursor": (4, 20),
    "exclude": {
        "start": (1, 1),
        "end": (7, 4)
    },
    "include": {
        "start": (2, 1),
        "end": (6, 21)
    },
}

# A if block doesn't terminate with 'else'
buf['if'] = """\
if a == b then
    return common.get_ip_long(ip)
else
    return common.get_ip_short(ip)
end""".splitlines()
data['if'] = {
    "obj_type": 'block',
    "cursor": (2, 2),
    "exclude": {
        "start": (1, 1),
        "end": (5, 4)
    },
    "include": {
        "start": (2, 1),
        "end": (4, 35)
    },
}
buf['if_oneline'] = """\
 if a == b then return common.get_ip_long(ip) end""".splitlines()
data['if_oneline'] = {
    "obj_type": 'block',
    "cursor": (1, 30),
    "exclude": {
        "start": (1, 2),
        "end": (1, 50)
    },
    "include": {
        "start": (1, 17),
        "end": (1, 45)
    },
}

buf['for'] = """\
for a, _ in pairs(b) do
    return common.get_ip_long(ip)
end""".splitlines()
data['for'] = {
    "obj_type": 'block',
    "cursor": (2, 2),
    "exclude": {
        "start": (1, 1),
        "end": (3, 4)
    },
    "include": {
        "start": (2, 1),
        "end": (2, 34)
    },
}
buf['for_oneline'] = """\
 for a, _ in pairs(b) do return common.get_ip_long(ip) end""".splitlines()
data['for_oneline'] = {
    "obj_type": 'block',
    "cursor": (1, 30),
    "exclude": {
        "start": (1, 2),
        "end": (1, 59)
    },
    "include": {
        "start": (1, 26),
        "end": (1, 54)
    },
}

buf['while'] = """\
while ture do
    return common.get_ip_long(ip)
end""".splitlines()
data['while'] = {
    "obj_type": 'block',
    "cursor": (2, 2),
    "exclude": {
        "start": (1, 1),
        "end": (3, 4)
    },
    "include": {
        "start": (2, 1),
        "end": (2, 34)
    },
}
buf['while_oneline'] = """\
 while ture do return common.get_ip_long(ip) end""".splitlines()
data['while_oneline'] = {
    "obj_type": 'block',
    "cursor": (1, 30),
    "exclude": {
        "start": (1, 2),
        "end": (1, 49)
    },
    "include": {
        "start": (1, 16),
        "end": (1, 44)
    },
}

buf['repeat'] = """\
repeat
    return common.get_ip_long(ip)
until a > 20
if""".splitlines()
data['repeat'] = {
    "obj_type": 'block',
    "cursor": (2, 2),
    "exclude": {
        "start": (1, 1),
        "end": (3, 13)
    },
    "include": {
        "start": (2, 1),
        "end": (2, 34)
    },
}
buf['repeat_oneline'] = """\
 repeat return common.get_ip_long(ip) until a > 20
if """.splitlines()
data['repeat_oneline'] = {
    "obj_type": 'block',
    "cursor": (1, 30),
    "exclude": {
        "start": (1, 2),
        "end": (1, 51)
    },
    "include": {
        "start": (1, 9),
        "end": (1, 37)
    },
}

buf['nest'] = """\
function ip_to_number(ip)
    while true do
    end
    if a == 1 then
    end s = 2
    if a ~= 1 then
    end
    return common.get_ip_long(ip)
end""".splitlines()
data['nest'] = {
    "obj_type": 'block',
    "cursor": (5, 11),
    "exclude": {
        "start": (1, 1),
        "end": (9, 4)
    },
    "include": {
        "start": (2, 1),
        "end": (8, 34)
    },
}

nest_oneline = """\
function function ip_to_number(ip) while true do s end if a == 1 then end s = 2 if a ~= 1 then end return s end end"""
buf['nest_oneline'] = nest_oneline.splitlines()
data['nest_oneline'] = {
    "obj_type": 'block',
    "cursor": (1, 77),
    "exclude": {
        "start": (1, 10),
        "end": (1, 112)
    },
    "include": {
        "start": (1, 35),
        "end": (1, 108)
    },
}

nest_oneline_only_func = """\
function function ip_to_number(ip) while true do s end if a == 1 then end s = 2 if a ~= 1 then end return s end end"""
buf['nest_oneline_only_func'] = nest_oneline_only_func.splitlines()
data['nest_oneline_only_func'] = {
    "obj_type": "function",
    "cursor": (1, 77),
    "exclude": {
        "start": (1, 10),
        "end": (1, 112)
    },
    "include": {
        "start": (1, 35),
        "end": (1, 108)
    },
}

buf['if_condition'] = """\
if xxxx == 2 then""".splitlines()
data['if_condition'] = {
    'obj_type': 'condition',
    'cursor': (1, 6),
    'exclude': {
        'start': (1, 1),
        'end': (1, 18)
    },
    'include': {
        'start': (1, 4),
        'end': (1, 13)
    }
}

buf['for_condition'] = """\
for xxxx == 2 do """.splitlines()
data['for_condition'] = {
    'obj_type': 'condition',
    'cursor': (1, 6),
    'exclude': {
        'start': (1, 1),
        'end': (1, 17)
    },
    'include': {
        'start': (1, 5),
        'end': (1, 14)
    }
}

buf['while_condition'] = """\
while(xxxx == 2)do """.splitlines()
data['while_condition'] = {
    'obj_type': 'condition',
    'cursor': (1, 8),
    'exclude': {
        'start': (1, 1),
        'end': (1, 19)
    },
    'include': {
        'start': (1, 6),
        'end': (1, 16)
    }
}

buf['if_condition_multiline'] = """\
if
    xxxx == 2
then""".splitlines()
data['if_condition_multiline'] = {
    'obj_type': 'condition',
    'cursor': (2, 6),
    'exclude': {
        'start': (1, 1),
        'end': (3, 5)
    },
    'include': {
        'start': (2, 1),
        'end': (2, 14)
    }
}

buf['for_condition_multiline'] = """\
for
    xxxx == 2
do """.splitlines()
data['for_condition_multiline'] = {
    'obj_type': 'condition',
    'cursor': (2, 6),
    'exclude': {
        'start': (1, 1),
        'end': (3, 3)
    },
    'include': {
        'start': (2, 1),
        'end': (2, 14)
    }
}

buf['while_condition_multiline'] = """\
while
xxxx == 2
    do """.splitlines()
data['while_condition_multiline'] = {
    'obj_type': 'condition',
    'cursor': (2, 8),
    'exclude': {
        'start': (1, 1),
        'end': (3, 7)
    },
    'include': {
        'start': (2, 1),
        'end': (3, 4)
    }
}

class TestLuaTextBound(unittest.TestCase):
    def run_case(self, case):
        cursor = data[case]['cursor']
        obj_type = data[case]['obj_type']
        self.assertEqual(data[case]['exclude']['start'],
                         s_bound(buf[case], cursor,
                                 include=False, obj_type=obj_type))
        self.assertEqual(data[case]['exclude']['end'],
                         e_bound(buf[case], cursor,
                                 include=False, obj_type=obj_type))
        self.assertEqual(data[case]['include']['start'],
                         s_bound(buf[case], cursor,
                                 include=True, obj_type=obj_type))
        self.assertEqual(data[case]['include']['end'],
                         e_bound(buf[case], cursor,
                                 include=True, obj_type=obj_type))

def build_test_lambda(case):
    return lambda self: TestLuaTextBound.run_case(self, case)

for case in buf:
    setattr(TestLuaTextBound, 'test_'+case, build_test_lambda(case))

if __name__ == '__main__':
    unittest.main()
