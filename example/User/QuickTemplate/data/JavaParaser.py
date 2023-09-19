import re

def split_ex(pattern, str):
    """
    pattern で分割した後、空白以外の文字列を含む要素を配列で返します
    """
    splitted_itmes = re.split(pattern, str)
    return [item.strip() for item in splitted_itmes if len(item.strip()) > 0]

def exclude_liner_comment(code):
    return re.sub(r'\/\/.+', '', code, re.MULTILINE)

def exclude_block_comment(code):
    return re.sub(r'\/\*(.|[\r\n])+?\*\/', '', code)

def exclude_annotation(code):
    return re.sub(r'@\w+(\(.+?\))?', '', code)

def exclude_modifiers(code):
    return re.sub(r'(\s*)(abstract|final|interface|native|private|protected|public|static|strictfp|synchronized|transient|volatile)(\s*)', '', ' ' + code + ' ').strip()

def parse_logical_name(code):
    """
    Javaのフィールド定義文のJavaDocコメントからフィールドの論理名称を抽出します
    """
    logical_name_match = re.search(r'\/\*\*((.|[\r\n])+)\*\/', code)
    if logical_name_match:
        comment_text = logical_name_match.group(1)
        for comment_line in split_ex(r'\s*[\r\n]+\s+\*', comment_text):
            return comment_line.strip()
    return None

def parse_field_declaration(code):
    statement = exclude_block_comment(code)
    declaration = exclude_annotation(statement).split('=')[0]
    return re.sub(r'[\r\n]', '', declaration).strip()

def parse_type(field_declaration):
    variable_declaration = exclude_modifiers(field_declaration)
    return re.sub(r'\s+\S+$', '', variable_declaration)

def parse_name(field_declaration):
    variable_declaration = exclude_modifiers(field_declaration)
    name_match = re.search(r'\s+(\S+)$', variable_declaration)
    return name_match.group(1) if name_match else None

def is_static_field(field_declaration):
    return field_declaration.find(' static ') >= 0

def is_final_field(field_declaration):
    return field_declaration.find(' final ') >= 0

def parse_field_code(field_code):
    field_declaration = parse_field_declaration(field_code)
    name = parse_name(field_declaration)
    if name is None:
        return None
    parsed_logical_name = parse_logical_name(field_code)
    logical_name = parsed_logical_name if parsed_logical_name is not None else name
    return {
        "name": name,
        "logical_name": logical_name,
        "type": parse_type(field_declaration),
        "final": is_final_field(field_declaration),
        "static": is_static_field(field_declaration)
    }

field_codes = split_ex(';', exclude_liner_comment(selected_string))
fields = []
for field_code in field_codes:
    field = parse_field_code(field_code)
    if field is not None:
        fields.append(field)

# export data
data = {
    'fields': fields
}
