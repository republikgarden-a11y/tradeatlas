"""Collecte RSS publique, sans clé ni IA payante. Ne produit pas une validation éditoriale."""
from __future__ import annotations
import concurrent.futures,datetime as dt,email.utils,hashlib,html,json,re,sys,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[('Newsweed','https://www.newsweed.fr/feed/','fr','France'),('Le Cannabiste','https://lecannabiste.com/feed/','fr','France'),('Marijuana Moment','https://www.marijuanamoment.net/feed/','en','Monde'),('Ganjapreneur','https://www.ganjapreneur.com/feed/','en','Monde'),('Hanf Magazin','https://www.hanf-magazin.com/feed/','de','Europe')]
UA='GardenzActuz/2.0 (veille de presse; liens vers les sources; une collecte quotidienne)'
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s or ''))).strip()
def canonical(u):
 p=urllib.parse.urlsplit(u);q=urllib.parse.parse_qsl(p.query)
 return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,urllib.parse.urlencode([(k,v) for k,v in q if not k.lower().startswith(('utm_','fbclid','gclid'))]),''))
def date(s):
 try:d=email.utils.parsedate_to_datetime(s)
 except (TypeError,ValueError):
  try:d=dt.datetime.fromisoformat(s.replace('Z','+00:00'))
  except (ValueError,AttributeError):return None
 return d.replace(tzinfo=dt.timezone.utc) if d.tzinfo is None else d

def parse(blob,source,now):
 name,url,lang,region=source;root=ET.fromstring(blob);out=[]
 for item in root.findall('.//item'):
  title=clean(item.findtext('title'));link=canonical(item.findtext('link') or '');published=date(item.findtext('pubDate'))
  if not title or not link.startswith('https://') or not published:continue
  if not now-dt.timedelta(hours=24)<=published<=now:continue
  description=clean(item.findtext('description'))[:160]
  # Un extrait de flux, jamais une conclusion juridique ou médicale automatique.
  out.append(dict(id=hashlib.sha256(link.encode()).hexdigest()[:20],title=title,url=link,source=name,sourceFeed=url,language=lang,region=('Francophone' if lang=='fr' else 'International'),publishedAt=published.isoformat(),collectedAt=now.isoformat(),excerpt=description,status='Extrait du flux · à vérifier',image='',credit=''))
 return sorted(out,key=lambda x:x['publishedAt'],reverse=True)[:4]

def fetch(source,now):
 name,url,*_=source
 try:
  req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/rss+xml,application/xml,text/xml'})
  with urllib.request.urlopen(req,timeout=20) as r:
   if r.status!=200:raise ValueError('HTTP '+str(r.status))
   blob=r.read(2_000_001)
   if len(blob)>2_000_000:raise ValueError('Flux trop volumineux')
  items=parse(blob,source,now)
  return items,dict(name=name,url=url,ok=True,count=len(items),checkedAt=now.isoformat())
 except Exception as e:return [],dict(name=name,url=url,ok=False,count=0,checkedAt=now.isoformat(),error=type(e).__name__)

def image(item):
 """Image réellement publiée ; pas de contournement d'un refus de la source."""
 try:
  req=urllib.request.Request(item['url'],headers={'User-Agent':UA})
  with urllib.request.urlopen(req,timeout=12) as r:page=r.read(1_500_000).decode('utf-8','replace')
  tag=re.search(r'<meta\b[^>]*(?:property|name)=[\"\']og:image[\"\'][^>]*>',page,re.I)
  if not tag:return
  found=re.search(r'content=[\"\']([^\"\']+)',tag[0],re.I)
  if not found:return
  u=urllib.parse.urljoin(item['url'],html.unescape(found[1]))
  if urllib.parse.urlsplit(u).scheme!='https':return
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=12) as r:
   typ=r.headers.get_content_type();blob=r.read(1_500_001)
  ext={'image/jpeg':'jpg','image/png':'png','image/webp':'webp'}.get(typ)
  if not ext or len(blob)>1_500_000:return
  relative='assets/live-'+hashlib.sha256(blob).hexdigest()[:20]+'.'+ext
  (ROOT/relative).write_bytes(blob);item.update(image=relative,imageSource=u,credit=item['source']+' · visuel og:image de l’article ; crédit individuel et nature documentaire non vérifiés. Illustration possible.')
 except Exception:pass

def main():
 now=dt.datetime.now(dt.timezone.utc);target=ROOT/'data/latest.json';previous=json.loads(target.read_text()) if target.exists() else {}
 if '--if-needed' in sys.argv and previous.get('lastSuccess') and date(previous['lastSuccess']).astimezone(ZoneInfo('Europe/Paris')).date()==now.astimezone(ZoneInfo('Europe/Paris')).date():
  print('Collecte du jour déjà réussie.');return
 results=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(lambda s:fetch(s,now),SOURCES))
 fresh=[i for items,_ in results for i in items];health=[h for _,h in results];ok=sum(h['ok'] for h in health)
 stored={i['id']:i for i in previous.get('items',[]) if date(i.get('publishedAt','')) and date(i['publishedAt'])>=now-dt.timedelta(days=30)}
 for i in fresh:
  if i['id'] in stored:i.update({k:v for k,v in stored[i['id']].items() if k in ['image','imageSource','credit','collectedAt']})
  stored[i['id']]=i
 selected=[i for i in fresh if not i.get('image')][:6]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(image,selected))
 data=dict(version=2,mode='public-rss',attemptedAt=now.isoformat(),lastSuccess=now.isoformat() if ok else previous.get('lastSuccess'),status='ok' if ok==len(SOURCES) else 'partial' if ok else 'error',sources=health,items=sorted(stored.values(),key=lambda i:i['publishedAt'],reverse=True),windowHours=24,notice='Collecte automatique de flux publics. Les titres et extraits appartiennent aux sources. Ce fil ne remplace pas les bulletins vérifiés. Aucune synthèse médicale ou juridique générée automatiquement.')
 target.parent.mkdir(exist_ok=True);tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2));tmp.replace(target)
 history=ROOT/'data/history';history.mkdir(exist_ok=True);(history/(now.astimezone(ZoneInfo('Europe/Paris')).date().isoformat()+'.json')).write_text(json.dumps({**data,'items':fresh},ensure_ascii=False,indent=2))
 print(f'{ok}/{len(SOURCES)} sources accessibles · {len(fresh)} articles dans les dernières 24 h · {len(stored)} conservés')
 if not ok:raise SystemExit(1)
if __name__=='__main__':main()
