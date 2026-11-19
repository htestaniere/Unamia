import sys,pathlib
r=pathlib.Path(__file__).parent;app=(r/'app.src.html').read_text()
lib=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else str(r/'web/supabase.umd.js')).read_text()
be=(r/'web/backend.js').read_text()
i=app.index('\n<script>\n')
out=app[:i]+'\n<script>'+lib+'</script>\n<script>'+be+'</script>'+app[i:]
(r/(sys.argv[2] if len(sys.argv)>2 else 'index.html')).write_text(out);print(len(out))
