"""
ScamShield - simulated Alexa+ web experience.
Voice-style web page that calls your real MCP server and reads back the verdict,
now showing which detection layer caught the scam.
Run order: python server.py  ->  python webapp.py  ->  http://127.0.0.1:8282
"""
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession

MCP_URL = "http://127.0.0.1:8181/mcp"
app = FastAPI()


async def call_scamshield(message: str) -> dict:
    async with streamable_http_client(MCP_URL) as streams:
        read, write = streams[0], streams[1]
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("check_scam", {"message": message})
            return json.loads(result.content[0].text)


@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    try:
        return JSONResponse(await call_scamshield(data.get("message", "")))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE


HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>ScamShield - Alexa+ Simulator</title>
<style>
  :root { --bg:#0a0e17; --card:#141a28; --line:#263249; --text:#e8eef9; --muted:#8aa0c0;
          --cyan:#28c7fa; --danger:#ff4d5e; --warn:#ffb020; --safe:#2ecc71; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--text);
         font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
         min-height:100vh; display:flex; flex-direction:column; align-items:center; padding:32px 16px; }
  h1 { font-size:26px; margin:18px 0 2px; letter-spacing:.5px; }
  .sub { color:var(--muted); font-size:14px; margin-bottom:10px; text-align:center; }
  .orb { width:120px; height:120px; border-radius:50%;
         background:conic-gradient(from 0deg,#28c7fa,#6a5cff,#28c7fa);
         filter:blur(2px); opacity:.85; animation:spin 6s linear infinite; box-shadow:0 0 50px #28c7fa66; }
  .orb.think { animation:spin 1.1s linear infinite; box-shadow:0 0 70px #28c7faaa; }
  @keyframes spin { to { transform:rotate(360deg); } }
  .status { height:18px; color:var(--cyan); font-size:13px; margin:8px 0 0; }
  .panel { width:100%; max-width:620px; }
  .row { display:flex; gap:10px; margin-top:22px; }
  textarea { flex:1; background:var(--card); border:1px solid var(--line); color:var(--text);
             border-radius:14px; padding:14px; font-size:15px; resize:none; min-height:58px; }
  button { border:0; border-radius:14px; padding:0 18px; font-size:15px; font-weight:600; cursor:pointer; }
  .ask { background:var(--cyan); color:#001018; }
  .mic { background:var(--card); color:var(--text); border:1px solid var(--line); font-size:20px; }
  .card { margin-top:22px; background:var(--card); border:1px solid var(--line); border-radius:16px; padding:20px; display:none; }
  .level { font-size:22px; font-weight:800; letter-spacing:.5px; }
  .advice { margin:12px 0; line-height:1.5; }
  .signs { margin:0; padding-left:18px; color:var(--muted); font-size:14px; }
  .pill { display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:700; margin-bottom:10px; }
  .layers { margin-top:14px; display:flex; flex-wrap:wrap; gap:6px; }
  .chip { font-size:11px; background:#28c7fa18; color:var(--cyan); border:1px solid #28c7fa44;
          padding:3px 9px; border-radius:999px; }
  .DANGEROUS { color:var(--danger); } .DANGEROUS .pill { background:#ff4d5e22; color:var(--danger); }
  .SUSPICIOUS { color:var(--warn); } .SUSPICIOUS .pill { background:#ffb02022; color:var(--warn); }
  .SAFE { color:var(--safe); } .SAFE .pill { background:#2ecc7122; color:var(--safe); }
  .hint { color:var(--muted); font-size:12px; margin-top:14px; text-align:center; }
</style>
</head>
<body>
  <div class="orb" id="orb"></div>
  <div class="status" id="status"></div>
  <h1>ScamShield</h1>
  <div class="sub">Ask me if a message is a scam. Powered by your MCP server.</div>
  <div class="panel">
    <div class="row">
      <textarea id="msg" placeholder="Paste a suspicious text, email, or message..."></textarea>
      <button class="mic" id="mic" title="Speak">&#127908;</button>
      <button class="ask" id="ask">Ask</button>
    </div>
    <div class="card" id="card">
      <span class="pill" id="pill"></span>
      <div class="level" id="level"></div>
      <div class="advice" id="advice"></div>
      <ul class="signs" id="signs"></ul>
      <div class="layers" id="layers"></div>
    </div>
    <div class="hint">Try: "URGENT: your account is blocked, verify your OTP now to reactivate."</div>
  </div>
<script>
  const orb=document.getElementById('orb'), card=document.getElementById('card'), status=document.getElementById('status');
  function speak(t){ try{ const u=new SpeechSynthesisUtterance(t); u.rate=1; speechSynthesis.cancel(); speechSynthesis.speak(u);}catch(e){} }

  async function ask(){
    const msg=document.getElementById('msg').value.trim();
    if(!msg) return;
    orb.classList.add('think'); card.style.display='none'; status.textContent='ScamShield is analyzing...';
    try{
      const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
      const d=await r.json();
      orb.classList.remove('think'); status.textContent='';
      if(d.error){ alert('Could not reach the server. Is server.py running?\\n'+d.error); return; }
      const lvl=d.risk_level||'SAFE';
      card.className='card '+lvl; card.style.display='block';
      document.getElementById('pill').textContent='ScamShield says';
      document.getElementById('level').textContent=lvl;
      document.getElementById('advice').textContent=d.advice||'';
      const ul=document.getElementById('signs'); ul.innerHTML='';
      (d.warning_signs||[]).forEach(s=>{const li=document.createElement('li');li.textContent=s;ul.appendChild(li);});
      const ly=document.getElementById('layers'); ly.innerHTML='';
      (d.caught_by||[]).forEach(s=>{const c=document.createElement('span');c.className='chip';c.textContent='caught by: '+s;ly.appendChild(c);});
      speak(lvl+'. '+(d.advice||''));
    }catch(e){ orb.classList.remove('think'); status.textContent=''; alert('Error: '+e); }
  }
  document.getElementById('ask').onclick=ask;

  const mic=document.getElementById('mic');
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(SR){ const rec=new SR(); rec.lang='en-US';
    mic.onclick=()=>{ orb.classList.add('think'); status.textContent='Listening...'; rec.start(); };
    rec.onresult=e=>{ document.getElementById('msg').value=e.results[0][0].transcript; orb.classList.remove('think'); status.textContent=''; ask(); };
    rec.onerror=()=>{ orb.classList.remove('think'); status.textContent=''; };
  } else { mic.style.display='none'; }
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    print("ScamShield web app on http://127.0.0.1:8282  (make sure server.py is running)")
    uvicorn.run(app, host="127.0.0.1", port=8282)