"""Compare offline MCP-style tool inventories. Never calls a server or tool."""
import argparse
import hashlib
import json

MAX_BYTES = 1024 * 1024
MAX_DEPTH = 64


def check_depth(value):
    pending = [(value, 0)]
    while pending:
        node, depth = pending.pop()
        if depth > MAX_DEPTH:
            raise ValueError("inventory nesting exceeds limit")
        if isinstance(node, dict):
            pending.extend((v, depth + 1) for v in node.values())
        elif isinstance(node, list):
            pending.extend((v, depth + 1) for v in node)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def inventory(doc):
    if type(doc) is not dict or set(doc)!={'tools'} or type(doc['tools']) is not list:
        raise ValueError('expected object with tools list only')
    result={}
    for tool in doc['tools']:
        if type(tool) is not dict or not {'name','inputSchema'} <= set(tool):
            raise ValueError('tool needs name and inputSchema')
        name=tool['name']
        if type(name) is not str or not name.strip() or name in result:
            raise ValueError('tool names must be nonempty and unique')
        if type(tool['inputSchema']) is not dict or type(tool.get('description','')) is not str:
            raise ValueError('invalid schema or description type')
        # Include every field, including unknown extensions. Nothing is silently ignored.
        fingerprint(tool)
        result[name]=tool
    return result


def compare(before,after):
    old,new=inventory(before),inventory(after)
    added=sorted(set(new)-set(old)); removed=sorted(set(old)-set(new))
    changed=[]; unchanged=[]
    for name in sorted(set(old)&set(new)):
        if fingerprint(old[name])==fingerprint(new[name]):
            unchanged.append(name); continue
        fields=sorted(k for k in set(old[name])|set(new[name])
                      if k not in old[name] or k not in new[name] or fingerprint(old[name][k])!=fingerprint(new[name][k]))
        changed.append({'name':name,'fields':fields,'before_sha256':fingerprint(old[name]),'after_sha256':fingerprint(new[name])})
    return {'review_required':bool(added or removed or changed), 'added':added,'removed':removed,
            'changed':changed,'unchanged':unchanged,'before_sha256':fingerprint(before),'after_sha256':fingerprint(after)}


def load(path):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise ValueError('duplicate JSON key')
            d[k]=v
        return d
    with open(path, 'rb') as f:
        raw = f.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('inventory exceeds byte limit')
    try:
        doc = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite number')))
    except RecursionError as exc:
        raise ValueError('inventory nesting exceeds parser limit') from exc
    check_depth(doc)
    return doc


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('before');p.add_argument('after');a=p.parse_args()
    try: result=compare(load(a.before),load(a.after))
    except (OSError,ValueError,TypeError):
        print(json.dumps({'review_required':True,'error':'invalid or unreadable inventory'}));return 2
    print(json.dumps(result,indent=2));return 1 if result['review_required'] else 0


if __name__=='__main__':raise SystemExit(main())
