from __future__ import print_function

class LineStructure(object):
    ISUNKNOWN = 0
    ISDIGIT = 1
    ISALPHA = 2
    ISSIGN = 3

    def __init__(self, _line):
        self._ctypes = []
        self._lengths = []
        self._words = []
        self._parse_line(_line)

    def _parse_line(self, _line):
        _cstate = LineStructure.ISUNKNOWN
        _change_point = 0
        for _i in range(len(_line)):
            if _line[_i].isdigit():
                if _cstate == LineStructure.ISUNKNOWN:
                    _cstate = LineStructure.ISDIGIT
                elif _cstate != LineStructure.ISDIGIT:
                    self._ctypes.append(_cstate)
                    self._lengths.append(_i-_change_point)
                    self._words.append(_line[_change_point:_i])
                    _cstate = LineStructure.ISDIGIT
                    _change_point = _i
            elif _line[_i].isalpha():
                if _cstate == LineStructure.ISUNKNOWN:
                    _cstate = LineStructure.ISALPHA
                elif _cstate != LineStructure.ISALPHA:
                    self._ctypes.append(_cstate)
                    self._lengths.append(_i-_change_point)
                    self._words.append(_line[_change_point:_i])
                    _cstate = LineStructure.ISALPHA
                    _change_point = _i
            else:
                if _cstate == LineStructure.ISUNKNOWN:
                    _cstate = LineStructure.ISSIGN
                elif _cstate != LineStructure.ISSIGN:
                    self._ctypes.append(_cstate)
                    self._lengths.append(_i-_change_point)
                    self._words.append(_line[_change_point:_i])
                    _cstate = LineStructure.ISSIGN
                    _change_point = _i
        # process the last segment
        self._ctypes.append(_cstate)
        self._lengths.append(len(_line)-_change_point)
        self._words.append(_line[_change_point:len(_line)])

class LineTemplate(object):
    def __init__(self, _line_structure):
        self._ctypes = _line_structure._ctypes
        self._lengths = _line_structure._lengths
        self._wordsets = [set([_w,]) for _w in _line_structure._words]
        self._instances = [_line_structure, ]

    def update(self, _line_structure):
        if (self._ctypes != _line_structure._ctypes
            or self._lengths != _line_structure._lengths):
            return False
        for _tws, _w in zip(self._wordsets, _line_structure._words):
            _tws.add(_w)
        self._instances.append(_line_structure)

class LineTemplateManager(object):
    def __init__(self):
        # list of LineTemplates
        self._templates = []

    def _find_template(self, _line_structure):
        for _t in self._templates:
            if (_t._ctypes == _line_structure._ctypes
                and _t._lengths == _line_structure._lengths):
                return _t
        return None

    def update_template(self, _line_structure):
        _t = self._find_template(_line_structure)
        if _t:
            _t.update(_line_structure)
        else:
            _new_template = LineTemplate(_line_structure)
            self._templates.append(_new_template)

    def generate_formats(self, _threshold=20):
        _formats = set()
        for _t in self._templates:
            _vars = []
            for _ct, _ws in zip(_t._ctypes, _t._wordsets):
                _vars.append(len(_ws) > _threshold)
            for _i in _t._instances:
                _format = ''
                for _ct, _w, _v in zip(_i._ctypes, _i._words, _vars):
                    if _v:
                        if _ct == LineStructure.ISDIGIT:
                            _ft = '[0-9]+'
                        elif _ct == LineStructure.ISALPHA:
                            _ft = '[a-zA-Z]+'
                        else:
                            _ft = '[^0-9a-zA-Z]+'
                    else:
                        _ft = _w
                    _format += _ft
                _formats.add(_format)
        return _formats

def generate_formats(_lines, _threshold=20):
    _tm = LineTemplateManager()
    for _line in _lines:
        _ls = LineStructure(_line)
        _tm.update_template(_ls)
    return list(_tm.generate_formats(_threshold=_threshold))
