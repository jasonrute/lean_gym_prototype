def load_array(f):
    x = []
    line = f.readline()
    while line != "</ARRAY>\n":
        v = load_json(f, line)
        x.append(v)
        line = f.readline()

    return x


def load_object(f):
    x = {}
    line = f.readline()
    while line != "</OBJECT>\n":
        assert line == "<KEY>\n"
        k = load_key(f)
        v = load_json(f)
        x[k] = v
        line = f.readline()

    return x


def load_key(f):
    lines = []
    line = f.readline()
    while line != "</KEY>\n":
        lines.append(line)
        line = f.readline()
    x = "".join(lines)[:-1]

    return x


def load_string(f):
    lines = []
    line = f.readline()
    while line != "</STRING>\n":
        lines.append(line)
        line = f.readline()
    x = "".join(lines)[:-1]

    return x


def load_int(f):
    line = f.readline()
    x = int(line)

    line = f.readline()
    assert line == "</INT>\n"
    return x


def load_float(f):
    line = f.readline()
    x = float(line)

    line = f.readline()
    assert line == "</FLOAT>\n"
    return x


def load_bool(f):
    line = f.readline()
    if line == "true\n":
        x = True
    elif line == "false\n":
        x = False
    else:
        raise Exception(line)

    line = f.readline()
    assert line == "</BOOL>\n"
    return x


def load_null(f):
    x = None

    line = f.readline()
    assert line == "</NULL>\n"
    return x


def load_json_message(f):
    line = f.readline()
    assert line == "<JSON_MESSAGE>\n"
    x = load_json(f)
    line = f.readline()
    assert line == "</JSON_MESSAGE>\n"

    return x


def load_json(f, flag=None):
    if flag is None:
        line = f.readline()
    else:
        line = flag

    if line == "<ARRAY>\n":
        x = load_array(f)
    elif line == "<OBJECT>\n":
        x = load_object(f)
    elif line == "<STRING>\n":
        x = load_string(f)
    elif line == "<INT>\n":
        x = load_int(f)
    elif line == "<FLOAT>\n":
        x = load_float(f)
    elif line == "<BOOL>\n":
        x = load_bool(f)
    elif line == "<NULL>\n":
        x = load_null(f)
    else:
        raise Exception(line)

    return x


def json_lines(x):
    lines = []
    if isinstance(x, dict):
        lines.append("<OBJECT>")
        for k, v in x.items():
            lines.append("<KEY>")
            lines.append(k)
            lines.append("</KEY>")
            lines.extend(json_lines(v))
        lines.append("</OBJECT>")
    elif isinstance(x, list):
        lines.append("<ARRAY>")
        for v in x:
            lines.extend(json_lines(v))
        lines.append("</ARRAY>")
    elif isinstance(x, bool):
        lines.append("<BOOL>")
        if x:
            lines.append("true")
        else:
            lines.append("false")
        lines.append("</BOOL>")
    elif isinstance(x, int):
        lines.append("<INT>")
        lines.append(repr(x))
        lines.append("</INT>")
    elif isinstance(x, float):
        lines.append("<FLOAT>")
        lines.append(repr(x))
        lines.append("</FLOAT>")
    elif isinstance(x, str):
        lines.append("<STRING>")
        lines.append(x)
        lines.append("</STRING>")
    elif x is None:
        lines.append("<NULL>")
        lines.append("</NULL>")
    else:
        raise Exception(x)

    return lines


def json_write(x, f):
    for l in json_lines(x):
        print(l, file=f, flush=True)