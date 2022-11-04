def get_deep_hash(obj):
    if obj is None:
        return 0
    result = 1
    for o in obj:
        element_hash = get_hash(o)
        result = 31 * result + element_hash
    return result


def get_hash(o):
    if o is None:
        return 0
    result = 1
    for o1 in o:
        result = 31 * result + o1
    return result


def deep_equals(a, b):
    if a is b:
        return True
    if a is None or b is None:
        return False
    length = len(a)
    if len(b) != length:
        return False
    for i in range(0, length):
        e1, e2 = a[i], b[i]
        if e1 is e2:
            continue
        if e1 is None:
            return False
        eq = deep_equals0(e1, e2)
        if not eq:
            return False
    return True


def deep_equals0(e1, e2):
    assert e1 is not None
    if e1 is e2:
        return True
    if e1 is None or e2 is None:
        return False
    length = len(e1)
    if len(e2) != length:
        return False
    for i in range(0, length):
        if e1[i] != e2[i]:
            return False
    return True
