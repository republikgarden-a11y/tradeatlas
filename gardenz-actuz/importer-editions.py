"""Importer des bulletins HTML dans ce kiosque sans supprimer les archives.

Usage : python3 importer-editions.py /chemin/Gardenz-Actuz-AAAA-MM-JJ.html [...]
Dépendance : lxml. Les images intégrées sont conservées octet pour octet.
"""
from pathlib import Path
import base64
import hashlib
import json
import re
import sys
from lxml import html

ROOT = Path(__file__).resolve().parent

def text(node):
    return ' '.join(node.text_content().split()) if node is not None else ''

def first(node, cls):
    found = node.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," '+cls+' ")]')
    return found[0] if found else None

def markup(node):
    return html.tostring(node, encoding='unicode', with_tail=False)

def import_file(path):
    match = re.fullmatch(r'Gardenz-Actuz-(\d{4}-\d{2}-\d{2})\.html', path.name)
    if not match:
        raise ValueError('Nom de bulletin non reconnu : '+path.name)
    document = html.fromstring(path.read_bytes())
    main = document.xpath('//main[contains(concat(" ",normalize-space(@class)," ")," paper ")]')
    if len(main) != 1:
        raise ValueError('Journal principal absent ou ambigu : '+path.name)
    main = main[0]
    for node in list(main.xpath('.//script|.//*[@onclick]|.//*[@onerror]|.//*[@onload]')):
        if node.tag == 'script':
            node.drop_tree()
        else:
            for name in list(node.attrib):
                if name.startswith('on'):
                    del node.attrib[name]
    # La navigation et la recherche appartiennent au kiosque, pas au bulletin.
    for node in list(main.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," archive ") or contains(concat(" ",normalize-space(@class)," ")," searchbox ") or @id="empty"]')):
        node.drop_tree()
    for image in main.xpath('.//img[starts-with(@src,"data:")]'):
        data = image.get('src')
        encoded = re.fullmatch(r'data:image/(png|jpeg|webp|gif);base64,(.*)', data, re.S)
        if not encoded:
            raise ValueError('Image intégrée non prise en charge')
        payload = base64.b64decode(encoded[2], validate=True)
        extension = {'jpeg':'jpg'}.get(encoded[1], encoded[1])
        relative = 'assets/'+hashlib.sha256(payload).hexdigest()[:20]+'.'+extension
        (ROOT / relative).write_bytes(payload)
        image.set('src', relative)
        image.set('loading', 'lazy')
        image.set('decoding', 'async')
    articles = []
    selected = main.xpath('.//article[contains(concat(" ",normalize-space(@class)," ")," story ")]|.//section[contains(concat(" ",normalize-space(@class)," ")," brief ")]')
    for index, article in enumerate(selected, 1):
        heading = article.xpath('.//h2|.//h3')
        if not heading:
            raise ValueError('Article sans titre')
        if not article.get('id'):
            article.set('id', 'breve-'+str(index))
        images = article.xpath('.//img')
        captions = article.xpath('.//figcaption')
        articles.append({
            'id':article.get('id'), 'title':text(heading[0]),
            'summary':text(first(article,'summary')) or text(article)[:400], 'text':text(article),
            'image':images[0].get('src') if images else '',
            'region':re.sub(r'^\d+\s*/\s*','',text(first(article,'story-number'))),
            'sourceDate':text(first(article,'date')), 'status':text(first(article,'status')),
            'creditHTML':markup(captions[0]) if captions else ''
        })
    if not articles:
        raise ValueError('Aucun article importé')
    return {'date':match[1], 'html':''.join(markup(child) for child in main), 'count':len(articles), 'articles':articles}

def run(paths):
    target = ROOT / 'editions.json'
    editions = {e['date']:e for e in json.loads(target.read_text())}
    for path in paths:
        edition = import_file(Path(path))
        editions[edition['date']] = edition
    ordered = sorted(editions.values(), key=lambda e:e['date'], reverse=True)
    target.write_text(json.dumps(ordered, ensure_ascii=False, separators=(',',':')))
    print(json.dumps({'editions':len(ordered),'latest':ordered[0]['date'],'articles':sum(e['count'] for e in ordered)},ensure_ascii=False))

if __name__ == '__main__':
    if not sys.argv[1:]:
        raise SystemExit(__doc__)
    run(sys.argv[1:])
