import os
import subprocess

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_mod = html.replace('let db=null,downloads=null,room=null,view="tahunan",estMonth=10', 
                        'let db=null,downloads=null,room=null,view="est",estMonth=10')
html_mod = html_mod.replace('view="tahunan"', 'view="est"')

inject_head = """
<style>
  #lockScreen { display: none !important; }
  .app { filter: none !important; pointer-events: auto !important; opacity: 1 !important; }
  html, body { height: auto !important; min-height: 100% !important; overflow: visible !important; background: #0c0f14 !important; }
  .app, .main, .view { height: auto !important; min-height: 100% !important; overflow: visible !important; }
  .tw { max-height: 800px !important; overflow-y: hidden !important; }
</style>
<script>
  window.addEventListener('DOMContentLoaded', () => {
    try {
      if (typeof unlockDashboard === 'function') unlockDashboard();
      view = 'est';
      estMonth = 10;
      if (typeof render === 'function') render();
    } catch(e) {}
  });
</script>
"""
html_mod = html_mod.replace('</head>', inject_head + '</head>')

inject_body = """
<script>
  try {
    sessionStorage.setItem('foxe_auth', 'unlocked');
    localStorage.setItem('foxe_auth_token', 'token_ok');
  } catch(e){}
  setTimeout(() => {
    view = 'est';
    estMonth = 10;
    if (typeof render === 'function') render();
  }, 100);
</script>
"""
html_mod = html_mod.replace('</body>', inject_body + '</body>')

temp_html = os.path.abspath('temp_render.html')
with open(temp_html, 'w', encoding='utf-8') as f:
    f.write(html_mod)

chrome_path = r"C:\Users\ASUS\AppData\Local\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

out_png = os.path.abspath('temp_render.png')
cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--hide-scrollbars",
    f"--screenshot={out_png}",
    "--window-size=1600,4800",
    "--virtual-time-budget=3000",
    f"file:///{temp_html.replace(os.sep, '/')}"
]

print("1. Capturing screenshot...")
subprocess.run(cmd, check=True)
print("Screenshot captured!")

ps_script = f"""
Add-Type -AssemblyName System.Drawing
$inPath = '{out_png}'
$outPath1 = Join-Path (Get-Location) 'estimate_omzet_split.jpg'
$outPath2 = 'C:\\Users\\ASUS\\.gemini\\antigravity\\brain\\cb6d8573-7d38-4cde-bf05-95f4860c1cf3\\estimate_omzet_split.jpg'

$img = [System.Drawing.Image]::FromFile($inPath)
$codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object {{ $_.FormatDescription -eq "JPEG" }}
$encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
$encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, 92L)

$img.Save($outPath1, $codec, $encoderParams)
$img.Save($outPath2, $codec, $encoderParams)
$img.Dispose()
Write-Host "Success writing estimate_omzet_split.jpg!"
"""

with open('convert_script.ps1', 'w', encoding='utf-8') as f:
    f.write(ps_script)

print("2. Converting to JPG...")
subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "convert_script.ps1"], check=True)

# Cleanup
for f in [temp_html, out_png, 'convert_script.ps1']:
    if os.path.exists(f):
        try: os.remove(f)
        except: pass

print("Render complete!")
