import re


def match_tag_equality(_oid, data, key, term):
    return data['tags'].get(key) == term


def match_tag_exists(_oid, data, key):
    return key in data['tags']


def match_any_tag_value(_oid, data, term):
    return term in data['tags'].itervalues()


def match_tag_regex(_oid, data, key, term):
    return key in data['tags'] and re.search(term, data['tags'][key])


def match_tag_name_regex(_oid, data, key):
    regex = re.compile(key)
    return any(regex.search(k) for k in data['tags'].iterkeys())


def match_tag_value_regex(_oid, data, term):
    regex = re.compile(term)
    return any(regex.search(v) for v in data['tags'].itervalues())


def match_id_regex(oid, _data, key):
    return re.search(key, oid)


def match_negate(oid, data, ast):
    return not match_ast(oid, data, ast)


def match_or(oid, data, *asts):
    return any(match_ast(oid, data, ast) for ast in asts)


def match_and(oid, data, *asts):
    return all(match_ast(oid, data, ast) for ast in asts)


# (oid, data) -> a key:object from the dict of objects
# ast: an AST structure from Query.compile_asts()
def match_ast(oid, data, ast):
    return globals()[ast[0]](oid, data, *ast[1:])


# objects is expected to be a dict with elements like id: data
# id's are matched, and the return value is a dict in the same format
# if you use tags, make sure data['tags'] is a dict of tags or this'll blow up
def filter_matching(ast, objects):
    return dict((oid, data) for (oid, data) in objects.items() if match_ast(oid, data, ast))
