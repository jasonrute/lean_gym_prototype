import re
import sys


def extract_inductives_from_lean_file(lean_file):
    with open(lean_file) as f:
        inductives = []
        open_comment_lines = []
        comment = ""

        for line in f:
            print(line)

            if open_comment_lines:
                # in the middle of a comment
                m = re.search(r'\s*(.*)-/\s*$', line)
                if m:
                    print("Match:", m.group(1))
                    # finished comment
                    open_comment_lines.append(m.group(1).strip())
                    comment = " ".join(open_comment_lines).strip()
                    open_comment_lines = []
                    print("comment_complete:", comment)
                    continue

                open_comment_lines.append(line.strip())
                continue

            if line.strip() == "":
                continue

            m = re.search(r'^\s*/-(.*)-/\s*$', line)
            if m:
                # single line comment
                print("Match: ", m.group(1))
                comment = m.group(1).strip()
                print("comment_complete:", comment)
                continue

            m = re.search(r'^\s*/-(.*)\s*$', line)
            if m:
                # start of multiline comment
                print("Match:", m.group(1))
                open_comment_lines.append(m.group(1).strip())
                continue

            m = re.search(r'^\s*(?:meta\s*)?inductive\s*(\w+)\s*$', line)
            if m:
                # start of inductive
                print("Match:", m.group(1))
                current_inductive = {'name': m.group(1), 'doc_string': comment, 'cases': []}
                inductives.append(current_inductive)
                comment = ""
                continue

            # matches up to 10 arguments
            m = re.search(
                r'^\s*\|\s*(\w+)(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?(?:\s*\(\s*(\w+)\s*:\s*([^:]*)\s*\))?\s*:?.*\s*',
                line)
            if m:
                # start of case
                print("Match:", m.group(1), m.group(2), m.group(3))
                args = []
                for i in range(10):
                    if m.group(2 * i + 2) is not None:
                        args.append((m.group(2 * i + 2, 2 * i + 3)))
                current_inductive['cases'].append({'name': m.group(1), 'doc_string': comment, 'args': args})
                comment = ""
                continue

            else:
                raise Exception("Unmatched line: ", line)

    return inductives


# lean boilerplate

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

arg_block2 = """("{argname}", to_json {argname})"""


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
                arg_blocks.append(arg_block.format(argname=argname, argtype=argtype))
                arg_list.append(argname)
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
    inductives = extract_inductives_from_lean_file(lean_file)

    pprint(inductives)

    print()
    print()
    print("=== Lean Code =====================")

    print(make_lean_boilerplate(inductives))

    print("===================================")

    print()
    print()
    print("=== Python Code =====================")

    print(make_python_boilerplate(inductives))

    print("=====================================")


if __name__ == '__main__':
    main()
