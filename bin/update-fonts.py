"""Downloads the Google fonts the theme uses and rewrites the @font-face rules
to point at local files."""
import os
import re
import subprocess

THEME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(THEME, 'assets/fonts')
CSS_OUT = os.path.join(THEME, 'assets/styles/fonts.css')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
URL = ('https://fonts.googleapis.com/css2'
       '?family=Poppins:ital,wght@0,400;0,500;0,600;0,700;1,400'
       '&family=Roboto:ital,wght@0,400;0,500;0,700;1,400'
       '&family=Roboto+Condensed:ital,wght@0,400;0,700;1,400'
       '&display=swap')

# Only the subsets a French or English site renders. The others (cyrillic,
# greek, devanagari, vietnamese) are several files per weight that no page here
# would ever ask for.
KEEP = {'latin', 'latin-ext'}

css = subprocess.run(['curl', '-sS', '-A', UA, URL], capture_output=True, text=True, check=True).stdout

os.makedirs(FONT_DIR, exist_ok=True)

blocks = re.findall(r'/\* (\S+) \*/\s*(@font-face \{.*?\})', css, re.S)
kept = []
downloaded = 0

for subset, block in blocks:
    if subset not in KEEP:
        continue

    family = re.search(r"font-family: '([^']+)'", block).group(1)
    style = re.search(r'font-style: (\w+)', block).group(1)
    weight = re.search(r'font-weight: (\d+)', block).group(1)
    url = re.search(r'src: url\((\S+)\) format', block).group(1)

    name = '%s-%s-%s-%s.woff2' % (
        family.lower().replace(' ', '-'), weight, style, subset,
    )
    target = os.path.join(FONT_DIR, name)

    if not os.path.exists(target):
        subprocess.run(['curl', '-sS', '-A', UA, url, '-o', target], check=True)
        downloaded += 1

    block = block.replace('src: url(%s) format' % url, 'src: url("../fonts/%s") format' % name)
    kept.append(('/* %s %s %s, %s */\n' % (family, weight, style, subset)) + block)

header = """/* Fonts served by the site itself.

   Asking fonts.googleapis.com for them sends the address of every visitor to a
   third party before they have agreed to anything, which a French or German
   court has more than once held to be a breach of the GDPR, and it costs a
   connection to another host on the critical path of the first paint.

   Regenerate with bin/update-fonts.py when the families or the
   weights change. Only the latin and latin-ext subsets are kept. */

"""

with open(CSS_OUT, 'w', encoding='utf-8') as handle:
    handle.write(header + '\n\n'.join(kept) + '\n')

print('%d rules kept, %d files downloaded, %d bytes of fonts'
      % (len(kept), downloaded,
         sum(os.path.getsize(os.path.join(FONT_DIR, f)) for f in os.listdir(FONT_DIR))))
