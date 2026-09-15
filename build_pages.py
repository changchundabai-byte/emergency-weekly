"""Build an approved public snapshot for either a root or project Pages URL."""
from pathlib import Path
import argparse, hashlib, json, re, shutil
from urllib.parse import urlsplit, unquote
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public'

def digest():
    h=hashlib.sha256()
    for p in sorted(PUBLIC.rglob('*')):
        if p.is_file():
            data=p.read_bytes()
            if p.suffix in {'.html','.css','.js','.svg'}:
                data=data.replace(b'\r\n',b'\n')
            h.update(p.relative_to(PUBLIC).as_posix().encode()+b'\0'+data+b'\0')
    return h.hexdigest()

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        for key in ('href','src','data-permalink'):
            if a.get(key): self.links.append(a[key])

def build(base, output):
    assert not base or re.fullmatch(r'/[A-Za-z0-9_.-]+',base), 'Invalid Pages base path'
    output=Path(output).resolve()
    assert output.parent == ROOT and output.name.startswith('_site'), 'Output must be a local _site directory'
    output.mkdir(exist_ok=True)
    for src in PUBLIC.rglob('*'):
        if not src.is_file(): continue
        dst=output/src.relative_to(PUBLIC); dst.parent.mkdir(parents=True,exist_ok=True)
        if src.suffix=='.html':
            t=src.read_text(encoding='utf-8')
            t=re.sub(r'((?:href|src|data-permalink)=["\'])/(?!/)',lambda m:m[1]+base+'/',t)
            dst.write_text(t,encoding='utf-8')
        else: shutil.copy2(src,dst)
    (output/'.nojekyll').touch()
    for p in output.rglob('*.html'):
        parser=Page(); parser.feed(p.read_text(encoding='utf-8'))
        for link in parser.links:
            u=urlsplit(link)
            if u.scheme or u.netloc: continue
            if not u.path:
                assert not u.fragment or u.fragment in parser.ids, f'Missing anchor {link}'
                continue
            path=unquote(u.path)
            if path.startswith('/'):
                if base: assert path.startswith(base+'/'), f'Missing base: {path}'
                target=output/path[len(base):].lstrip('/')
            else: target=p.parent/path
            if target.is_dir(): target/='index.html'
            assert target.is_file(), f'Missing file: {link}'
    return output

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--base-path',default='')
    ap.add_argument('--output',default=str(ROOT/'_site'))
    ap.add_argument('--approved-sha256')
    ap.add_argument('--print-digest',action='store_true')
    a=ap.parse_args()
    actual=digest()
    if a.print_digest: print(actual)
    else:
        if a.approved_sha256 is not None:
            assert a.approved_sha256==actual, 'The reviewed snapshot differs from current files; review again before publishing.'
        dest=build(a.base_path.rstrip('/'),a.output)
        print(json.dumps({'status':'validated','snapshot_sha256':actual,'output':str(dest)},ensure_ascii=False))
