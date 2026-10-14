import base64,json,sys,tempfile,threading,unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server

class HubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(); server.DATA=Path(cls.tmp.name)
        with server.db() as c:
            c.executescript('CREATE TABLE courses(id TEXT PRIMARY KEY,title TEXT,path TEXT UNIQUE); CREATE TABLE progress(id TEXT PRIMARY KEY,position REAL DEFAULT 0,completed INTEGER DEFAULT 0);')
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.url='http://127.0.0.1:'+str(cls.http.server_port)
        threading.Thread(target=cls.http.serve_forever,daemon=True).start()
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.tmp.cleanup()
    def post(self,path,data):
        return json.load(urlopen(Request(self.url+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})))
    def test_upload_import_range_and_progress(self):
        batch='a'*24
        for name,data in [('Module/2.mp4',b'video2'),('Module/10.mp4',b'video10'),('Module/example.py',b'print(1)')]:
            self.post('/api/upload',dict(batch=batch,name=name,offset=0,chunk=base64.b64encode(data).decode()))
        self.post('/api/finish',dict(batch=batch,title='Course test'))
        c=json.load(urlopen(self.url+'/api/courses'))[0]
        self.assertEqual([l['name'] for l in c['lessons']],['2.mp4','10.mp4'])
        self.assertEqual(len(c['materials']),1)
        l=c['lessons'][0]
        self.post('/api/progress',dict(id=l['id'],position=12.5,completed=True))
        l=json.load(urlopen(self.url+'/api/courses'))[0]['lessons'][0]
        self.assertEqual(l['position'],12.5);self.assertEqual(l['completed'],1)
        r=urlopen(Request(self.url+l['url'],headers={'Range':'bytes=1-3'}))
        self.assertEqual(r.status,206);self.assertEqual(r.read(),b'ide')
        r=urlopen(Request(self.url+l['url'],headers={'Range':'bytes=-2'}))
        self.assertEqual(r.read(),b'o2')
    def test_upload_traversal_and_offset_rejected(self):
        for name,offset in [('../escape.py',0),('/tmp/escape.py',0),('x.py',99)]:
            with self.assertRaises(HTTPError) as err:
                self.post('/api/upload',dict(batch='b'*24,name=name,offset=offset,chunk='YQ=='))
            self.assertEqual(err.exception.code,400);err.exception.close()
    def test_nonexistent_folder_rejected(self):
        with self.assertRaises(HTTPError) as err:self.post('/api/import',dict(path='/nonexistent/course'))
        self.assertEqual(err.exception.code,400);err.exception.close()

if __name__=='__main__':unittest.main()
