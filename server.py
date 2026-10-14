"""Courses Hub local: Python 3.11+, sem dependências externas."""
import base64, hashlib, json, mimetypes, re, sqlite3, threading
from contextlib import contextmanager
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote

ROOT = Path(__file__).resolve().parent
DATA = ROOT / '.data'
DATA.mkdir(exist_ok=True)
LOCK = threading.Lock()
VIDEO = {'.mp4', '.webm', '.m4v', '.mov'}
MATERIAL = {'.py', '.txt', '.pdf', '.ipynb', '.md', '.csv', '.json', '.zip'}

@contextmanager
def db():
    con = sqlite3.connect(DATA / 'hub.db')
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()

with db() as con:
    con.executescript('CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY, title TEXT, path TEXT UNIQUE); CREATE TABLE IF NOT EXISTS progress(id TEXT PRIMARY KEY, position REAL DEFAULT 0, completed INTEGER DEFAULT 0);')

def natural(value):
    return [int(v) if v.isdigit() else v.lower() for v in re.split(r'(\d+)', value)]

def identifier(value):
    return hashlib.sha256(str(value).encode()).hexdigest()[:24]

def import_course(path, title=None):
    folder = Path(path).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError('Essa pasta não existe neste computador.')
    if not any(p.suffix.lower() in VIDEO for p in folder.rglob('*') if p.is_file()):
        raise ValueError('Nenhum vídeo encontrado na pasta selecionada.')
    cid = identifier(folder)
    with db() as con:
        con.execute('INSERT INTO courses VALUES(?,?,?) ON CONFLICT(path) DO UPDATE SET title=excluded.title', (cid, title or folder.name, str(folder)))
    return cid

def catalog():
    with db() as con:
        rows = con.execute('SELECT * FROM courses ORDER BY rowid').fetchall()
        progress = {r['id']: dict(r) for r in con.execute('SELECT * FROM progress')}
    result = []
    for r in rows:
        folder = Path(r['path'])
        lessons, materials = [], []
        for p in sorted(folder.rglob('*'), key=lambda p: natural(str(p.relative_to(folder)))):
            if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(folder):
                continue
            ext = p.suffix.lower()
            if ext not in VIDEO | MATERIAL:
                continue
            fid = identifier(p)
            item = dict(id=fid, title=p.stem, name=p.name, module=str(p.parent.relative_to(folder)) if p.parent != folder else 'Aulas', ext=ext, url='/files/'+r['id']+'/'+quote(str(p.relative_to(folder))), size=p.stat().st_size)
            if ext in VIDEO:
                item.update(progress.get(fid, dict(position=0, completed=0)))
                lessons.append(item)
            else:
                materials.append(item)
        result.append(dict(id=r['id'],title=r['title'],lessons=lessons,materials=materials,available=folder.exists()))
    return result

class Handler(BaseHTTPRequestHandler):
    def send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        from urllib.parse import unquote
        path = urlparse(self.path).path
        if path == '/api/courses':
            return self.send_json(catalog())
        if path.startswith('/files/'):
            parts = path.split('/',3)
            with db() as con:
                row = con.execute('SELECT path FROM courses WHERE id=?',(parts[2],)).fetchone()
            if not row: return self.send_error(404)
            base = Path(row['path']).resolve()
            target = (base / unquote(parts[3])).resolve()
            if not target.is_relative_to(base) or not target.is_file(): return self.send_error(404)
        else:
            target = (ROOT / 'web' / ('index.html' if path=='/' else path.lstrip('/'))).resolve()
            if not target.is_relative_to(ROOT/'web') or not target.is_file(): return self.send_error(404)
        size = target.stat().st_size
        start, end = 0, size-1
        value = self.headers.get('Range')
        if value:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', value)
            if not match or not any(match.groups()): return self.send_error(416)
            a,b = match.groups()
            if a: start=int(a); end=min(int(b),end) if b else end
            else: start=max(0,size-int(b))
            if start>end or start>=size: return self.send_error(416)
        self.send_response(206 if value else 200)
        self.send_header('Content-Type',mimetypes.guess_type(target.name)[0] or 'application/octet-stream')
        self.send_header('Accept-Ranges','bytes')
        if path.startswith('/files/') and parse_qs(urlparse(self.path).query).get('download') == ['1']:
            self.send_header('Content-Disposition', "attachment; filename*=UTF-8''" + quote(target.name))
        self.send_header('Content-Length',str(end-start+1))
        self.send_header('X-Content-Type-Options','nosniff')
        if value: self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        try:
            with target.open('rb') as f:
                f.seek(start); remaining=end-start+1
                while remaining>0:
                    chunk=f.read(min(1024*1024,remaining))
                    if not chunk: break
                    self.wfile.write(chunk); remaining-=len(chunk)
        except (BrokenPipeError,ConnectionResetError): pass

    def do_POST(self):
        if self.headers.get('Origin') and self.headers['Origin'] != 'http://'+self.headers.get('Host',''):
            return self.send_json({'error':'Origem não permitida.'},403)
        try:
            length=int(self.headers.get('Content-Length',0))
            if length>16*1024*1024: raise ValueError('Arquivo muito grande para esta operação.')
            data=json.loads(self.rfile.read(length))
            if self.path=='/api/import':
                return self.send_json({'id':import_course(data['path'],data.get('title'))})
            if self.path=='/api/upload':
                # Um arquivo por requisição, sem carregar o curso inteiro em memória.
                batch=data['batch']
                if not re.fullmatch('[a-f0-9]{24}',batch): raise ValueError('Importação inválida.')
                base=DATA/'uploads'/batch
                relative=Path(data['name'])
                target=(base/relative).resolve()
                if relative.is_absolute() or not target.is_relative_to(base.resolve()): raise ValueError('Caminho inválido.')
                if target.suffix.lower() not in VIDEO|MATERIAL: raise ValueError('Tipo de arquivo não suportado.')
                chunk=base64.b64decode(data['chunk'],validate=True)
                offset=int(data['offset'])
                target.parent.mkdir(parents=True,exist_ok=True)
                with LOCK:
                    actual=target.stat().st_size if target.exists() else 0
                    if actual!=offset: raise ValueError('Envio fora de ordem. Inicie novamente.')
                    with target.open('ab') as f: f.write(chunk)
                return self.send_json({'ok':True})
            if self.path=='/api/finish':
                if not re.fullmatch('[a-f0-9]{24}',data['batch']): raise ValueError('Importação inválida.')
                return self.send_json({'id':import_course(DATA/'uploads'/data['batch'],data['title'])})
            if self.path=='/api/progress':
                if not any(l['id']==data['id'] for c in catalog() for l in c['lessons']): raise ValueError('Aula inexistente.')
                position=max(0,float(data.get('position',0)))
                if not position<1e9: raise ValueError('Posição inválida.')
                with db() as con:
                    con.execute('INSERT INTO progress VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET position=excluded.position,completed=excluded.completed',(data['id'],position,int(bool(data.get('completed')))))
                return self.send_json({'ok':True})
            self.send_error(404)
        except (ValueError,KeyError,OSError) as e: self.send_json({'error':str(e)},400)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765); args=parser.parse_args()
    print(f'Courses Hub: http://localhost:{args.port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
