#!/usr/bin/env python2.6
# coding: utf-8


import types

# DOUBLE_LINE_MAP = [ u'\u2800\u2880\u28a0\u28b0\u28b8',
#                     u'\u2840\u28C0\u28E0\u28F0\u28F8',
#                     u'\u2844\u28C4\u28E4\u28F4\u28FC',
#                     u'\u2846\u28C6\u28E6\u28F6\u28FE',
#                     u'\u2847\u28C7\u28E7\u28F7\u28FF', ]
DOUBLE_LINE_MAP = [
    ["⠀", "⢀", "⢠", "⢰", "⢸", ],
    ["⡀", "⣀", "⣠", "⣰", "⣸", ],
    ["⡄", "⣄", "⣤", "⣴", "⣼", ],
    ["⡆", "⣆", "⣦", "⣶", "⣾", ],
    ["⡇", "⣇", "⣧", "⣷", "⣿", ],
]

x = DOUBLE_LINE_MAP
DOT_COUNTER_BOTTOM = [
    x[0][0],
    x[1][0], x[1][1],
    x[2][1], x[2][2],
    x[3][2], x[3][3],
    x[4][3], x[4][4],
]
del x

DOT_COUNTER = [ x[0] for x in DOUBLE_LINE_MAP ] \
    + [x for x in DOUBLE_LINE_MAP[4][1:]]

DOT_COUNTER_2 = sum(DOUBLE_LINE_MAP, [])


def line_pad(linestr, padding=''):

    lines = linestr.split("\n")

    if type(padding) in types.StringTypes:
        lines = [padding + x for x in lines]

    elif callable(padding):
        lines = [padding(x) + x for x in lines]

    lines = "\n".join(lines)

    return lines


def format_line(items, sep=' ', aligns=''):

    listtype = (type([]), type(()))

    aligns = [x for x in aligns] + [''] * len(items)
    aligns = aligns[:len(items)]
    aligns = ['r' if x == 'r' else x for x in aligns]

    items = [(x if type(x) in listtype else [x])
             for x in items]

    items = [[y if isinstance(y, ColoredString) else str(y)
              for y in x]
             for x in items]

    maxHeight = max([len(x) for x in items] + [0])

    max_width = lambda x: max([y.__len__()
                               for y in x] + [0])

    widths = [max_width(x) for x in items]

    items = [(x + [''] * maxHeight)[:maxHeight]
             for x in items]

    lines = []
    for i in range(maxHeight):
        line = []
        for j in range(len(items)):
            width = widths[j]
            elt = items[j][i]

            actualWidth = elt.__len__()
            elt = str(elt)

            if actualWidth < width:
                padding = ' ' * (width - actualWidth)
                if aligns[j] == 'l':
                    elt = elt + padding
                else:
                    elt = padding + elt

            line.append(elt)

        line = sep.join(line)

        lines.append(line)

    return "\n".join(lines)


def colorize(v, total, ptn='{0}'):
    if total > 0:
        color = fading_color(v, total)
    else:
        color = fading_color(-total - v, -total)
    return ColoredString(ptn.format(v), color)


class ColoredString(object):

    def __init__(self, v, color):
        self.v = v
        if type(color) == type(''):
            color = _named_colors[color]
        self.color = color

    def __str__(self):
        return '\033[38;5;' + str(self.color) + 'm' + str(self.v) + '\033[0m'

    def __len__(self):
        return len(str(self.v))


def fading_color(v, total):
    return _clrs[fading_idx(v, total)]


def fading_idx(v, total=100):
    l = len(_clrs)
    pos = int(v * l / total + 0.5)
    pos = min(pos, l - 1)
    pos = max(pos, 0)
    return pos


_clrs = [63, 67, 37, 36, 41, 46, 82, 118,
         154, 190, 226, 220, 214, 208, 202, 196]
_named_colors = {
    'danger': _clrs[fading_idx(100)],
    'warn': _clrs[fading_idx(60)],
    'loaded': _clrs[fading_idx(30)],
    'optimal': _clrs[fading_idx(0)],
    'dark': _clrs[1],
}


if __name__ == "__main__":
    for i in range(len(_clrs)):
        print colorize(i, len(_clrs))