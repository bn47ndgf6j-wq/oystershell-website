#!/usr/bin/env python3
"""Build the static Oystershell site.

src/site.html is the single-file design source (also used for the preview).
This script splits it into one real page per section, adds SEO and AI-search
markup, and writes everything Cloudflare Pages serves into public/.
Run: python3 build.py
"""
import json, re, shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = (ROOT / 'src/site.html').read_text()
OUT = ROOT / 'public'
SITE = 'https://www.oystershell.co.uk'
DRAFT = True  # set False at launch: removes the draft banner

PAGES = {
  'home': dict(path='/', title='Oystershell | Hospitality sales consulting, contactless payments and battery power',
    desc='Oystershell is a UK commercial and sales consultancy for hospitality technology: contactless payment installs with Kashing, certified lithium battery packs, refurbished jukeboxes and management advice.'),
  'contactless': dict(path='/contactless/', title='Contactless payments for pool tables, jukeboxes and vending | Oystershell',
    desc='Card and contactless payment readers for coin-operated machines: pool tables, jukeboxes, vending, laundrettes, kids rides, EV charging and parking. Delivered with Kashing.'),
  'batteries': dict(path='/batteries/', title='14.8V 40Ah lithium battery packs, UN38.3 certified | Oystershell',
    desc='Certified 592 Wh lithium-ion battery packs for machines with no mains socket: pool tables, kiosks and payment terminals. Smart SMBus fuel gauge, UN38.3 tested, shipped as dangerous goods.'),
  'jukeboxes': dict(path='/jukeboxes/', title='Refurbished digital jukeboxes and venue background music | Oystershell',
    desc='Ex-venue digital jukeboxes refurbished for home bars and games rooms, trade batches for operators, and over forty years of background music and sound system experience.'),
  'advice': dict(path='/advice/', title='Hospitality management advice and product development | Oystershell',
    desc='Commercial strategy, interim sales and marketing leadership, route to market and product development for technology, music and payments companies selling into UK hospitality.'),
  'about': dict(path='/about/', title='About Oystershell | UK hospitality technology consultancy since 1999',
    desc='Oystershell Limited was founded in 1999 in Northampton. Its experience in UK hospitality sales, music and payments goes back to 1982.'),
  'experience': dict(path='/experience/', title='Experience | Oystershell',
    desc='Forty years of UK hospitality technology: cashless payments, digital jukeboxes, background music, board leadership and field sales.'),
  'reviews': dict(path='/reviews/', title='Client reviews | Oystershell',
    desc='What clients say about working with Oystershell.', noindex=True),
  'contact': dict(path='/contact/', title='Contact Oystershell | Book a call',
    desc='Talk to Oystershell about contactless installs, battery packs, jukeboxes or commercial advice. Email james@oystershell.co.uk.'),
  'privacy': dict(path='/privacy/', title='Privacy policy | Oystershell', desc='How Oystershell Limited collects and uses personal information.'),
  'terms': dict(path='/terms/', title='Terms of use | Oystershell', desc='Terms of use for the Oystershell Limited website.'),
}

FAQ = {
  'home': [
    ('What does Oystershell do?', 'Oystershell is a UK commercial and sales consultancy for hospitality technology. It leads sales and marketing for Kashing, supplies certified lithium battery packs, sells refurbished digital jukeboxes, and advises companies selling into pubs, bars and leisure venues.'),
    ('Where is Oystershell based?', 'Oystershell Limited is based in Northampton and works across the UK. It is registered in England and Wales, company number 03856081.'),
    ('Who does Oystershell work with?', 'Technology, music and payments companies, machine operators and venue owners in UK hospitality, leisure and unattended retail.'),
  ],
  'contactless': [
    ('Can a pool table take contactless payments?', 'Yes. A contactless card reader can be fitted to a coin-operated pool table so players pay by card, phone or watch. Where there is no socket nearby, a battery pack powers the reader.'),
    ('Which machines can take card payments?', 'Pool tables, jukeboxes, vending machines, laundrette washers and dryers, kids rides, EV chargers and parking or forecourt machines.'),
    ('Who provides the payment service?', 'Payments are processed by Kashing Limited, which is authorised and regulated by the Financial Conduct Authority as a Small Payment Institution.'),
  ],
  'batteries': [
    ('Who supplies UN38.3 certified battery packs for coin-op machines in the UK?', 'Oystershell supplies smart lithium-ion battery packs, UN38.3 tested, for pool tables, kiosks, payment terminals and other machines that need to run without mains power.'),
    ('What are the battery pack specifications?', '14.8 V nominal, 40 Ah typical capacity (592 Wh), 32 x 21700 cells in a 4S8P layout, 5 A maximum charge and discharge, 179 x 155 x 47 mm, about 2.4 kg, with an SMBus fuel gauge.'),
    ('Can you make a pack to my specification?', 'Yes. Packs can be built to your voltage, capacity, size and connector needs, with test reports for each design.'),
  ],
  'jukeboxes': [
    ('Where can I buy a refurbished digital jukebox for my home?', 'Oystershell sells ex-pub digital jukeboxes, refurbished for home bars, games rooms and man caves. Current stock is listed on eBay and Facebook Marketplace.'),
    ('Do you buy used jukeboxes?', 'Yes. Oystershell buys surplus digital jukeboxes from operators and venues, in single units or in quantity.'),
    ('Can you advise on background music for a venue?', 'Yes. Oystershell has over forty years of experience in commercial background music, jukeboxes and sound installation for UK hospitality.'),
  ],
  'advice': [
    ('How can a technology company sell into UK pubs?', 'Start with a clear proposition for operators and pub companies, the right commercial model, and introductions to the people who decide. Oystershell provides all three, from strategy to signed contract.'),
    ('Do you offer interim sales and marketing leadership?', 'Yes. Oystershell can act as the name and face of your sales function on a rolling contract, without a full-time hire.'),
    ('Do you help with product development?', 'Yes, from customer-side input to research and development, through hardware specification and certification, to venue pilots and launch.'),
  ],
}

def org_ld():
  return {
    '@type': ['Organization', 'LocalBusiness'], '@id': SITE + '/#org',
    'name': 'Oystershell Limited', 'alternateName': 'Oystershell', 'url': SITE + '/',
    'logo': SITE + '/logo-horizontal-960@2x.png', 'image': SITE + '/og-image-1200x630.png',
    'email': 'james@oystershell.co.uk', 'foundingDate': '1999-10-08', 'founder': {'@type': 'Person', 'name': 'James Luck'},
    'identifier': {'@type': 'PropertyValue', 'propertyID': 'Companies House', 'value': '03856081'},
    'address': {'@type': 'PostalAddress', 'streetAddress': '3 Neale Close, Weston Favell', 'addressLocality': 'Northampton', 'postalCode': 'NN3 3DB', 'addressCountry': 'GB'},
    'areaServed': 'GB',
    'sameAs': ['https://www.linkedin.com/in/jamesluckoystershell/', 'https://www.ebay.co.uk/usr/oystershelllimited'],
    'knowsAbout': ['Hospitality sales', 'Contactless payments', 'Unattended payments', 'Lithium battery packs', 'Digital jukeboxes', 'Background music', 'Product development'],
  }

def page_ld(name, meta):
  graph = [org_ld(), {'@type': 'WebPage', 'url': SITE + meta['path'], 'name': meta['title'], 'description': meta['desc'], 'isPartOf': {'@id': SITE + '/#org'}, 'inLanguage': 'en-GB'}]
  if name == 'batteries':
    graph.append({'@type': 'Product', 'name': 'Oystershell 14.8 V 40 Ah smart lithium battery pack', 'brand': {'@id': SITE + '/#org'},
      'description': '592 Wh lithium-ion pack, 32 x 21700 cells (4S8P), SMBus fuel gauge, UN38.3 tested.',
      'additionalProperty': [{'@type': 'PropertyValue', 'name': n, 'value': v} for n, v in [
        ('Nominal voltage', '14.8 V'), ('Capacity', '40 Ah'), ('Energy', '592 Wh'), ('Weight', '2.4 kg'), ('Dimensions', '179 x 155 x 47 mm'), ('Certification', 'UN38.3')]]})
  services = {'contactless': 'Contactless payment installation for coin-operated machines',
              'advice': 'Hospitality management advice and product development',
              'jukeboxes': 'Refurbished digital jukeboxes and background music advice'}
  if name in services:
    graph.append({'@type': 'Service', 'name': services[name], 'provider': {'@id': SITE + '/#org'}, 'areaServed': 'GB'})
  if name in FAQ:
    graph.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ[name]]})
  if name != 'home':
    graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
      {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
      {'@type': 'ListItem', 'position': 2, 'name': meta['title'].split(' | ')[0], 'item': SITE + meta['path']}]})
  return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=1)

def faq_html(name):
  if name not in FAQ: return ''
  items = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ[name])
  return f'\n  <section class="faq"><div class="wrap narrow"><p class="eyebrow">Questions</p><h2 class="h2">Good to know.</h2><div class="faq-list">{items}</div></div></section>\n'

# --- split the source ---
style = re.search(r'<style>.*?</style>', SRC, re.S).group(0)
style = style.replace('</style>', '''
.faq{background:var(--off)}
.faq-list{margin-top:32px;border-top:1px solid var(--rule)}
.faq details{border-bottom:1px solid var(--rule);padding-block:20px}
.faq summary{font-size:19px;font-weight:600;cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq summary::after{content:"+";color:var(--blue);font-weight:400;font-size:24px;line-height:1}
.faq details[open] summary::after{content:"\\2212"}
.faq details p{color:var(--muted-ink);margin-top:12px;max-width:62ch}
.page{display:block}
.h1-kicker{display:block;font-size:14px;line-height:1.4;letter-spacing:.08em;margin-bottom:14px}
.hero .hero-name.h1-kicker{font-size:clamp(20px,2.6vw,28px);letter-spacing:.1em;margin-bottom:18px}
</style>''')
nav = re.search(r'<nav.*?</nav>', SRC, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', SRC, re.S).group(0)
draft = re.search(r'<div class="draft">.*?</div></div>', SRC, re.S).group(0)
main = re.search(r'<main>(.*)</main>', SRC, re.S).group(1)
blocks = {}
for m in re.finditer(r'<div class="page" data-page="([a-z-]+)">(.*?)\n</div>\n(?=\s*(?:<!--|$))', main + '\n', re.S):
  blocks[m.group(1)] = m.group(2)
missing = set(PAGES) - set(blocks)
assert not missing, missing
script = '''<script>
(function(){
  var menu=document.getElementById('menu'), btn=document.getElementById('menu-btn');
  btn.addEventListener('click',function(){var o=menu.classList.toggle('open');btn.setAttribute('aria-expanded',o?'true':'false');});
  [].forEach.call(document.querySelectorAll('.slot[data-src]'),function(f){
    var img=new Image(); img.alt=f.dataset.alt||''; img.loading='lazy'; img.decoding='async';
    img.onload=function(){f.innerHTML='';f.appendChild(img);};
    img.src=f.dataset.src;
  });
  var form=document.getElementById('contact-form');
  if(form){var note=document.getElementById('form-note');form.addEventListener('submit',function(e){
    if(!form.checkValidity()){e.preventDefault();note.textContent='Please fill in your name, email and message, and tick the consent box.';}
  });}
})();
</script>'''

def fix_links(html):
  def rep(m):
    target = m.group(1)
    if target == 'sound-link': return 'href="/jukeboxes/#sound"'
    if target in PAGES: return f'href="{PAGES[target]["path"]}"'
    return m.group(0)
  html = re.sub(r'href="#([a-z-]+)"', rep, html)
  html = html.replace('data-src="images/', 'data-src="/images/')
  return html

def head(name, meta):
  robots = '<meta name="robots" content="noindex, follow">' if meta.get('noindex') else '<meta name="robots" content="index, follow, max-image-preview:large">'
  url = SITE + meta['path']
  return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{meta['title']}</title>
<meta name="description" content="{meta['desc']}">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Oystershell">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{meta['title']}">
<meta property="og:description" content="{meta['desc']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image-1200x630.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#000000">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon-180.png">
<link rel="manifest" href="/site.webmanifest">
<script type="application/ld+json">
{page_ld(name, meta)}
</script>
{style}
</head>'''

if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
for name, meta in PAGES.items():
  body = blocks[name]
  # the contact form posts to Formspree, which emails james@oystershell.co.uk
  body = body.replace('<form id="contact-form" novalidate>', '<form id="contact-form" action="https://formspree.io/f/xwlljvzl" method="POST"><input type="hidden" name="_subject" value="New enquiry from oystershell.co.uk">')
  body = body.replace('<input id="f-name" name="name"', '<input id="f-name" name="name"').replace('<input id="f-consent" type="checkbox" required>', '<input id="f-consent" name="consent" type="checkbox" required>')
  body = re.sub(r'<p class="form-note" id="form-note" role="status"></p>', '<p class="form-note" id="form-note" role="status"></p>', body)
  # each page's first visible heading is its h1; demote nothing else
  if name in ('privacy', 'terms'):
    body = re.sub(r'<h2>(Privacy policy|Terms of use)</h2>', r'<h1 class="h2">\1</h1>', body)
  body = re.sub(r'<p class="(eyebrow grad[^"]*)">(.*?)</p>\s*<h1 class="h1"([^>]*)>', r'<h1 class="h1"\3><span class="\1 h1-kicker">\2</span> ', body, count=1)
  navp = fix_links(nav).replace(f'href="{meta["path"]}"', f'href="{meta["path"]}" aria-current="page"', 1) if name != 'home' else fix_links(nav)
  html = head(name, meta) + '\n<body>\n' + (draft + '\n' if DRAFT else '') + navp + '\n<main>\n' + fix_links(body) + faq_html(name) + '\n</main>\n' + fix_links(footer) + '\n' + script + '\n</body>\n</html>\n'
  dest = OUT / meta['path'].strip('/') / 'index.html' if name != 'home' else OUT / 'index.html'
  dest.parent.mkdir(parents=True, exist_ok=True)
  dest.write_text(html)

# 404
nf = head('home', dict(path='/404', title='Page not found | Oystershell', desc='This page does not exist.', noindex=True)).replace(f'<link rel="canonical" href="{SITE}/404">', '')
(OUT / '404.html').write_text(nf + '\n<body>\n' + fix_links(nav) + '<main><header class="hero dark"><div class="wrap"><h1 class="h1">Page not found.</h1><p class="lede">The page you were looking for has moved or never existed.</p><div class="links"><a class="btn" href="/">Go to the homepage</a></div></div></header></main>' + fix_links(footer) + script + '</body></html>\n')

# brand assets
B = ROOT / 'assets'
for f in B.glob('*'):
  if f.is_file(): shutil.copy(f, OUT / f.name)
if (ROOT / 'images').exists(): shutil.copytree(ROOT / 'images', OUT / 'images', ignore=shutil.ignore_patterns('*.md'))

# sitemap, robots, llms.txt, headers
urls = ''.join(f'<url><loc>{SITE}{m["path"]}</loc><changefreq>monthly</changefreq><priority>{"1.0" if n == "home" else "0.8" if n in FAQ else "0.4"}</priority></url>' for n, m in PAGES.items() if not m.get('noindex'))
(OUT / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
(OUT / 'robots.txt').write_text('''# Search engines and AI assistants are welcome.
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: Bingbot
Allow: /

Sitemap: https://www.oystershell.co.uk/sitemap.xml
''')
llms = ['# Oystershell Limited', '', '> UK commercial and sales consultancy for hospitality technology, based in Northampton. Founded 1999. Company number 03856081 (England and Wales). Contact: james@oystershell.co.uk.', '',
  'Oystershell leads sales and marketing for Kashing, a UK unattended contactless payments provider, and has over forty years of experience selling technology, music and payment systems to most of the larger hospitality retailers in the UK.', '', '## Services', '']
for n in ['contactless', 'batteries', 'jukeboxes', 'advice']:
  llms.append(f'- [{PAGES[n]["title"].split(" | ")[0]}]({SITE}{PAGES[n]["path"]}): {PAGES[n]["desc"]}')
llms += ['', '## Company', '', f'- [About]({SITE}/about/): {PAGES["about"]["desc"]}', f'- [Experience]({SITE}/experience/): {PAGES["experience"]["desc"]}', f'- [Contact]({SITE}/contact/): {PAGES["contact"]["desc"]}', '', '## Frequently asked questions', '']
for n, qa in FAQ.items():
  for q, a in qa: llms += [f'### {q}', a, '']
(OUT / 'llms.txt').write_text('\n'.join(llms))
(OUT / '_headers').write_text('''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/images/*
  Cache-Control: public, max-age=2592000

/*.png
  Cache-Control: public, max-age=2592000
''')
(OUT / '_redirects').write_text('/services /advice/ 301\n/services/ /advice/ 301\n/track-record /experience/ 301\n/power /batteries/ 301\n')
print('built', len(PAGES), 'pages into', OUT)
