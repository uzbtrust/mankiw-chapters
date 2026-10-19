from pathlib import Path
from html import escape
from html.parser import HTMLParser
import re,json

base=Path('/Users/uzbtrust/Documents/Codex/2026-10-13/sh-2/work/chapters')
p=base/'chapter-08.html';s=p.read_text()
s=s.replace('a. To‘g‘ri, standart farazlarda.','a. Noto‘g‘ri.')
s=s.replace('Miqdor ta’siri esa egiluvchan taklif tufayli katta bo‘lishi mumkin.','Miqdorning qisqarishi ikkala tomonning javobiga bog‘liq; bu misolda noelastik talab qisqarishni cheklaydi. Xaridor ortiqchaligi ko‘proq, sotuvchi ortiqchaligi esa kamroq kamayadi.')
s=s.replace('Sotuvchi oladigan birlik narxi pasayadi. Ammo jami tushum PS×Q₂ miqdori albatta pasayadi deb aytib bo‘lmaydi: miqdor kamayishi bilan birlik narxning o‘zgarishi birga ta’sir qiladi. Elastiklik va qiymatlar berilmagan.','Sotuvchi oladigan birlik narxi pasayadi va sotilgan miqdor ham kamayadi. Shuning uchun sotuvchining soliqdan keyingi jami tushumi PS×Q₂ <strong>albatta kamayadi</strong>: musbat narx ham, musbat miqdor ham oldingi qiymatidan kichik. Xaridorning jami sarfi haqidagi javobdan farqli ravishda, buning yo‘nalishini aniqlash uchun elastiklikning aniq soni kerak emas.')
s=s.replace('0≤T≤300 da Q musbat; T=300 da Q=0.','0≤T<300 da Q musbat; T=300 da Q=0.')
s=s.replace('<li>tushumni','<li>Tushumni').replace('<li>egiluvchanlik','<li>Egiluvchanlik').replace('<li>laffer','<li>Laffer')

def t(x,y,text,anchor='start',color='#365449',size=14):
 return f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" fill="{color}" font-size="{size}">{escape(text)}</text>'
def line(x1,y1,x2,y2,color='#8c9c90',dash=True):
 return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="1.2"'+(' stroke-dasharray="5 5"' if dash else '')+'/>'
def poly(points,color):return '<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{color}" fill-opacity=".36"/>'
def wrap(i,title,desc,inside,caption,height=430):
 return f'<figure class="diagram"><svg viewBox="0 0 720 {height}" role="img" aria-labelledby="{i}-title {i}-desc"><title id="{i}-title">{escape(title)}</title><desc id="{i}-desc">{escape(desc)}</desc><g font-family="system-ui,sans-serif" font-size="14">{inside}</g></svg><figcaption>{caption}</figcaption></figure>'

def tax(i,title,caption,letters=False,gain=False):
 X=lambda q:85+q/45*550;Y=lambda p:340-p/120*285
 D=lambda q:100-2*q;S=lambda q:20+2*q
 q0,qt,pb,ps,p0=20,15,70,50,60
 z=''
 if not gain:
  z+=poly([(X(0),Y(pb)),(X(0),Y(100)),(X(qt),Y(pb))],'#91c5b0')
  z+=poly([(X(0),Y(20)),(X(0),Y(ps)),(X(qt),Y(ps))],'#d4b2a0')
  z+=poly([(X(0),Y(ps)),(X(qt),Y(ps)),(X(qt),Y(pb)),(X(0),Y(pb))],'#dec878')
 z+=poly([(X(qt),Y(pb)),(X(q0),Y(p0)),(X(qt),Y(ps))],'#d98258')
 z+=line(X(0),45,X(0),340,dash=False)+line(X(0),340,650,340,dash=False)
 z+=f'<path d="M{X(0)} {Y(100)}L{X(44)} {Y(D(44))}" fill="none" stroke="#17695f" stroke-width="3"/>'
 z+=f'<path d="M{X(0)} {Y(20)}L{X(44)} {Y(S(44))}" fill="none" stroke="#c06843" stroke-width="3"/>'
 for q,pr,label in [(qt,pb,'Q₂'),(q0,p0,'Q₁')]:z+=line(X(q),Y(pr),X(q),340)+t(X(q),365,label,'middle')
 for pr,label in [(pb,'PB'),(p0,'P₁'),(ps,'PS')]:z+=line(X(0),Y(pr),X(qt if pr!=p0 else q0),Y(pr))+t(72,Y(pr)+5,label,'end')
 z+=t(570,80,'Taklif',color='#a14e30')+t(570,307,'Talab',color='#17695f')+t(84,30,'Narx')+t(645,386,'Miqdor','end')
 if letters:
  for q,pr,label in [(5,84,'A'),(7,65,'B'),(7,55,'D'),(5,34,'F'),(16.5,64,'C'),(16.5,54,'E')]:z+=t(X(q),Y(pr)+4,label,'middle',size=15)
  z+=t(110,414,'A = CS soliqli; F = PS soliqli; B+D = tushum; C+E = sof yo‘qotish',size=13)
 else:
  if not gain:z+=t(X(7),Y(60)+5,'Tushum','middle',size=13)
  z+=t(350,155,'Sof yo‘qotish',color='#a14e30',size=13)+line(345,161,X(17),Y(60),dash=False)
  z+=t(110,414,'PB − PS = T; Q₂ < Q₁. Soyalar chiziqlar bilan chegaralangan.',size=13)
 return wrap(i,title,'Talab va taklif Q1, P1 da kesishadi. Q2 da talab narxi PB, taklif narxi PS; shu vertikal pona soliqdir. Tushum miqdor o‘qidan Q2 gacha, sof yo‘qotish Q2 dan Q1 gacha.',z,caption)

replacements={
 'c8-tax':tax('c8-tax','Soliq ponasi va farovonlik hududlari','Soliqsiz CS=A+B+C, PS=D+E+F. Soliqli CS=A, PS=F, tushum=B+D; sof yo‘qotish=C+E.',True),
 'c8-gain':tax('c8-gain','Soliq tufayli bajarilmagan savdolar','Q₂ dan Q₁ gacha talab qiymati taklif xarajatidan yuqori. Soliq bu bitimlarni to‘xtatib, soyali uchburchakdagi yutuqni yo‘qotadi.',gain=True),
 'c8-review-graph':tax('c8-review-graph','Soliq tushumi va sof yo‘qotish','Tushumning eni Q₂, balandligi PB−PS=T. Q₂–Q₁ oralig‘idagi talab-taklif orasidagi uchburchak sof yo‘qotishdir.'),
 'c8-pizza':tax('c8-pizza','Pitsa bozorida bir dollarlik soliq','T=$1. Grafik shartli: narx va miqdorning sonli tenglamalari berilmagan. A va F xususiy ortiqchalik; B+D davlatga o‘tadi; C+E yo‘qoladi.',True),
}

# Each panel uses its own scale; the zeros and curves are computed from the model.
z=''
for offset,title,color,fn,mx in [(0,'Sof yo‘qotish: soliqning kvadratiga bog‘liq','#a14e30',lambda v:v*v/8,800),(310,'Davlat tushumi: stavka × qolgan savdo miqdori','#17695f',lambda v:v*(20-v/4),400)]:
 X=lambda v:85+v/80*550;Y=lambda v:offset+245-v/mx*170
 z+=line(85,offset+65,85,offset+245,dash=False)+line(85,offset+245,645,offset+245,dash=False)
 pts=' '.join(f'{X(v):.2f},{Y(fn(v)):.2f}' for v in range(81))
 z+=f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>'+t(85,offset+32,title,size=16)
 z+=t(645,offset+275,'Soliq T →','end')+t(75,offset+263,'0','end')
 if offset:z+=t(275,offset+110,'Laffer egri chizig‘i',color=color)
 else:z+=t(155,offset+177,'DWL ∝ T²',color=color)
replacements['c8-curves']=wrap('c8-curves','Soliq miqdori, sof yo‘qotish va davlat tushumi','Yuqorida sof yo‘qotish soliq kvadratiga mutanosib ortadi. Pastda tushum avval ortadi, cho‘qqiga chiqadi, bozor yo‘qolganda nolga tushadi.',z,'Soddalashtirilgan chiziqli bozor shakli. Har bir panelning o‘z vertikal masshtabi bor; bu muayyan mamlakat uchun optimal stavka degan da’vo emas.',610)

# Two panels show receipts before and after a buyer tax. Geometry is normalized.
z=''
for off,before in [(0,True),(405,False)]:
 X=lambda q:85+q/45*550;Y=lambda p:off+315-p/120*245
 q,pb,ps=(20,60,60) if before else (15,70,50)
 z+=poly([(X(0),Y(0)),(X(q),Y(0)),(X(q),Y(ps)),(X(0),Y(ps))],'#91c5b0')
 if not before:z+=poly([(X(0),Y(ps)),(X(q),Y(ps)),(X(q),Y(pb)),(X(0),Y(pb))],'#dec878')
 z+=line(X(0),off+45,X(0),off+315,dash=False)+line(X(0),off+315,650,off+315,dash=False)
 z+=f'<path d="M{X(0)} {Y(100)}L{X(42)} {Y(16)}" fill="none" stroke="#17695f" stroke-width="3"/>'
 z+=f'<path d="M{X(0)} {Y(20)}L{X(42)} {Y(104)}" fill="none" stroke="#c06843" stroke-width="3"/>'
 if not before:z+=f'<path d="M{X(0)} {Y(80)}L{X(40)} {Y(0)}" fill="none" stroke="#17695f" stroke-width="2" stroke-dasharray="6 5"/>'
 z+=t(85,off+27,'Soliqsiz' if before else 'Xaridorga soliqdan keyin',size=16)
 for pr,lab in ([(60,'P₁')] if before else [(70,'PB'),(50,'PS')]):z+=line(X(0),Y(pr),X(q),Y(pr))+t(72,Y(pr)+5,lab,'end')
 z+=t(X(q),off+338,'Q₁' if before else 'Q₂','middle')
 z+=t(550,off+93,'Taklif',color='#a14e30')+t(565,off+299,'Talab',color='#17695f')
 z+=t(170,off+258,'P₁×Q₁' if before else 'PS×Q₂',size=16)
 if not before:z+=t(145,Y(60)+4,'T×Q₂',size=13)+t(390,off+363,'Punktir: talab − soliq',size=13)
 z+=t(85,off+387,'Xaridor sarfi = sotuvchi tushumi' if before else 'Xaridor sarfi PB×Q₂ = sotuvchi tushumi PS×Q₂ + davlat tushumi T×Q₂',size=13)
replacements['c8-socks']=wrap('c8-socks','Paypoq bozorida pul tushumlari','Soliqsiz xaridor xarajati va sotuvchi tushumi P1Q1. Soliqdan keyin xaridor PBQ2 to‘laydi, sotuvchi PSQ2 oladi, davlat farqni yig‘adi.',z,'Bu to‘rtburchaklar pul sarfi va tushumni ifodalaydi; ularni iste’molchi yoki ishlab chiqaruvchi ortiqchaligi bilan adashtirmang.',810)

X=lambda v:90+v/300*530;Y=lambda v:345-v/30000*285
z=line(90,45,90,345,dash=False)+line(90,345,640,345,dash=False)
for v in [0,15000,30000]:z+=line(90,Y(v),620,Y(v))+t(78,Y(v)+5,f'{v:,}'.replace(',',' '),'end',size=13)
for v in [0,75,150,225,300]:z+=t(X(v),370,str(v),'middle',size=13)
for fn,color in [(lambda v:200*v-2*v*v/3,'#17695f'),(lambda v:v*v/3,'#a14e30')]:
 pts=' '.join(f'{X(v):.2f},{Y(fn(v)):.2f}' for v in range(301))
 z+=f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>'
z+=t(90,30,'Qiymat · dollar')+t(640,402,'Soliq T · dollar','end')+t(143,121,'R(T) = 200T − (2/3)T²',color='#17695f')+t(370,45,'DWL(T) = T²/3',color='#a14e30')
z+=f'<circle cx="{X(150)}" cy="{Y(15000)}" r="5" fill="#17695f"/>'+t(X(150)+10,Y(15000)-10,'R eng katta: 15 000',size=13)
replacements['c8-quant']=wrap('c8-quant','10-masala: tushum va sof yo‘qotish','R(T)=200T−(2/3)T² nolda va 300 da nol, 150 da 15000. DWL(T)=T²/3 300 da 30000.',z,'Har bir nuqta berilgan tenglamalardan hisoblangan. T=150 da R=15 000, DWL=7 500; T=300 da R=0, DWL=30 000.',430)

def replace(m):
 f=m[0];idmatch=re.search(r'<title id="([^"]+)-title"',f)
 return replacements.get(idmatch[1],f) if idmatch else f
s=re.sub(r'<figure\b.*?</figure>',replace,s,flags=re.S)
p.write_text(s)
class P(HTMLParser):
 def __init__(self):super().__init__();self.text=[]
 def handle_data(self,d):self.text.append(d)
parser=P();parser.feed(s)
j=p.with_suffix('.json');c=json.loads(j.read_text());c['wordCount']=len(re.findall(r'\S+',' '.join(parser.text)));c['diagramCount']=s.count('<svg');j.write_text(json.dumps(c,ensure_ascii=False,indent=2))
print('Chapter 8 corrected: claims and all seven diagrams; words',c['wordCount'])
