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
  .app, .main, .view { height: auto !important; min-height: 100% !important; overflow: visible !important; padding: 20px !important; }
  .view > *:not(#cardOrangeRecovery) { display: none !important; }
  #cardOrangeRecovery { display: block !important; width: 100% !important; max-width: 1500px !important; margin: 0 auto !important; }
  .tw { max-height: 1000px !important; overflow-y: hidden !important; }
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

temp_html = os.path.abspath('temp_orange.html')
with open(temp_html, 'w', encoding='utf-8') as f:
    f.write(html_mod)

chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

out_png = os.path.abspath('temp_orange.png')
cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--hide-scrollbars",
    f"--screenshot={out_png}",
    "--window-size=1600,1800",
    "--virtual-time-budget=3000",
    f"file:///{temp_html.replace(os.sep, '/')}"
]

print("1. Capturing orange screenshot...")
subprocess.run(cmd, check=True)
print("Screenshot captured!")

ps_script = f"""
Add-Type -AssemblyName System.Drawing
$inPath = '{out_png}'
$outPath1 = Join-Path (Get-Location) 'summary_lock_row.jpg'
$outPath2 = 'C:\\Users\\ASUS\\.gemini\\antigravity\\brain\\cb6d8573-7d38-4cde-bf05-95f4860c1cf3\\summary_lock_row.jpg'

$img = [System.Drawing.Image]::FromFile($inPath)
$codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object {{ $_.FormatDescription -eq "JPEG" }}
$encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
$encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, 92L)

$img.Save($outPath1, $codec, $encoderParams)
$img.Save($outPath2, $codec, $encoderParams)
$img.Dispose()
Write-Host "Success writing summary_lock_row.jpg!"
"""

with open('convert_orange.ps1', 'w', encoding='utf-8') as f:
    f.write(ps_script)

print("2. Converting to JPG...")
subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "convert_orange.ps1"], check=True)

# Also run render_split.py to update full page render
if os.path.exists('render_split.py'):
    subprocess.run(["python", "render_split.py"], check=True)

# Cleanup
for f in [temp_html, out_png, 'convert_orange.ps1']:
    if os.path.exists(f):
        try: os.remove(f)
        except: pass

print("Render complete!")
