#!/usr/bin/env python
# coding: utf-8
import unittest
from lua_text_bound import find_start_bound as s_bound
from lua_text_bound import find_end_bound as e_bound


buf = {}
data = {}
buf['normal'] = """\
function ip_to_number(ip)
    local s = ""
    return common.get_ip_long(ip)
end""".splitlines()
data['normal'] = {
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

buf['oneline'] = """\
 function ip_to_number(ip) return common.get_ip_long(ip) end  """.splitlines()
data['oneline'] = {
    "cursor": (1, 30),
    "exclude": {
        "start": (1, 2),
        "end": (1, 61)
    },
    "include": {
        "start": (1, 27),
        "end": (1, 57)
    },
}


buf['not_found'] = """\
afunction ip_to_number(ip) return common.get_ip_long(ip)bend""".splitlines()
data['not_found'] = {
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

class TestLuaTextBound(unittest.TestCase):
    def run_case(self, case):
        cursor = data[case]['cursor']
        self.assertEqual(data[case]['exclude']['start'],
                         s_bound(buf[case], cursor, False))
        self.assertEqual(data[case]['exclude']['end'],
                         e_bound(buf[case], cursor, False))
        self.assertEqual(data[case]['include']['start'],
                         s_bound(buf[case], cursor, True))
        self.assertEqual(data[case]['include']['end'],
                         e_bound(buf[case], cursor, True))

def build_test_lambda(case):
    return lambda self: TestLuaTextBound.run_case(self, case)

for case in buf:
    setattr(TestLuaTextBound, 'test_'+case, build_test_lambda(case))

if __name__ == '__main__':
    unittest.main()
