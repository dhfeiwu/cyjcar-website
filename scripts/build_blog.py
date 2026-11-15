from pathlib import Path
from datetime import date, datetime
import html, re, yaml, markdown
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
BASE='https://cyjcar.com/'
MARKER_START='<!-- CMS-POSTS-START -->'
MARKER_END='<!-- CMS-POSTS-END -->'
POSTS=ROOT/'content/posts'

def parse_post(path):
    raw=path.read_text(encoding='utf-8')
    m=re.match(r'\A---\s*\n(.*?)\n---\s*\n(.*)\Z',raw,re.S)
    if not m: raise ValueError(f'Missing YAML frontmatter: {path}')
    data=yaml.safe_load(m.group(1)) or {}
    data['body']=m.group(2)
    data['slug']=path.stem
    for field in ('title','description','date'):
        if not data.get(field):raise ValueError(f'Missing {field}: {path}')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',data['slug']):raise ValueError(f'Invalid filename: {path.name}')
    return data

def e(s):return html.escape(str(s),quote=True)
def date_str(v):return v.isoformat() if isinstance(v,(date,datetime)) else str(v)
def local_img(v):
    v=str(v or '').strip()
    if not v:return ''
    if v.startswith('/'):v=v[1:]
    if v.startswith('https://cyjcar.com/'):v=v[len('https://cyjcar.com/'):]
    if not v.startswith('assets/images/blog/') or '..' in v.split('/'):
        raise ValueError('Cover must be uploaded under assets/images/blog/: '+v)
    return v

blog_path=ROOT/'blog.html'
blog=blog_path.read_text(encoding='utf-8')
if MARKER_START not in blog or MARKER_END not in blog:raise RuntimeError('CMS markers missing in blog.html')
posts=sorted((parse_post(p) for p in POSTS.glob('*.md')),key=lambda x:date_str(x['date']),reverse=True)
header=(ROOT/'toyota-auto-parts-shipping-iraq.html').read_text(encoding='utf-8')
nav=re.search(r'<div class="topbar">.*?</header>',header,re.S).group(0)
footer=re.search(r'<a aria-label="Chat on WhatsApp".*?</html>',blog,re.S).group(0)
style="<style>.cms-article{background:#fff;padding:52px 0 78px;color:#172235}.cms-article .container{max-width:900px}.cms-article h1{font-size:clamp(30px,4vw,46px);line-height:1.18;margin:16px 0}.cms-article .lead{font-size:18px;color:#536175;line-height:1.7}.cms-body{font-size:17px;line-height:1.85}.cms-body h2{font-size:27px;margin:32px 0 12px}.cms-body img{max-width:100%;height:auto;border-radius:12px}.cms-body a{color:#c51e2e}.cms-cover{width:100%;max-height:460px;object-fit:cover;border-radius:14px;margin:20px 0}.cms-date{color:#667085;font-size:14px}</style>"
cards=[]
for p in posts:
    slug=p['slug'];title=e(p['title']);desc=e(p['description']);cat=e(p.get('category') or 'BLOG');cover=local_img(p.get('cover'))
    url=slug+'.html'; body=markdown.markdown(p['body'],extensions=['extra','sane_lists'])
    cover_tag=f'<img class="cms-cover" src="{e(cover)}" alt="{title}" loading="eager">' if cover else ''
    doc=f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | CYJCAR</title><meta name="description" content="{desc}"><link rel="canonical" href="{BASE}{url}"><meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><link rel="stylesheet" href="style.css">{style}</head><body>{nav}<main class="cms-article"><div class="container"><p><a href="blog.html">← Back to Blog</a></p><span class="eyebrow">{cat}</span><h1>{title}</h1><p class="cms-date">{e(date_str(p['date']))}</p><p class="lead">{desc}</p>{cover_tag}<div class="cms-body">{body}</div><p style="margin-top:36px"><a href="index.html#contact">Request a Quote →</a></p></div></main>{footer}"""
    (ROOT/url).write_text(doc,encoding='utf-8')
    thumb=f'<img src="{e(cover)}" alt="{title}" loading="lazy" style="width:100%;height:225px;object-fit:cover;display:block">' if cover else '<div style="height:225px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#172235,#3a4d62);color:white;padding:20px;text-align:center;font-size:24px;font-weight:700">CYJCAR · AUTO PARTS GUIDES</div>'
    cards.append(f'<article class="blog-card"><a href="{url}" aria-label="Read {title}">{thumb}</a><div class="blog-card-body"><span class="blog-tag">{cat}</span><h3><a href="{url}" style="color:inherit;text-decoration:none">{title}</a></h3><p>{desc}</p><a class="blog-link" href="{url}">Read Article →</a></div></article>')
blog=blog[:blog.index(MARKER_START)+len(MARKER_START)]+'\n'+''.join(cards)+'\n'+blog[blog.index(MARKER_END):]
blog_path.write_text(blog,encoding='utf-8')

sitemap=ROOT/'sitemap.xml'
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
tree=ET.parse(sitemap); node=tree.getroot()
existing={x.text for x in node.findall(f'{ns}url/{ns}loc')}
for p in posts:
    url=BASE+p['slug']+'.html'
    if url not in existing:ET.SubElement(ET.SubElement(node,ns+'url'),ns+'loc').text=url
if BASE+'blog.html' not in existing:ET.SubElement(ET.SubElement(node,ns+'url'),ns+'loc').text=BASE+'blog.html'
tree.write(sitemap,encoding='utf-8',xml_declaration=True)
print(f'Generated {len(posts)} CMS articles')
