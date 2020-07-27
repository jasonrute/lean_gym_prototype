import re
import sys


def extract_inductives_and_structures_from_lean_file(lean_file):
    with open(lean_file) as f:
        inductives_and_structures = []
        open_comment_lines = []
        comment = ""
        current_inductive = None
        current_structure = None  # includes structures and cases

        for line in f:
            # handle doc strings.  All docstrings are assumed to be of the form /- ... -/ (possibly over multiple lines)
            # A structure/inductive, a case of an inductive, or a structure field can all have doc strings.

            # at the end of a doc string
            if open_comment_lines:
                m = re.search(r'\s*(.*)-/\s*$', line)
                if m:
                    open_comment_lines.append(m.group(1).strip())
                    comment = " ".join(open_comment_lines).strip()
                    open_comment_lines = []
                    continue

                open_comment_lines.append(line.strip())
                continue

            # blank line
            if line.strip() == "":
                continue

            # one-line doc string
            m = re.search(r'^\s*/-(.*)-/\s*$', line)
            if m:
                comment = m.group(1).strip()
                continue

            # start of multi-line doc string
            m = re.search(r'^\s*/-(.*)\s*$', line)
            if m:
                open_comment_lines.append(m.group(1).strip())
                continue

            # start of inductive
            m = re.search(r'^\s*(?:meta\s*)?inductive\s*(\w+)\s*$', line)
            if m:
                current_inductive = {'kind': 'induct', 'name': m.group(1), 'docstring': comment, 'cases': []}
                inductives_and_structures.append(current_inductive)
                comment = ""
                continue

            # inductive case with up to 10 parameters, all of the form (name : type)
            m = re.search(
                r'^\s*\|\s*(\w+)(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?\s*:?.*\s*',
                line)
            if m:
                args = []
                for i in range(10):
                    if m.group(2 * i + 2) is not None:
                        args.append({'kind': 'arg', 'name': m.group(2 * i + 2), 'type': m.group(2 * i + 3), 'docstring': ""})
                current_structure = {'kind': 'case', 'name': m.group(1), 'docstring': comment, 'args': args}
                current_inductive['cases'].append(current_structure)
                comment = ""
                continue

            # start of structure with each field on its own line
            m = re.search(r'^\s*(?:meta\s*)?structure\s*(\w+)\s*:=\s*$', line)
            if m:
                current_structure = {'kind': 'struct', 'name': m.group(1), 'docstring': comment, 'args': []}
                inductives_and_structures.append(current_structure)
                comment = ""
                continue

            # structure field on its own line
            m = re.search(r'^\s*(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))\s*$', line)
            if m:
                arg = {'kind': 'arg', 'name': m.group(1), 'type': m.group(2), 'docstring': comment}
                current_structure['args'].append(arg)
                comment = ""
                continue

            else:
                raise Exception("Unmatched line: ", line)

    return inductives_and_structures


class ListBuilder:
    def __init__(self, sep, item_builder, rec_sub_builders=None):
        self.sep = sep
        self.item_builder = item_builder
        self.rec_sub_builders = rec_sub_builders

    def build(self, object_list, **kwargs):
        kwargs2 = kwargs.copy()
        if self.rec_sub_builders is not None:
            if '_sub_builders' in kwargs2:
                kwargs2['_sub_builders'].update(self.rec_sub_builders)
            else:
                kwargs2['_sub_builders'] = self.rec_sub_builders
        return self.sep.join(self.item_builder.build(o, **kwargs2) for o in object_list)


class ConditionalBuilder:
    def __init__(self, builders):
        self.builders = builders

    def build(self, item, **kwargs):
        for builder in self.builders:
            s = builder.build(item, **kwargs)
            if s is not None:
                return s

        raise ValueError("No conditions satsified.")


class FunctionBuilder:
    def __init__(self, f):
        self.f = f

    def build(self, item, **kwargs):
        return self.f(item)


class TemplateBuilder:
    def __init__(self, template, sub_builders=None, cond=None):
        self.cond = cond
        self.template = template
        self.sub_builders = sub_builders if sub_builders is not None else {}

    def build_code_parts(self, kwargs2):
        if '_sub_builders' in kwargs2:
            for k, builder in kwargs2['_sub_builders'].items():
                key = k.split("__")[0]
                if key in kwargs2:
                    item = kwargs2[key]
                    kwargs2[k] = builder.build(item, **kwargs2)
        for k, builder in self.sub_builders.items():
            item = kwargs2[k.split("__")[0]]
            kwargs2[k] = builder.build(item, **kwargs2)

    def build(self, object_dict, **kwargs):
        kwargs2 = kwargs.copy()
        kind = object_dict['kind']
        kwargs2['kind'] = kind
        for k, v in object_dict.items():
            if k == "kind":
                pass
            else:
                kwargs2[kind + "_" + k] = v

        # check condition
        if self.cond is not None and not self.cond(kwargs2):
            return None

        self.build_code_parts(kwargs2)

        return self.template.format(**kwargs2)


# TODO: Add has_repr instance?  (Although, could use JSON)
lean_builder = ListBuilder(
    sep='\n\n',
    item_builder=ConditionalBuilder([
        TemplateBuilder(
            cond=(lambda d: d['kind'] == "induct"),
            template=
            'meta instance {induct_name}_has_to_json : has_to_json {induct_name} :=\n'
            'has_to_json.mk $ λ s, match s with\n'
            '{induct_cases__block1}\n'
            'end\n'
            '\n'
            'private meta def decode_json_{induct_name} : json → exceptional {induct_name}\n'
            '{induct_cases__block2}\n'
            '| j := exceptional.fail $ "Unexpected form for " ++ "{induct_name}" ++ ", found: " ++ (to_string j)\n'
            '\n'
            'meta instance {induct_name}_has_from_json : has_from_json {induct_name} :=\n'
            '⟨decode_json_{induct_name}⟩\n',
            sub_builders={
                'induct_cases__block1': ListBuilder(
                    sep='\n',
                    item_builder=TemplateBuilder(
                        template=
                        '| ({induct_name}.{case_name} {case_args__list}): = json.jobject [("{case_name}", json.jobject [{case_args__kvs}])]',
                        sub_builders={
                            'case_args__list': ListBuilder(sep=" ", item_builder=TemplateBuilder(template='{arg_name}')),
                            'case_args__kvs': ListBuilder(
                                sep=", ",
                                item_builder=ConditionalBuilder([
                                    TemplateBuilder(
                                        cond=lambda d: d['induct_name'] == d['arg_type'],
                                        template='("{arg_name}", @to_json {arg_type} {arg_type}_has_to_json {arg_name})'
                                    ),
                                    TemplateBuilder(
                                        template='("{arg_name}", to_json {arg_name})'
                                    )
                                ])
                            ),
                        }
                    )
                ),
                'induct_cases__block2': ListBuilder(
                    sep = "\n",
                    item_builder=TemplateBuilder(
                        template=
                        '| (json.jobject [("{case_name}", json.jobject kvs)]) := do\n'
                        '{case_args__extractors}\n'
                        '  decoder_check_empty kvs,\n'
                        '  return $ {induct_name}.{case_name} {case_args__list}',
                        sub_builders={
                            'case_args__list': ListBuilder(sep=" ", item_builder=TemplateBuilder(template='{arg_name}')),
                            'case_args__extractors': ListBuilder(
                                sep="\n",
                                item_builder=ConditionalBuilder([
                                    TemplateBuilder(
                                        cond=lambda d: d['induct_name'] == d['arg_type'],
                                        template='  ({arg_name}, kvs) <- @decoder_get_field_value {arg_type} ⟨decode_json_{arg_type}⟩ "{arg_name}" kvs,'
                                    ),
                                    TemplateBuilder(
                                        template='  ({arg_name}, kvs) <- decoder_get_field_value {arg_type} "{arg_name}" kvs,'
                                    )
                                ])
                            )
                        }
                    )
                )
            }
        ),
        TemplateBuilder(
            cond=(lambda d: d['kind'] == "struct"),
            template=
            'meta instance {struct_name}_has_to_json : has_to_json {struct_name} :=\n'
            'has_to_json.mk $ λ s, match s with\n'
            '| ⟨{struct_args__list1}⟩ := json.jobject [{struct_args__kvs}]\n'
            'end\n'
            '\n'
            'private meta def decode_json_{struct_name} : json → exceptional {struct_name}\n'
            '| (json.jobject kvs) := do\n'
            '{struct_args__extractors}\n'
            '  decoder_check_empty kvs,\n'
            '  return $ {struct_name}.mk {struct_args__list2}\n'
            '| j := exceptional.fail $ "Unexpected form for " ++ "{struct_name}" ++ ", found: " ++ (to_string j)\n'
            '\n'
            'meta instance {struct_name}_has_from_json : has_from_json {struct_name} :=\n'
            '⟨decode_json_{struct_name}⟩\n',
            sub_builders={
                'struct_args__list1': ListBuilder(sep=", ", item_builder=TemplateBuilder(template='{arg_name}')),
                'struct_args__list2': ListBuilder(sep=" ", item_builder=TemplateBuilder(template='{arg_name}')),
                'struct_args__kvs': ListBuilder(
                    sep=", ",
                    item_builder=ConditionalBuilder([
                        TemplateBuilder(
                            cond=lambda d: d['struct_name'] == d['arg_type'],
                            template='("{arg_name}", @to_json {arg_type} {arg_type}_has_to_json {arg_name})'
                        ),
                        TemplateBuilder(
                            template='("{arg_name}", to_json {arg_name})'
                        )
                    ])
                ),
                'struct_args__extractors': ListBuilder(
                    sep="\n",
                    item_builder=ConditionalBuilder([
                        TemplateBuilder(
                            cond=lambda d: d['struct_name'] == d['arg_type'],
                            template='  ({arg_name}, kvs) <- @decoder_get_field_value {arg_type} ⟨decode_json_{arg_type}⟩ "{arg_name}" kvs,'
                        ),
                        TemplateBuilder(
                            template='  ({arg_name}, kvs) <- decoder_get_field_value {arg_type} "{arg_name}" kvs,'
                        )
                    ])
                )
            }
        )
    ])
)


# lean templates

inductive_block = """
meta instance {name}_has_to_json : has_to_json {name} := 
has_to_json.mk $ λ s, match s with{caseblocks2}
end

private meta def decode_json_{name} : json → exceptional {name}{caseblocks}
| j := exceptional.fail $ "Unexpected form for " ++ "{name}" ++ ", found: " ++ (to_string j)

meta instance {name}_has_from_json : has_from_json {name} := 
⟨decode_json_{name}⟩
"""

case_block = """
| (json.jobject [("{casename}", json.jobject kvs)]) := do{argblocks}
  decoder_check_empty kvs,
  return $ {name}.{casename} {arglist}"""

case_block2 = """
| ({name}.{casename} {arglist}) := json.jobject [("{casename}", json.jobject [{argblocks2}])]"""

arg_block = """
  ({argname}, kvs) <- decoder_get_field_value {argtype} "{argname}" kvs,"""

arg_block_rec = """
  ({argname}, kvs) <- @decoder_get_field_value {argtype} ⟨decode_json_{argtype}⟩ "{argname}" kvs,"""

arg_block2 = """("{argname}", to_json {argname})"""

arg_block2_rec = """("{argname}", @to_json {argtype} {argtype}_has_to_json {argname})"""


def make_lean_boilerplate(inductives):
    lean_code_lines = []
    for i in inductives:
        case_blocks = []
        case_blocks2 = []
        for c in i['cases']:
            arg_blocks = []
            arg_list = []
            arg_blocks2 = []
            for argname, argtype in c['args']:
                arg_list.append(argname)
                if argtype == i['name']:
                    # recursive type
                    arg_blocks.append(arg_block_rec.format(argname=argname, argtype=argtype))
                    arg_blocks2.append(arg_block2_rec.format(argname=argname, argtype=argtype))
                else:
                    arg_blocks.append(arg_block.format(argname=argname, argtype=argtype))
                    arg_blocks2.append(arg_block2.format(argname=argname))
            arg_blocks_str = "".join(arg_blocks)
            arg_list_str = " ".join(arg_list)
            arg_blocks2_str = ", ".join(arg_blocks2)
            case_blocks.append(
                case_block.format(name=i['name'], casename=c['name'], argblocks=arg_blocks_str, arglist=arg_list_str))
            case_blocks2.append(case_block2.format(name=i['name'], casename=c['name'], argblocks2=arg_blocks2_str,
                                                   arglist=arg_list_str))
        case_blocks_str = "".join(case_blocks)
        case_blocks2_str = "".join(case_blocks2)
        line = inductive_block.format(name=i['name'], caseblocks=case_blocks_str, caseblocks2=case_blocks2_str)

        lean_code_lines.append(line)

    return "\n".join(lean_code_lines)


# python boilerplate
def capcase(snake_case_var):
    return ''.join(i.capitalize() for i in snake_case_var.split('_'))


def pytype(leantype):
    if leantype in ["int", "nat"]:
        return "int"
    if leantype == "bool":
        return "bool"
    if leantype == "string":
        return "str"
    if " " in leantype:
        type1, type2 = leantype.split(" ", 1)
        type2 = type2.strip()
        if type2.startswith("(") and type2.endswith(")"):
            type2 = type2[1:-1]
        return cap_case(type1) + "[" + pytype(type2) + "]"
    return cap_case(leantype)


def pyclass(leantype):
    if leantype in ["nat", "int", "bool", "string"]:
        return None
    if " " in leantype:
        type1, type2 = leantype.split(" ", 1)
        return cap_case(type1)
    return cap_case(leantype)


cap_case_builder = FunctionBuilder(lambda s: capcase(s))
class_docstring_builder = FunctionBuilder(lambda docstring: '\n    """' + docstring + '"""' if docstring else '')
pytype_builder = FunctionBuilder(lambda leantype: pytype(leantype))
pyclass_builder = FunctionBuilder(lambda leantype: pyclass(leantype))
python_builder = ListBuilder(
    sep='\n\n\n',
    rec_sub_builders={
        'induct_name__caps': cap_case_builder,
        'induct_docstring__python': class_docstring_builder,
        'struct_name__caps': cap_case_builder,
        'struct_docstring__python': class_docstring_builder,
        'case_name__caps': cap_case_builder,
        'case_docstring__python': class_docstring_builder,
        'arg_type__pytype': pytype_builder,
        'arg_type__pyclass': pyclass_builder,
    },
    item_builder=ConditionalBuilder([
        TemplateBuilder(
            cond=(lambda d: d['kind'] == "induct"),
            template=
            'class {induct_name__caps}:{induct_docstring__python}\n'
            '{induct_cases__blocks1}\n'
            '\n'
            '    def to_dict(self) -> dict:\n'
            '        """Dictionary which can later be serialized to JSON"""\n'
            '        pass\n'
            '\n'
            '    @staticmethod\n'
            '    def from_dict(d: dict) -> "{induct_name__caps}":\n'
            '        """Build {induct_name__caps} from dictionary which was deserialized from JSON"""\n'
            '{induct_cases__blocks2}\n'
            '        raise Exception("Dict not of the correct form: " + str(d))\n'
            '\n'
            '    def __repr__(self):\n'
            '        pass\n'
            '\n'
            '\n'
            '{induct_cases__classes}',
            sub_builders={
                'induct_cases__blocks1': ListBuilder(
                    sep="\n\n",
                    item_builder=TemplateBuilder(
                        template=
                        '    @staticmethod\n'
                        '    def {case_name}({case_args__list1}) -> "{case_name__caps}{induct_name__caps}":\n'
                        '        return {case_name__caps}{induct_name__caps}({case_args__list2})',
                        sub_builders={
                            'case_args__list1': ListBuilder(
                                sep=", ",
                                item_builder=TemplateBuilder(
                                    template="{arg_name}: {arg_type__pytype}"
                                ),
                            ),
                            'case_args__list2': ListBuilder(
                                sep=", ",
                                item_builder=TemplateBuilder(template="{arg_name}")
                            ),
                        }
                    )
                ),
                'induct_cases__blocks2': ListBuilder(
                    sep="\n",
                    item_builder=TemplateBuilder(
                        template=
                        '        if "{case_name}" in d:\n'
                        '            return {case_name__caps}{induct_name__caps}.from_dict(d)'
                    )
                ),
                'induct_cases__classes': ListBuilder(
                    sep="\n\n\n",
                    item_builder=TemplateBuilder(
                        template=
                        'class {case_name__caps}{induct_name__caps}({induct_name__caps}):{case_docstring__python}\n'
                        '    def __init__(self, {case_args__list1}):{case_args__blocks1}\n'
                        '        pass\n'
                        '\n'
                        '    def to_dict(self) -> dict:\n'
                        '        """Dictionary which can later be serialized to JSON"""\n'
                        '        return {{"{case_name}": {{{case_args__blocks2}}}}}\n'
                        '\n'
                        '    @staticmethod\n'
                        '    def from_dict(d: dict) -> "{case_name__caps}{induct_name__caps}":\n'
                        '        """Build {case_name__caps}{induct_name__caps} from dictionary which was deserialized from JSON"""\n'
                        '        return {case_name__caps}{induct_name__caps}({case_args__blocks3})\n'
                        '\n'
                        '    def __repr__(self):\n'
                        '        return "{case_name__caps}{induct_name__caps}(" + {case_args__blocks4}")"',
                        sub_builders={
                            'case_args__list1': ListBuilder(
                                sep=", ",
                                item_builder=TemplateBuilder(
                                    template="{arg_name}: {arg_type__pytype}"
                                ),
                            ),
                            'case_args__blocks1': ListBuilder(
                                sep="",
                                item_builder=ConditionalBuilder([
                                    TemplateBuilder(
                                        cond=(lambda d: d['arg_type'] == 'nat'),
                                        template =
                                        '\n'
                                        '        self.{arg_name} = {arg_name}\n'
                                        '        assert {arg_name} >= 0'
                                    ),
                                    TemplateBuilder(
                                        template =
                                        '\n'
                                        '        self.{arg_name} = {arg_name}'
                                    )
                                ])
                            ),
                            'case_args__blocks2': ListBuilder(
                                sep=', ',
                                item_builder=ConditionalBuilder([
                                    TemplateBuilder(
                                        cond=(lambda d: d['arg_type'] in ['nat', 'int', 'string', 'bool']),
                                        template='"{arg_name}": self.{arg_name}'
                                    ),
                                    # TODO: Handle list case if needed?  Complicated because of polymorphism.
                                    TemplateBuilder(
                                        template='"{arg_name}": self.{arg_name}.to_dict()'
                                    )
                                ])
                            ),
                            'case_args__blocks3': ListBuilder(
                                sep=', ',
                                item_builder=ConditionalBuilder([
                                    TemplateBuilder(
                                        cond=(lambda d: d['arg_type'] in ['nat', 'int', 'string', 'bool']),
                                        template='d["{case_name}"]["{arg_name}"]'
                                    ),
                                    # TODO: Handle list case if needed?  Complicated because of polymorphism.
                                    TemplateBuilder(
                                        template='{arg_type__pyclass}.from_dict(d["{case_name}"]["{arg_name}"])'
                                    )
                                ])
                            ),
                            'case_args__blocks4': ListBuilder(
                                sep='", " + ',
                                item_builder=TemplateBuilder(
                                    template='"{arg_name} = " + repr(self.{arg_name}) + '
                                )
                            ),
                        }
                    )
                ),

            }
        ),
        TemplateBuilder(
            cond=(lambda d: d['kind'] == "struct"),
                template=
                'class {struct_name__caps}:{struct_docstring__python}\n'
                '    def __init__(self, {struct_args__list1}):{struct_args__blocks1}\n'
                '        pass\n'
                '\n'
                '    def to_dict(self) -> dict:\n'
                '        """Dictionary which can later be serialized to JSON"""\n'
                '        return {{"{struct_name}": {{{struct_args__blocks2}}}}}\n'
                '\n'
                '    @staticmethod\n'
                '    def from_dict(d: dict) -> "{struct_name__caps}":\n'
                '        """Build {struct_name__caps} from dictionary which was deserialized from JSON"""\n'
                '        return {struct_name__caps}({struct_args__blocks3})\n'
                '\n'
                '    def __repr__(self):\n'
                '        return "{struct_name__caps}(" + {struct_args__blocks4}")"',
                sub_builders={
                    'struct_args__list1': ListBuilder(
                        sep=", ",
                        item_builder=TemplateBuilder(
                            template="{arg_name}: {arg_type__pytype}"
                        ),
                    ),
                    'struct_args__blocks1': ListBuilder(
                        sep="",
                        item_builder=ConditionalBuilder([
                            TemplateBuilder(
                                cond=(lambda d: d['arg_type'] == 'nat'),
                                template =
                                '\n'
                                '        self.{arg_name} = {arg_name}\n'
                                '        assert {arg_name} >= 0'
                            ),
                            TemplateBuilder(
                                template =
                                '\n'
                                '        self.{arg_name} = {arg_name}'
                            )
                        ])
                    ),
                    'struct_args__blocks2': ListBuilder(
                        sep=', ',
                        item_builder=ConditionalBuilder([
                            TemplateBuilder(
                                cond=(lambda d: d['arg_type'] in ['nat', 'int', 'string', 'bool']),
                                template='"{arg_name}": self.{arg_name}'
                            ),
                            # TODO: Handle list case if needed?  Complicated because of polymorphism.
                            TemplateBuilder(
                                template='"{arg_name}": self.{arg_name}.to_dict()'
                            )
                        ])
                    ),
                    'struct_args__blocks3': ListBuilder(
                        sep=', ',
                        item_builder=ConditionalBuilder([
                            TemplateBuilder(
                                cond=(lambda d: d['arg_type'] in ['nat', 'int', 'string', 'bool']),
                                template='d["{struct_name}"]["{arg_name}"]'
                            ),
                            # TODO: Handle list case if needed?  Complicated because of polymorphism.
                            TemplateBuilder(
                                template='{arg_type__pyclass}.from_dict(d["{struct_name}"]["{arg_name}"])'
                            )
                        ])
                    ),
                    'struct_args__blocks4': ListBuilder(
                        sep='", " + ',
                        item_builder=TemplateBuilder(
                            template='"{arg_name} = " + repr(self.{arg_name}) + '
                        )
                    ),
                }
            )
    ])
)

python_inductive_block = '''
class {capname}:{docstring}{caseblocks1}
    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> '{capname}':
        """Build {capname} from dictionary which was deserialized from JSON"""{caseblocks2}
        
        raise Exception("Dict not of the correct form: " + str(d))
        
    def __repr__(self):
        pass

{caseclasses}'''

python_case_block1 = """

    @staticmethod
    def {casename}({arglist1}) -> '{capcasename}{capname}':
        return {capcasename}{capname}({arglist2})"""

python_case_block2 = """
        if '{casename}' in d:
            return {capcasename}{capname}.from_dict(d)"""

python_case_class = '''

class {capcasename}{capname}({capname}):{docstring}
    def __init__(self, {arglist1}):{argblocks1}
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {{'{casename}': {{{argblocks2}}}}}

    @staticmethod
    def from_dict(d: dict) -> '{capcasename}{capname}':
        """Build {capcasename}{capname} from dictionary which was deserialized from JSON"""
        return {capcasename}{capname}({argblocks3})
    
    def __repr__(self):
        return '{capcasename}{capname}(' + {argblocks4} ')'
'''

python_arg_block0 = """{argname}: {pytype}"""

python_arg_block1 = """
        self.{argname} = {argname}{condition}"""

python_arg_block2_primative = """'{argname}': self.{argname}"""
# ignore lists for now.  They make things messy b/c of polymorphism
python_arg_block2_object = """'{argname}': self.{argname}.to_dict()"""

python_arg_block3_primative = "d['{casename}']['{argname}']"
# ignore lists for now.  They make things messy b/c of polymorphism
python_arg_block3_object = "{captype}.from_dict(d['{casename}']['{argname}'])"

python_arg_block4 = """'{argname} = ' + repr(self.{argname}) +"""


primitive_types = ['int', 'nat', 'string', 'bool']


def cap_case(s):
    return ''.join(i.capitalize() for i in s.split('_'))


def pytype_from_argtype(argtype):
    if argtype in ['int', 'nat']:
        return "int"
    elif argtype == 'string':
        return 'str'
    elif argtype == "bool":
        return "bool"
    else:
        return cap_case(argtype)


def make_python_boilerplate(inductives):
    lines = []
    for i in inductives:
        case_blocks1 = []
        case_blocks2 = []
        case_classes = []
        capname = cap_case(i['name'])
        for c in i['cases']:
            arg_list = []
            arg_blocks0 = []
            arg_blocks1 = []
            arg_blocks2 = []
            arg_blocks3 = []
            arg_blocks4 = []
            for argname, argtype in c['args']:
                arg_list.append(argname)
                arg_blocks0.append(python_arg_block0.format(argname=argname, pytype=pytype_from_argtype(argtype)))
                condition = "\n        assert " + argname + " >= 0" if argtype == "nat" else ""
                arg_blocks1.append(python_arg_block1.format(argname=argname, condition=condition))
                arg_blocks4.append(python_arg_block4.format(argname=argname))
                if argtype in primitive_types:
                    arg_blocks2.append(python_arg_block2_primative.format(argname=argname))
                    arg_blocks3.append(python_arg_block3_primative.format(casename=c['name'], argname=argname))
                else:
                    arg_blocks2.append(python_arg_block2_object.format(argname=argname))
                    arg_blocks3.append(python_arg_block3_object.format(
                        captype=cap_case(argtype),
                        casename=c['name'],
                        argname=argname
                    ))

            arg_blocks1_str = "".join(arg_blocks1)
            arg_blocks2_str = ", ".join(arg_blocks2)
            arg_blocks3_str = ", ".join(arg_blocks3)
            arg_blocks4_str = "', ' + ".join(arg_blocks4)
            arg_list1_str = ", ".join(arg_blocks0)
            arg_list2_str = ", ".join(arg_list)
            capcasename = cap_case(c['name'])
            case_blocks1.append(python_case_block1.format(
                casename=c['name'],
                capname=capname,
                capcasename=capcasename,
                arglist1=arg_list1_str,
                arglist2=arg_list2_str,
            ))
            case_blocks2.append(python_case_block2.format(
                casename=c['name'],
                capname=capname,
                capcasename=capcasename
            ))
            case_classes.append(python_case_class.format(
                casename=c['name'],
                capname=capname,
                capcasename=capcasename,
                docstring='\n    """' + c['doc_string'] + '"""' if c['doc_string'] else '',
                arglist1=arg_list1_str,
                argblocks1=arg_blocks1_str,
                argblocks2=arg_blocks2_str,
                argblocks3=arg_blocks3_str,
                argblocks4=arg_blocks4_str,
            ))
        case_blocks1_str = "".join(case_blocks1)
        case_blocks2_str = "".join(case_blocks2)
        case_classes_str = "".join(case_classes)
        line = python_inductive_block.format(
            name=i['name'],
            capname=capname,
            docstring='\n    """' + i['doc_string'] + '"""' if i['doc_string'] else '',
            caseblocks1=case_blocks1_str,
            caseblocks2=case_blocks2_str,
            caseclasses=case_classes_str
        )

        lines.append(line)

    return "\n".join(lines)


def main():
    from pprint import pprint
    lean_file = sys.argv[1]
    inductives = extract_inductives_and_structures_from_lean_file(lean_file)

    #pprint(inductives)

    #print()
    #print()
    #print("=== Lean Code =====================")
    #print(lean_builder.build(inductives), flush=True)
    #print("===================================")

    #print()
    #print()
    #print("=== Python Code ===================")
    print(python_builder.build(inductives), flush=True)
    #print("===================================")

    """
    print()
    print()
    print("=== Old Lean Code =====================")

    print(make_lean_boilerplate(inductives))

    print("===================================")

    print()
    print()
    print("=== Old Python Code =====================")

    print(make_python_boilerplate(inductives))

    print("=====================================")
    """

if __name__ == '__main__':
    main()
