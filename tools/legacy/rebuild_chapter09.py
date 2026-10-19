from pathlib import Path
from html import escape
import re, json

OUT = Path('/Users/uzbtrust/Documents/Codex/2026-10-13/sh-2/work/chapters')
parts = []
sections = []
diagram_count = 0

def section(sid, title, topics, text, kicker='9-bob · Xalqaro savdo'):
    sections.append({'id':sid,'title':title,'sourceTopics':topics})
    parts.append(f'<section class="lesson-section" id="{sid}"><div class="section-kicker">{kicker}</div><h2>{title}</h2>{text}</section>')

def q(kind, n, prompt, answer):
    return f'<details class="answer" data-kind="{kind}" data-q="{n}"><summary><span class="q-number">{n:02d}</span> {prompt}</summary><div class="answer-body">{answer}</div></details>'

def table(heads, rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join(f'<th>{x}</th>' for x in heads)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{x}</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def txt(x,y,s,fill='#33483f',size=13,anchor='middle'):
    return f'<text x="{x:g}" y="{y:g}" fill="{fill}" font-size="{size}" text-anchor="{anchor}">{escape(s)}</text>'

def line(x1,y1,x2,y2,color='#81918b',dash=False,width=1.5):
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="5 4"' if dash else '')+'/>'

def poly(points,fill,opacity=1):
    return '<polygon points="'+' '.join(f'{x:g},{y:g}' for x,y in points)+f'" fill="{fill}" opacity="{opacity}"/>'

def finish_svg(title,desc,content,caption):
    global diagram_count
    diagram_count += 1
    return f'<figure class="diagram"><svg viewBox="0 0 640 360" width="100%" role="img" aria-labelledby="c9-fig-{diagram_count}-title c9-fig-{diagram_count}-desc"><title id="c9-fig-{diagram_count}-title">{escape(title)}</title><desc id="c9-fig-{diagram_count}-desc">{escape(desc)}</desc>{content}</svg><figcaption>{caption}</figcaption></figure>'

def chart(mode,title,caption):
    X=lambda v:80+48*v
    Y=lambda v:290-2.4*v
    P=lambda pts,fill:poly([(X(a),Y(b)) for a,b in pts],fill)
    T=lambda a,b,s:txt(X(a),Y(b),s)
    H=lambda p,s,d=True:line(80,Y(p),570,Y(p),dash=d)+txt(70,Y(p)+4,s,anchor='end')
    Q=lambda a,p,s:line(X(a),Y(p),X(a),290,dash=True)+txt(X(a),311,s)
    c=''
    ticks=[]
    if mode=='closed':
        c+=P([(0,100),(5,50),(0,50)],'#d7eee7')+P([(0,0),(5,50),(0,50)],'#f4ddcd')
        c+=T(1.8,72,'Iste’molchi yutug‘i')+T(1.8,26,'Ishlab chiqaruvchi yutug‘i')
        c+=H(50,'P₀')+Q(5,50,'Q₀')
    elif mode=='export':
        c+=P([(0,100),(3,70),(0,70)],'#d7eee7')
        c+=P([(0,50),(5,50),(3,70),(0,70)],'#e2e8f1')
        c+=P([(0,0),(5,50),(0,50)],'#f4ddcd')
        c+=P([(3,70),(5,50),(7,70)],'#cbe7dd')
        c+=T(1,84,'A')+T(1.9,60,'B')+T(1.6,25,'C')+T(5,62,'D')
        c+=H(50,'P₀')+H(70,'Pᵥ')+Q(3,70,'Qᴰ')+Q(5,50,'Q₀')+Q(7,70,'Qˢ')
        c+=line(X(3),268,X(7),268)+T(5,4,'Eksport = Qˢ − Qᴰ')
    elif mode=='import':
        c+=P([(0,100),(5,50),(0,50)],'#d7eee7')
        c+=P([(0,30),(3,30),(5,50),(0,50)],'#e2e8f1')
        c+=P([(0,0),(3,30),(0,30)],'#f4ddcd')
        c+=P([(3,30),(5,50),(7,30)],'#cbe7dd')
        c+=T(1.5,70,'A')+T(1.6,40,'B')+T(1,15,'C')+T(5,35,'D')
        c+=H(50,'P₀')+H(30,'Pᵥ')+Q(3,30,'Qˢ')+Q(5,50,'Q₀')+Q(7,30,'Qᴰ')
        c+=line(X(3),268,X(7),268)+T(5,4,'Import = Qᴰ − Qˢ')
    elif mode=='tariff':
        c+=P([(0,100),(5,50),(0,50)],'#d7eee7')
        c+=P([(0,50),(5,50),(6,40),(0,40)],'#d7eee7')
        c+=P([(0,20),(2,20),(4,40),(0,40)],'#f4ddcd')
        c+=P([(2,20),(4,20),(4,40)],'#f0bdb2')
        c+=P([(4,20),(6,20),(6,40),(4,40)],'#d9e4f2')
        c+=P([(6,40),(6,20),(8,20)],'#f0bdb2')
        c+=P([(0,0),(2,20),(0,20)],'#f4ddcd')
        c+=T(1.7,73,'A')+T(5.5,44,'B')+T(1.4,30,'C')+T(3.3,25,'D')+T(5,29,'E')+T(6.8,25,'F')+T(.8,8,'G')
        c+=H(50,'P₀')+H(40,'Pᵥ + t')+H(20,'Pᵥ')
        c+=Q(2,20,'Q₁ˢ')+Q(4,40,'Q₂ˢ')+Q(6,40,'Q₂ᴰ')+Q(8,20,'Q₁ᴰ')
        c+=line(X(4),270,X(6),270)+T(5,3,'Tarifdan keyingi import')
    elif mode=='wine':
        c+=P([(0,30),(3,30),(4.5,45),(0,45)],'#f4ddcd')
        c+=P([(3,30),(7,30),(5.5,45),(4.5,45)],'#f0bdb2')
        c+=H(50,'P₀')+H(45,'Pᵥ′')+H(30,'Pᵥ')
        c+=Q(3,30,'Qˢ')+Q(4.5,45,'Qˢ′')+Q(5.5,45,'Qᴰ′')+Q(7,30,'Qᴰ')
        c+=T(1.5,37,'PS o‘sishi')+T(5,36,'Sof zarar')
    elif mode=='importfall':
        c+=P([(0,30),(3,30),(4,40),(0,40)],'#f4ddcd')
        c+=P([(3,30),(7,30),(6,40),(4,40)],'#cbe7dd')
        c+=H(50,'P₀')+H(40,'Pᵥ₁')+H(30,'Pᵥ₂')
        c+=Q(3,30,'Q₂ˢ')+Q(4,40,'Q₁ˢ')+Q(6,40,'Q₁ᴰ')+Q(7,30,'Q₂ᴰ')
        c+=T(5,34,'TS o‘sishi')
    elif mode=='exportfall':
        c+=P([(0,60),(4,60),(3,70),(0,70)],'#d7eee7')
        c+=P([(3,70),(7,70),(6,60),(4,60)],'#f0bdb2')
        c+=H(50,'P₀')+H(70,'Pᵥ₁')+H(60,'Pᵥ₂')
        c+=Q(3,70,'Q₁ᴰ')+Q(4,60,'Q₂ᴰ')+Q(6,60,'Q₂ˢ')+Q(7,70,'Q₁ˢ')
        c+=T(5,66,'TS kamayishi')
    elif mode=='exporttax':
        c+=P([(3,70),(4.5,70),(4.5,55)],'#f0bdb2')
        c+=P([(4.5,55),(5.5,55),(5.5,70),(4.5,70)],'#d9e4f2')
        c+=P([(5.5,55),(5.5,70),(7,70)],'#f0bdb2')
        c+=H(50,'P₀')+H(70,'Pᵥ')+H(55,'Pᵥ − t')
        c+=Q(3,70,'Q₁ᴰ')+Q(4.5,55,'Q₂ᴰ')+Q(5.5,55,'Q₂ˢ')+Q(7,70,'Q₁ˢ')
        c+=T(3.9,64,'DWL')+T(5,63,'R')+T(6.1,64,'DWL')
        c+=T(5,11,'R = t × qolgan eksport')
    elif mode=='consumption':
        c+=P([(0,20),(6,20),(6,40),(0,40)],'#d9e4f2')
        c+=P([(6,40),(6,20),(8,20)],'#f0bdb2')
        c+=H(50,'P₀')+H(40,'Pᵥ + t')+H(20,'Pᵥ')
        c+=Q(2,20,'Q₁ˢ')+Q(6,40,'Q₂ᴰ')+Q(8,20,'Q₁ᴰ')
        c+=T(3,29,'Davlat tushumi: C + D + E')+T(6.8,25,'F')
    elif mode=='inelastic':
        c+=P([(3,30),(5,30),(5,50)],'#cbe7dd')
        c+=H(50,'P₀')+H(30,'Pᵥ')+Q(3,30,'Qˢ')+Q(5,50,'Qᴰ = Q₀')
        c+=line(X(5),50,X(5),290,'#17695f',width=3)+txt(X(5)+10,70,'Vertikal talab',anchor='start')
        c+=T(4.4,35,'Foyda')
    elif mode=='subsidy':
        c+=P([(2,60),(8,60),(8,80),(2,80)],'#d9e4f2')
        c+=P([(2,80),(2,60),(4,60)],'#f0bdb2')
        c+=P([(6,60),(8,60),(8,80)],'#f0bdb2')
        c+=H(50,'P₀')+H(80,'Pᵥ + s')+H(60,'Pᵥ')
        c+=Q(2,80,'Q₂ᴰ')+Q(4,60,'Q₁ᴰ')+Q(6,60,'Q₁ˢ')+Q(8,80,'Q₂ˢ')
        c+=T(2.6,66,'DWL')+T(5,70,'s × eksport')+T(7.4,66,'DWL')
    c+=line(80,290,580,290,width=2)+line(80,290,80,38,width=2)
    if mode!='inelastic':
        c+=line(80,50,560,290,'#17695f',width=3)+txt(540,277,'Talab',fill='#17695f',anchor='start')
    c+=line(80,290,560,50,'#c06843',width=3)+txt(535,60,'Taklif',fill='#c06843',anchor='start')
    c+=txt(80,25,'Narx',anchor='start')+txt(567,347,'Miqdor',anchor='end')+txt(72,306,'0')
    desc='Vertikal o‘qda narx, gorizontal o‘qda miqdor. Talab pasayadi, taklif ko‘tariladi; shartli chiziqli egri chiziqlardagi maydonlar matnda izohlangan.'
    return finish_svg(title,desc,c,caption)

def textilia_chart():
    X=lambda q:80+100*q
    Y=lambda p:292-(p-12)*11
    P=lambda pts,fill:poly([(X(a),Y(b)) for a,b in pts],fill)
    c=P([(0,16),(1,16),(3,20),(0,20)],'#f4ddcd')+P([(1,16),(3,20),(4,16)],'#cbe7dd')
    for p,label in [(16,'$16'),(20,'$20')]:
        c+=line(80,Y(p),590,Y(p),dash=True)+txt(70,Y(p)+4,label,anchor='end')
    for q,label in [(1,'1'),(3,'3'),(4,'4')]:
        p=20 if q==3 else 16
        c+=line(X(q),Y(p),X(q),292,dash=True)+txt(X(q),313,label)
    c+=line(80,292,590,292,width=2)+line(80,292,80,40,width=2)
    c+=line(X(0),Y(32),X(5),Y(12),'#17695f',width=3)+txt(570,275,'Talab',fill='#17695f',anchor='start')
    c+=line(X(0),Y(14),X(5),Y(24),'#c06843',width=3)+txt(570,152,'Taklif',fill='#c06843',anchor='start')
    c+=txt(185,229,'PS: −$8 mln')+txt(335,238,'TS: +$6 mln')+txt(80,25,'Narx ($)',anchor='start')+txt(580,347,'Futbolka miqdori (mln dona)',anchor='end')
    return finish_svg('Textilia: $20 dan $16 ga tushish','Savdosiz 3 million futbolka $20 dan sotiladi. Erkin savdoda $16 narxda ishlab chiqarish 1 million, iste’mol 4 million. Import 3 million.',c,'Masaladagi barcha narx va miqdorlar ko‘rsatilgan. Berilgan nuqtalar orasida chiziqlilik farazi qo‘llanadi: iste’molchi yutug‘i $14 mln oshadi, ishlab chiqaruvchi yutug‘i $8 mln kamayadi; sof foyda $6 mln.')

def tv_chart():
    X=lambda q:80+360*q
    H=135; L=225
    P=lambda pts,fill:poly([(X(a),b) for a,b in pts],fill)
    c=P([(0,L),(.2,L),(.4,H),(0,H)],'#f4ddcd')+P([(.2,L),(.4,L),(.4,H)],'#f0bdb2')+P([(.4,L),(1,L),(1,H),(.4,H)],'#d9e4f2')+P([(1,H),(1,L),(1.2,L)],'#f0bdb2')
    for y,label in [(H,'Pᴴ'),(L,'Pᴸ')]:
        c+=line(80,y,580,y,dash=True)+txt(70,y+4,label,anchor='end')
    for q,y,label in [(.2,L,'0,2'),(.4,H,'0,4'),(1,H,'1,0'),(1.2,L,'1,2')]:
        c+=line(X(q),y,X(q),292,dash=True)+txt(X(q),313,label)
    c+=line(80,292,590,292,width=2)+line(80,292,80,38,width=2)
    c+=line(X(.08),279,X(.63),31.5,'#c06843',width=3)+txt(304,50,'Taklif',fill='#c06843')
    c+=line(X(.77),31.5,X(1.32),279,'#17695f',width=3)+txt(385,50,'Talab',fill='#17695f')
    c+=txt(135,177,'C: $30 mln')+txt(207,209,'D: $10 mln')+txt(332,184,'E: $60 mln')+txt(470,211,'F: $10 mln')
    c+=txt(82,25,'Narx ($)',anchor='start')+txt(580,347,'Televizor miqdori (mln dona)',anchor='end')+txt(580,118,'Pᴴ − Pᴸ = $100',anchor='end')
    return finish_svg('Televizor narxi va $100 tarif','Past narxda ishlab chiqarish 0,2 million, iste’mol 1,2 million. $100 tarif narxni yuqori darajaga qaytaradi: ishlab chiqarish 0,4 million, iste’mol 1 million.',c,'Mutlaq narx berilmagan: Pᴴ eski narx, Pᴸ = Pᴴ − $100. Tarifdagi xaridor zarari C + D + E + F = $110 mln; C ishlab chiqaruvchiga, E davlatga o‘tadi; D + F = $20 mln sof yo‘qotish.')

section('c9-s1','Savdo yo‘nalishini qanday aniqlaymiz?',['Kirish','9-1','9-1a','9-1b','9-2: kichik mamlakat farazi'],'''
<p>Bir futbolkani mahalliy korxonadan 100 ming so‘mga yoki chetdan 80 ming so‘mga olish mumkin bo‘lsa, xaridor arzonini tanlashga intiladi. Xaridorning tejashi mahalliy korxonaning daromadi kamayishi bilan yonma-yon kelishi mumkin. Shu sabab xalqaro savdoni baholashda uch savol zarur: narx va miqdor qanday o‘zgaradi, kim yutadi, kim zarar ko‘radi, mamlakat bo‘yicha jami natija qanday bo‘ladi?</p>
<p class="source-note">Manbaning kirish misoli — AQSh to‘qimachilik va kiyim sanoati. Kitob chet eldagi sifatli, arzon mahsulotlar sabab ayrim ichki korxonalar yopilib, ishchilar ishsiz qolganini tasvirlaydi. AQSh iste’mol qiladigan kiyimlarning katta qismi import qilinishi haqidagi gap kitob yozilgan davrga tegishli. Bu bob shu o‘zgarishni talab, taklif va iqtisodiy yutuq bilan tushuntiradi.</p>
<h3>9-1a. Savdosiz bozor</h3>
<p>Kitobdagi Isoland — xayoliy mamlakat. Hukumat dastlab gazlama importi va eksportini taqiqlaydi. Shuning uchun faqat ichki xaridor va sotuvchilar qatnashadi. Narx talab bilan taklif kesishgan darajaga, P₀ ga, keladi. Q₀ birlik ishlab chiqariladi va aynan Q₀ birlik iste’mol qilinadi. Xaridorlarning to‘lashga tayyor summasi bilan haqiqiy to‘lovi orasidagi farq <strong>iste’molchi yutug‘i</strong>; sotuvchilar olgan tushum bilan ishlab chiqarish xarajati orasidagi farq <strong>ishlab chiqaruvchi yutug‘i</strong> bo‘ladi. Ularning yig‘indisi jami yutuqdir.</p>
'''+chart('closed','Isolandning savdosiz muvozanati','P₀ va Q₀ ichki talab hamda taklif kesishishidan aniqlanadi. Yuqoridagi yashil uchburchak iste’molchi yutug‘i, pastdagi och jigarrang uchburchak ishlab chiqaruvchi yutug‘idir.')+'''
<p>Yangi prezident Olivia Openminded iqtisodchilardan savdoni ochish narxga, guruhlarning farovonligiga va tarif zarurligiga qanday ta’sir qilishini so‘raydi. Tahlilning boshlang‘ich nuqtasi — shu yopiq bozor.</p>
<h3>9-1b. Jahon narxi va nisbiy ustunlik</h3>
<p><strong>Jahon narxi</strong> (world price), Pᵥ, mahsulotning xalqaro bozordagi narxidir. Pᵥ &gt; P₀ bo‘lsa, mamlakatdagi mahsulot xorijda qimmatroq sotiladi va mamlakat eksportchi bo‘ladi. Pᵥ &lt; P₀ bo‘lsa, chetdan olish arzonroq va mamlakat importchi bo‘ladi. Narxlar teng bo‘lsa, ushbu sodda modelda savdo hajmi nol bo‘lishi mumkin.</p>
<p>Savdosiz narx ishlab chiqarishning muqobil xarajatini aks ettiradi: bir birlik gazlama uchun boshqa nimalardan voz kechiladi? Ichki narxning jahon narxidan pastligi ushbu mahsulotda mamlakatning nisbiy ustunligiga ishora qiladi. Bu mutlaq unumdorlik musobaqasi emas. Bir mamlakat barcha mahsulotlarni kamroq mehnat bilan tayyorlasa ham, muqobil xarajatlar turlicha bo‘lgani uchun ikki tomon savdodan yutishi mumkin.</p>
<div class="callout"><h3>Modelning muhim sharti</h3><p>Isoland jahon bozoriga nisbatan kichik: uning savdo siyosati Pᵥ ni o‘zgartirmaydi. U <strong>narxni qabul qiluvchi</strong> (price taker) hisoblanadi. Jahon narxidagi gorizontal chiziq eksportchi uchun chet el talabini, importchi uchun chet el taklifini bildiradi. Tahlil raqobatli bozorni, bir xil mahsulotni va hisobga olinmagan tashqi ta’sirlar yo‘qligini ham nazarda tutadi. Transport xarajati kabi to‘siqlarni hozircha chetga qo‘yamiz. Katta mamlakatning savdosi jahon narxini o‘zgartirsa, ayrim siyosat natijalari uchun qo‘shimcha tahlil kerak.</p></div>
''')

section('c9-s2','Eksportchi: ishlab chiqaruvchi yutadi',['9-2a','Figure 2'],'''
<p>Pᵥ &gt; P₀ bo‘lsin. Korxona mahsulotni chet elda yuqori narxda sota olsa, ichkarida undan past narxni qabul qilishni istamaydi. Ichki xaridor esa Pᵥ dan qimmat to‘lamaydi, chunki xalqaro bozordan olish imkoniyati bor. Natijada ichki narx ham Pᵥ ga tenglashadi.</p>
<p>Yuqori narx taklif egri chizig‘i bo‘ylab ishlab chiqarishni oshiradi, talab egri chizig‘i bo‘ylab ichki iste’molni kamaytiradi. <strong>Eksport = Qˢ − Qᴰ</strong>. Bu ichki bozorda ortiqcha mahsulot qolib ketganini anglatmaydi: qolgan qismini xorijiy xaridorlar oladi. Ichki taklif va ichki talabning teng bo‘lmasligi xalqaro savdo mavjud bozor uchun nomuvozanat emas.</p>
'''+chart('export','Eksportchi mamlakatning yutuqlari','A, B, C va D manbadagi 2-rasmga mos. B iste’molchidan ishlab chiqaruvchiga o‘tgan yutuq; D esa savdo yaratgan qo‘shimcha sof foyda.')+table(['Ko‘rsatkich','Savdosiz','Erkin savdoda','O‘zgarish'],[['Iste’molchi yutug‘i, CS','A + B','A','−B'],['Ishlab chiqaruvchi yutug‘i, PS','C','B + C + D','+(B + D)'],['Jami yutuq, TS','A + B + C','A + B + C + D','+D']])+'''
<p>Mahalliy iste’molchi avval arzonroq olgan, endi ko‘proq to‘laydi va kamroq xarid qiladi: uning zarari B. Korxona yuqori narxdan va qo‘shimcha eksportdan yutadi: foydasi B + D. B mamlakat ichidagi qayta taqsimot, D esa oldin mavjud bo‘lmagan yutuq. Shuning uchun mamlakatning sof foydasi D ga teng.</p>
<p>Oddiy misol: mahalliy meva chet elda qimmatroq sotila boshlasa, bog‘bonning daromadi o‘sadi. Shu mevani oladigan ichki xaridor uchun xarajat oshishi mumkin. «Eksport ko‘paydi» degan xabarning o‘zi har bir insonning farovonligi oshganini isbotlamaydi.</p>
<div class="warning"><p><strong>Ko‘p uchraydigan xato:</strong> eksport paydo bo‘lishini ichki talabning siljishi bilan tushuntirish. Ushbu modelda talab va taklif chiziqlari joyida qoladi; jahon narxi sabab ular bo‘ylab harakat yuz beradi. Jahon bozoriga kirish savdo qilish imkoniyatini kengaytiradi.</p></div>
''')

section('c9-s3','Importchi: iste’molchi yutadi',['9-2b','Figure 3','g‘oliblar zarar ko‘rganlarni qoplash imkoniyati'],'''
<p>Pᵥ &lt; P₀ bo‘lsa, chet el sotuvchisi arzonroq mahsulot taklif qiladi. Raqobat ichki narxni Pᵥ ga tushiradi. Mahalliy korxonalar bu narxda kamroq ishlab chiqaradi, iste’molchilar esa ko‘proq sotib oladi. <strong>Import = Qᴰ − Qˢ</strong>. Iste’molning hammasi import bo‘lishi shart emas: mahsulotning bir qismini ichki korxonalar, qolganini xorij yetkazadi.</p>
'''+chart('import','Importchi mamlakatning yutuqlari','A, B, C va D manbadagi 3-rasmga mos. B ishlab chiqaruvchidan iste’molchiga o‘tgan yutuq, D mamlakatning qo‘shimcha sof foydasidir.')+table(['Ko‘rsatkich','Savdosiz','Erkin savdoda','O‘zgarish'],[['CS','A','A + B + D','+(B + D)'],['PS','B + C','C','−B'],['TS','A + B + C','A + B + C + D','+D']])+'''
<p>Xaridorning foydasi ikki manbadan keladi: avval ham olgan mahsulotini arzonroq oladi va eski narxda olmagan ayrim birliklarni endi sotib oladi. Korxonaning yo‘qotishi pastroq narx hamda qisqargan ishlab chiqarishdan keladi. Xaridor foydasi korxona zararidan D miqdor katta.</p>
<p>Sof foyda yana ikki iqtisodiy imkoniyatni aks ettiradi. Birinchisi, ichki xarajati jahon narxidan yuqori ayrim birliklarni chetdan arzonroq olish. Ikkinchisi, xaridor qiymat bergan, ammo savdosiz narxda olmagan qo‘shimcha birliklarni iste’mol qilish. Chiziqli chiziqlarda bu imkoniyatlar grafikdagi ikkita kichik uchburchak bo‘lib, birgalikda D ni beradi.</p>
<div class="callout"><p><strong>«Savdo hammani yaxshiroq holatga keltirishi mumkin»</strong> deganda g‘oliblarning foydasi zarar ko‘rganlarning yo‘qotishini qoplashga yetishi tushuniladi. Qoplash amalda avtomatik sodir bo‘lmaydi. Ishidan ayrilgan ishchi haqiqiy zarar ko‘rishi mumkin. Samaradorlik va adolat turli savollar: jami yutuq oshishi uning teng taqsimlanganini bildirmaydi.</p></div>
<p>Shu sabab savdo siyosati siyosiy bahsga aylanadi. Zarar bir nechta korxonada to‘planishi, foyda esa millionlab xaridorlarga oz-ozdan tarqalishi mumkin. Korxonalar uyushib himoya talab qilishi osonroq. Mamlakat bo‘yicha foydali siyosatning ham qarshilari bo‘lishi tabiiy.</p>
<div class="interactive" data-interactive="trade"><p>Jahon narxini savdosiz muvozanat narxidan pastga yoki yuqoriga o‘zgartiring. Ichki ishlab chiqarish va iste’mol, import yoki eksport oralig‘i hamda CS va PS maydonlari qanday o‘zgarishini kuzating. So‘ng importga tarif qo‘shib, davlat tushumi bilan ikkita sof yo‘qotish maydonini ajrating.</p></div>
''')

section('c9-s4','Tarif: himoyaning iqtisodiy bahosi',['9-2c','Figure 4'],'''
<p><strong>Tarif</strong> (tariff) — chetda ishlab chiqarilib, ichki bozorda sotiladigan mahsulotga import solig‘i. Agar mamlakat shu mahsulotni eksport qilib, import qilmasa, import tarifi bu modelda ta’sirsiz. Tarifni tahlil qilish uchun importchi mamlakatdan boshlaymiz.</p>
<p>Har birlikka t miqdor tarif qo‘yilsa, importchi xorijga Pᵥ va hukumatga t to‘laydi. Import davom etayotgan kichik mamlakatda ichki narx <strong>Pᵥ + t</strong> bo‘ladi. Mahalliy korxona ham shu yuqori narxda sotadi. Tarif faqat import mahsuloti narxini oshirib, mahalliy mahsulot narxini o‘zgartirmaydi, deyish xato.</p>
<p>Narx oshganda ichki ishlab chiqarish Q₁ˢ dan Q₂ˢ ga ko‘tariladi; iste’mol Q₁ᴰ dan Q₂ᴰ ga tushadi. Import oralig‘i torayadi. Quyidagi tahlilda tarif savdoni butunlay to‘xtatadigan darajadan kichik. Agar Pᵥ + t savdosiz P₀ ga yetsa yoki oshsa, import nolga tushadi; muvozanat P₀ da qoladi va import solig‘idan tushum bo‘lmaydi.</p>
'''+chart('tariff','Import tarifi va C, D, E, F maydonlari','C mahalliy ishlab chiqaruvchining qo‘shimcha yutug‘i; E davlat tushumi. D qimmat ichki ishlab chiqarish, F esa yo‘qolgan foydali iste’mol sabab paydo bo‘lgan sof yo‘qotishdir.')+table(['Ko‘rsatkich','Erkin savdo','Tarif bilan','O‘zgarish'],[['CS','A + B + C + D + E + F','A + B','−(C + D + E + F)'],['PS','G','C + G','+C'],['Davlat tushumi','0','E','+E'],['TS','A + B + C + D + E + F + G','A + B + C + E + G','−(D + F)']])+'''
<div class="formula"><p>Davlat tushumi = t × (Q₂ᴰ − Q₂ˢ).</p><p>Chiziqli chiziqlarda sof yo‘qotish, DWL = ½t(Q₂ˢ − Q₁ˢ) + ½t(Q₁ᴰ − Q₂ᴰ).</p></div>
<p>C va E yo‘qolib ketmagan: xaridordan korxonaga hamda davlatga o‘tgan. Jami yutuqqa davlat tushumi qo‘shilishi shart. Ammo D va F hech kimga o‘tmaydi. D: ayrim birliklarni jahon narxida sotib olish arzonroq bo‘lsa ham, tarif sabab ularni qimmatroq ichki resurslar bilan tayyorlaymiz. F: ayrim xaridorlar mahsulotni jahon narxidan ko‘proq qadrlaydi, lekin tarif qo‘shilgan narxda ololmaydi. Foydali almashinuv yuz bermaydi.</p>
<p>Demak, xaridor zarari = ishlab chiqaruvchi foydasi + davlat tushumi + sof yo‘qotish. Korxonadagi ish o‘rinlari saqlanishi haqiqiy foyda bo‘lishi mumkin, ammo shu foydaning xaridor va boshqa sohalar hisobidan qancha xarajat bilan olingani ham hisoblanadi. Bu natija kichik, raqobatli mamlakat modelining natijasidir.</p>
''')

section('c9-s5','Kvota rentasi va prezidentga tavsiya',['FYI: Import Quotas','9-2d'],'''
<h3>FYI: import kvotasi</h3>
<p><strong>Import kvotasi</strong> — chetdan keltirish mumkin bo‘lgan miqdorning yuqori chegarasi. Cheklov kuchga kirsa, arzon xorijiy mahsulot yetishmaydi va ichki narx ko‘tariladi. Bir xil import hajmini keltirib chiqaradigan tarif va kvota ichki iste’mol, ishlab chiqarish, CS, PS hamda ishlab chiqarish va iste’mol buzilishlarini bir xil qiladi. Farq narxlar oralig‘idagi pulni kim olishidadir.</p>
<p>Kvota ruxsatnomasi egasi mahsulotni Pᵥ dan olib, Pₖ ichki narxda sotadi. Uning <strong>kvota rentasi</strong> = (Pₖ − Pᵥ) × kvota miqdori. Bu umumiy foyda emas, cheklangan import huquqidan keladigan qo‘shimcha daromad. Tarif rasmidagi E kvotada ruxsatnoma egasiga tegishi mumkin.</p>
'''+table(['Ruxsatnoma qanday beriladi?','E maydoni kimga tegadi?','Ichki jami farovonlik'],[['Davlat bozor qiymatida sotadi yoki auksion qiladi','Davlatga','Mos tarif bilan bir xil'],['Ichki importchilarga bepul beradi','Ichki ruxsatnoma egalariga','Renta ichki yutuq sifatida hisobga olinadi; DWL qoladi'],['Xorijiy eksportchilarga beriladi','Xorijiy korxonalarga','D + F ga qo‘shimcha E ham mamlakatdan chiqadi']])+'''
<p class="source-note">Kitobdagi tarixiy misolda AQSh ba’zan Yaponiyadan avtomobil eksportini «ixtiyoriy» cheklashni so‘ragan. Yaponiya hukumati ruxsatnomalarni yapon firmalariga bergan; rentani ular olgan. AQSh nuqtayi nazaridan bu mos tarifdan yomonroq: tarifdagi davlat tushumi ham xorijga ketadi. Bu barcha kvotalarning rentasi albatta xorijga ketadi degani emas.</p>
<h3>9-2d. Iqtisodchilarning uch javobi</h3>
<ol class="step-list"><li><strong>Narx va miqdor:</strong> savdo ochilgach, narx Pᵥ ga boradi. Narx ko‘tarilsa eksport, pasaysa import paydo bo‘ladi; ishlab chiqarish va iste’mol qarama-qarshi yo‘nalishda o‘zgaradi.</li><li><strong>Kim yutadi:</strong> eksportda sotuvchi, importda xaridor yutadi. Har ikkala holatda g‘oliblar foydasi zarar ko‘rganlar yo‘qotishidan katta.</li><li><strong>Tarif kerakmi:</strong> ushbu modelda samaradorlik uchun erkin savdo yaxshiroq. Tarif importchini savdosiz holatga yaqinlashtirib, D + F ni yo‘qotadi.</li></ol>
<p>Prezidentga yana bir tavsiya bor: zarar ko‘ruvchilarning qiyinchiligini yumshatish uchun ijtimoiy himoya yetarli bo‘lsin. Masalan, vaqtinchalik yordam yoki qayta o‘qitish siyosatini muhokama qilish mumkin. Qaysi yordam yaxshi ishlashi alohida savol; grafik faqat qoplash uchun umumiy iqtisodiy imkoniyat mavjudligini ko‘rsatadi.</p>
''')

section('c9-s6','Savdoning grafikdan tashqaridagi foydalari',['9-2e'],'''
<p>CS va PS hisoblari muhim, ammo savdoning barcha foydasini qamramaydi. Kitob yana beshta imkoniyatni ajratadi.</p>
<div class="concept-grid"><div><h3>Ko‘proq xilma-xillik</h3><p>Turli mamlakat mahsulotlari aynan bir xil emas. Manbada Germaniya va AQSh pivosi misol bo‘ladi. Savdo xaridorga narxdan tashqari ta’m, sifat va uslub tanlovini kengaytiradi. Mahalliy hayotda turli kiyim yoki telefon modelini tanlash ham shu fikrni ko‘rsatadi.</p></div><div><h3>Ko‘lam samarasi</h3><p>Ba’zi mahsulotlarning bir birlik xarajati katta hajmda tayyorlaganda kamayadi. Kichik ichki bozor qimmat uskunadan to‘liq foydalanishga yetmasligi mumkin. Eksport bozori ishlab chiqarish hajmini kengaytirib, xarajatni pasaytirish imkonini beradi.</p></div><div><h3>Kuchliroq raqobat</h3><p>Xorijiy raqibdan himoyalangan firma narxni raqobatli darajadan yuqoriga ko‘tarishi mumkin. Import muqobil tanlov beradi va bozor hokimiyatini kamaytiradi. Natijada xaridor foydasi va resurslardan foydalanish yaxshilanishi mumkin.</p></div><div><h3>Yuqoriroq unumdorlik</h3><p>Savdo ochilganda eng unumdor firmalar kengayadi, eng sust firmalar qisqaradi yoki chiqib ketadi. Mehnat va kapital kam unumdor joydan ko‘proq mahsulot beradigan joyga ko‘chsa, iqtisodiyotning umumiy unumdorligi oshadi. Bu o‘tish ayrim ishchilar uchun og‘riqli bo‘lishi mumkin.</p></div><div><h3>Bilim va texnologiya oqimi</h3><p>Yangi g‘oyalar ko‘pincha ularni mujassam qilgan mahsulot bilan birga keladi. Kitobdagi qishloq xo‘jaligiga tayangan kambag‘al mamlakat kompyuterni boshidan yaratishga urinishi o‘rniga import orqali kompyuter texnologiyasini o‘rganishi mumkin.</p></div></div>
<p>Bu foydalarni oldingi uchburchaklarga yana raqamsiz qo‘shib yubormaymiz: ularning kattaligi uchun alohida ma’lumot kerak. Lekin oddiy bitta mahsulot bozoridagi grafik erkin savdoni qo‘llab-quvvatlovchi dalillarning faqat bir qismini ko‘rsatishini bilish zarur.</p>
''')

section('c9-s7','Savdoni cheklash uchun besh dalil',['9-3','9-3a','9-3b','9-3c','9-3d','9-3e'],'''
<p>Isolandning gazlama korxonalari narx pasayishini xohlamaydi. Ularning savdoni cheklash haqidagi dalillarini iqtisodiy mazmuni va amaliy xavfi bilan baholaymiz.</p>
<h3>9-3a. «Ish o‘rinlarini saqlash kerak»</h3>
<p>Import sabab ichki gazlama ishlab chiqarishi qisqarsa, bu sohada ish yo‘qolishi mumkin. Iqtisodchilar bu zararni inkor etmaydi. Ammo savdo boshqa, nisbiy ustunlik mavjud sohalarga bozor ham yaratadi. Eksport kengayishi va xaridorning boshqa ehtiyojlar uchun puli qolishi yangi ishlab chiqarishga imkon beradi. Muammo barcha ishning yo‘qolishidan ko‘ra ishlarning qayta taqsimlanishi va o‘tish qiyinchiligidir.</p>
<p>«Xorij hamma narsani arzonroq qiladi, bizda ish qolmaydi» degan xulosa mutlaq va nisbiy ustunlikni aralashtiradi. Hatto xorij har bir mahsulotda unumdor bo‘lsa ham, muqobil xarajati eng qulay sohada ichki mamlakat ixtisoslasha oladi. Bu uzoq muddatdagi imkoniyat; aniq ishchi yangi ishga darhol va xarajatsiz o‘tadi degani emas. Qisqa muddatda ijtimoiy yordam muhim.</p>
<h3>9-3b. «Milliy xavfsizlik uchun zarur»</h3>
<p>Po‘lat qurol va tanklar uchun kerak; urushda import uzilsa, mudofaa xavf ostida qolishi mumkin. Haqiqiy xavfsizlik ehtiyoji ayrim ishlab chiqarish quvvatini saqlashni oqlashi mumkin. Lekin himoyadan foyda oladigan firma o‘z ahamiyatini oshirib ko‘rsatishga manfaatdor.</p>
<p>Dalilni kim aytayotganiga qarash kerak. Po‘lat sotuvchi himoyani istaydi; po‘lat xarid qiladigan harbiylar esa arzon importdan yutadi va zaxirani arzonroq to‘plashi mumkin. Xavfsizlik foydasi iste’molchi xarajatiga tenglashtirib baholanadi; har bir soha «strategik» deb atalishi yetarli emas.</p>
<h3>9-3c. «Yosh sanoatni vaqtincha himoyalaylik»</h3>
<p>Yangi tarmoq tajriba to‘plab, keyin xorij bilan raqobatlashishi mumkin, deyiladi. Eski sanoat ham moslashish uchun vaqtinchalik himoya so‘rashi mumkin. Amaliy savollar og‘ir: qaysi tarmoq kelajakda samarali bo‘ladi, xaridor bugun ko‘taradigan xarajatni kelajak foydasi qoplaydimi, himoya qachon tugaydi?</p>
<p>Hukumat g‘oliblarni oldindan aniq bilmaydi. Siyosiy ta’siri kuchli korxona tanlanishi va vaqtinchalik imtiyoz doimiylashishi mumkin. Agar keyingi foyda haqiqatan yetarli bo‘lsa, mulkdor yoki investor dastlabki zararni o‘zi ko‘tarishga tayyor bo‘lishi kerak. Ko‘plab yangi firmalar himoyasiz ham dastlab zarar bilan ishlab, keyin o‘sadi. Himoya talabi o‘z-o‘zidan bozor muvaffaqiyatsizligini isbotlamaydi.</p>
<h3>9-3d. «Xorij adolatsiz raqobat qiladi»</h3>
<p>Neighborland hukumati gazlama firmalariga subsidiya bersa, ular arzonroq sotishi mumkin. Isoland korxonasi bundan zarar ko‘radi. Ammo Isoland xaridori arzon narxdan yutadi. Kichik importchi modelida xaridor foydasi ichki ishlab chiqaruvchi zararidan katta, subsidiya xarajatini esa Neighborland soliq to‘lovchilari ko‘taradi.</p>
<p>Turli mehnat yoki ekologik qoidalar haqidagi xavotirlar alohida tekshiriladi. Ushbu bobning xulosasi chet eldagi barcha siyosat yaxshi degani emas; xorij subsidiyasiga import cheklovi bilan javob berish ichki iste’molchiga ham xarajat yuklashini bildiradi.</p>
<h3>9-3e. «Cheklov muzokarada bosim vositasi bo‘lsin»</h3>
<p>Isoland: «Bug‘doyimizga tarifni olib tashlamasang, gazlamangga tarif qo‘yaman», deb tahdid qilishi mumkin. Qo‘shni yon bersa, ikkala tarafda savdo erkinlashadi. Shu jihatdan tahdidning nazariy foydasi bor.</p>
<p>Ammo qo‘shni yon bermasa, ikki yomon tanlov qoladi: tarifni joriy qilib, o‘z farovonligini kamaytirish yoki tahdiddan qaytib, keyingi muzokaralardagi ishonchlilikni yo‘qotish. Javob tariflari vaziyatni kuchaytirishi mumkin. «Savdo uchun tahdid»ning foydasi natija va qarshi tarafning javobiga bog‘liq; o‘z zararini kafolatlaydigan cheklov foydali kelishuvga teng emas.</p>
''')

section('c9-s8','Savdo bitimlari, WTO va ekspertlar',['Case Study: Trade Agreements and the World Trade Organization','Ask the Experts: Trade Deals and Tariffs'],'''
<h3>Bir tomonlama va ko‘p tomonlama yo‘l</h3>
<p><strong>Bir tomonlama</strong> (unilateral) usulda mamlakat o‘z cheklovlarini boshqalardan shart talab qilmasdan kamaytiradi. Kitob XIX asr Buyuk Britaniyasi, keyingi davrdagi Chili va Janubiy Koreyani misol qiladi. <strong>Ko‘p tomonlama</strong> (multilateral) usulda mamlakatlar kelishib, to‘siqlarni birgalikda qisqartiradi.</p>
<p class="source-note">Manbaning tarixiy ketma-ketligi: 1993-yilda kelishilgan NAFTA AQSh, Meksika va Kanada savdosini erkinlashtirish misoli sifatida beriladi; yangilangan USMCA 2020-yilda kuchga kirgan. Ikkinchi jahon urushidan keyingi GATT muzokaralari 1930-yillardagi yuqori tariflar tajribasiga javob bo‘lgan. Kitob a’zolarning o‘rtacha tarifi urushdan keyingi 20 foizdan yuqori darajadan 2000-yilda 5 foizdan pastga tushganini qayd etadi.</p>
<p>GATT qoidalari bilan bog‘liq <strong>Jahon savdo tashkiloti</strong> (WTO) 1995-yilda tuzilgan, markazi Jenevada. Kitobning 2021-yil ma’lumotida 164 a’zo jahon savdosining 98 foizini qamragan. Vazifalari: savdo bitimlarini boshqarish, muzokaralar uchun maydon berish, a’zolar o‘rtasidagi nizolarni ko‘rib chiqish. Bu raqamlar joriy holat haqidagi ma’lumot sifatida ishlatilmaydi.</p>
<p>Ko‘p tomonlama kelishuv ichki to‘siq bilan birga xorijdagini ham kamaytirishi mumkin. Siyosiy foydasi ham bor: Isoland gazlama korxonalari importga qarshi bo‘lsa, Neighborland bug‘doy tarifini pasaytirishdan yutadigan Isoland dehqonlari kelishuvni qo‘llashi mumkin. Biroq muzokara muvaffaqiyatsiz bo‘lsa, bir tomonlama ochilishi mumkin bo‘lgan bozor ham yopiq qoladi.</p>
<p class="source-note">Kitob Trump ma’muriyati davridagi qaytishni ham ko‘rsatadi. 2018-yil boshida AQSh–Xitoy savdosining oz qismi tarifga tortilgan; 2020-yil oxirida har ikki yo‘nalishdagi importning yarmidan ko‘pi taxminan 20 foizlik o‘rtacha tarif ostida bo‘lgan. Muallif keyingi yo‘nalish noaniqligini aytadi. Bu 2018–2020-yil tavsifi, bugungi tarif jadvali emas.</p>
<h3>Tarixiy ekspert so‘rovlari nimani ko‘rsatgan?</h3>
'''+table(['Bayonotning mazmuni','Rozi','Noaniq','Qarshi','Manbadagi sana'],[['Yirik oldingi savdo bitimlari ko‘pchilik amerikalikka foyda bergan','93%','7%','0%','11.11.2014'],['Yangi mehnat yoki ekologik talablar qabul qilinmaguncha savdoni erkinlashtirmaslik yomon siyosat','49%','26%','25%','27.03.2013'],['2019-yilgi AQSh import tariflari asosan amerikalik uy xo‘jaliklariga tushishi kutilgan','86%','14%','0%','29.05.2019'],['Tarif va Xitoy javoblari kam daromadli guruh hamda hududlarga og‘irroq tushishi kutilgan','75%','25%','0%','29.05.2019']])+'''
<p>Manba — IGM Economic Experts Panel. Bu tanlangan iqtisodchilarning tarixiy fikrlari; butun aholining so‘rovi ham, natijani o‘zi isbotlaydigan tajriba ham emas. Ikkinchi bayonotdagi bo‘linish savdo foydasini tan olish mehnat va ekologik talablar haqidagi barcha bahslarga bir xil javob bermasligini ko‘rsatadi.</p>
''')

section('c9-s9','Rivojlanish, oddiy buyumlar va «ixtirochi» hikoyasi',['In the News: Trade as a Tool for Economic Development','Questions to Discuss 1–2','9-4'],'''
<h3>Manbadagi yangilik: savdo va kambag‘allik</h3>
<p>Arthur C. Brooksning <em>Andy Warhol’s Guide to Public Policy</em> maqolasi 2015-yil 12-aprel kuni <em>New York Times</em>da chiqqan. Muallif Warholning kundalik oddiy buyumlarga e’tiborini siyosatga qo‘llaydi: odamlar yangilik va qimmat texnologiyani payqaydi, oddiy samarali yechimni chetda qoldirishi mumkin. U bezgakka qarshi oddiy chivin to‘rlari va maktabga qatnashni yaxshilashni misol qiladi; savdoni ham shunday oddiy, kuchli imkoniyat deb baholaydi.</p>
<p class="source-note">Maqola o‘sha davrdagi baholarni keltirgan: yigirma yildan ko‘proq vaqt davomida global kambag‘allik ulushi yiliga taxminan 1 foiz kamayishi, yiliga qariyb 70 mln odam kambag‘allikdan chiqishi, 1990-yildan buyon jami taxminan 1 mlrd odam; Xitoyda 1980-yillardan beri 680 mln odam mutlaq kambag‘allikdan chiqishi. Muallif o‘sish, islohotlar va xalqaro ishlab chiqarish zanjirlarini ta’kidlaydi. Bu 2015-yil maqolasidagi tarixiy baholar; «yiliga 1 foiz» iborasi noaniq bo‘lgani uchun uni bu yerda bir foiz punkt deb qayta talqin qilmaymiz.</p>
<p>Maqolada «Made in China» yozuvli krujka katta iqtisodiy jarayonning oddiy belgisi sifatida ishlatiladi. Muallif global daromad tengsizligi o‘sha davrning ko‘p yillarida kamayganini ham aytadi. Bular maqolaning dalillari va qarashlari: keltirilgan jami raqamlarning hammasini faqat savdoning alohida sababiy ta’siri deb o‘qish to‘g‘ri emas. Muallif savdo har bir muammoni yechmasligini, demokratiya va xavfsizlik ham kerakligini tan oladi.</p>
<div class="example"><h4>Muhokama 1: chetda tayyorlangan buyumni kim yutib sotib oladi?</h4><p>Masalan, telefon yorlig‘ida boshqa mamlakat ko‘rsatilgan bo‘lsa, xaridor uchun uning qiymati to‘langan narxdan yuqori, sotuvchi uchun narx xarajatdan yuqori bo‘lgani sabab ixtiyoriy savdodan odatda ikkala tomon yutadi. Aniq mamlakatni yorliqdan bilamiz; taxmin qilmaymiz. Mahalliy raqibning zarari esa alohida hisoblanadi.</p><h4>Muhokama 2: boy va kambag‘al mamlakat savdosi ishchiga qanday ta’sir qiladi?</h4><p>Eksport buyurtmasi kambag‘al mamlakatda ishga talab, tajriba va unumdorlikni oshirishi mumkin. Ish haqini mavjud mahalliy imkoniyatlar bilan taqqoslash kerak. Ayrim tarmoqlar yoki ishchilar zarar ko‘rishi, mehnat sharoiti muammolari saqlanishi mumkin. «Har bir ishchi albatta yutadi» deyish bobning taqsimot darsiga zid.</p></div>
<h3>9-4. Savdo texnologiyaga o‘xshashi mumkin</h3>
<p>Kitob AQSh shtatlari orasidagi erkin savdoni uzoq davom etgan misol sifatida beradi: Florida apelsin, Texas neft, Kaliforniya vino bilan ixtisoslashadi. Har kim faqat o‘z shtati mahsulotini iste’mol qilsa, tanlov va turmush darajasi qisqarardi. Mamlakatlar orasida ham shunday ixtisoslashish imkoniyati bor.</p>
<p>Isoland savdoni ochmagan bo‘lsin. Isabel Inventor bug‘doyni deyarli mehnatsiz gazlamaga «aylantirish» usulini topadi. Gazlama arzonlashadi; ayrim to‘qimachilar ishini yo‘qotadi, keyin bug‘doychilik yoki boshqa sohalarga o‘tadi. Odamlar buni texnologik taraqqiyot deb olqishlaydi. Jurnalist Roberto Reporter esa sirni ochadi: Isabel bug‘doyni chet elga olib chiqib, gazlamaga almashtirgan!</p>
<p>Hukumat bu faoliyatni yopadi, gazlama yana qimmatlashadi, eski fabrikalar ishini tiklaydi, turmush darajasi avvalgi holatga qaytadi. Hikoyaning maqsadi savdo ham resursni mahsulotga «aylantirish» usuli ekanini ko‘rsatishdir. Ishning bir sohadan boshqasiga ko‘chishi ham texnologiyada, ham savdoda yuz berishi mumkin. Natijani jami foyda va o‘tish xarajati bilan izchil baholash kerak.</p>
''')

review=[]
review.append(q('review',1,'Savdosiz ichki narx nisbiy ustunlik haqida nima bildiradi?', '''<p>Uni jahon narxi bilan taqqoslaymiz. P₀ &lt; Pᵥ — mahsulotning ichki muqobil xarajati nisbatan past, eksport imkoniyati bor. P₀ &gt; Pᵥ — shu mahsulotda xorijning nisbiy ustunligi bor, import qilish foydali. Faqat ichki narxning o‘zini bilib, boshqa mamlakatga nisbatan ustunlik haqida xulosa chiqarib bo‘lmaydi.</p>'''))
review.append(q('review',2,'Mamlakat qachon eksportchi, qachon importchi bo‘ladi?', '''<p>Erkin savdo ochilganda Pᵥ &gt; P₀ bo‘lsa narx ko‘tarilib, Qˢ &gt; Qᴰ bo‘ladi: farq eksport. Pᵥ &lt; P₀ bo‘lsa narx pasayib, Qᴰ &gt; Qˢ bo‘ladi: farq import. Narxlar tengligida sodda model savdo zaruratini ko‘rsatmaydi. Bu javob transport va boshqa savdo to‘siqlari hisobga olinmagan holat uchun.</p>'''))
review.append(q('review',3,'Importchi mamlakat grafigida savdodan oldingi va keyingi CS, PS hamda jami o‘zgarishni ko‘rsating.',chart('import','Nazorat 3: importchi mamlakat','Savdosiz CS = A, PS = B + C. Erkin savdoda CS = A + B + D, PS = C. Jami yutuq D ga oshadi.')+'''<p>Jahon narxi muvozanatdan past. Narx chizig‘ini P₀ dan Pᵥ ga tushiramiz. Xaridor B + D ni oladi, ishlab chiqaruvchi B ni yo‘qotadi. Ularning yig‘indisi +(B + D) − B = D. Grafikda savdo foydasi ichki qimmat ishlab chiqarishni almashtirish va yangi foydali iste’mol imkoniyatlaridan keladi.</p>'''))
review.append(q('review',4,'Tarif nima va uning iqtisodiy oqibatlari qanday?', '''<p>Importga soliq. Import davom etadigan kichik mamlakatda narx Pᵥ + t ga ko‘tariladi, ichki ishlab chiqarish o‘sadi, iste’mol hamda import kamayadi. CS kamayadi, PS va davlat tushumi oshadi. Tushum t × tarifdan keyingi importga teng. Xaridor zarari boshqa ikkala yutuqdan katta; farq ishlab chiqarish va iste’mol buzilishlarining sof yo‘qotishidir.</p>'''))
review.append(q('review',5,'Savdoni cheklash haqidagi besh dalil va iqtisodchilarning javobini ayting.', '''<ol><li><strong>Ish o‘rinlari:</strong> ayrim ishlar yo‘qoladi, lekin boshqa sohalarda ish va eksport imkoniyati ochiladi; o‘tishda yordam kerak.</li><li><strong>Milliy xavfsizlik:</strong> haqiqiy ehtiyoj himoyani oqlashi mumkin; firma o‘z rolini bo‘rttirishga manfaatdor.</li><li><strong>Yosh sanoat:</strong> kelajak foydasini oldindan tanlash qiyin; vaqtinchalik himoya doimiylashishi mumkin; istiqbolli firma investor topa olishi mumkin.</li><li><strong>Adolatsiz raqobat:</strong> xorij subsidiyasi ichki korxonani siqadi, ammo arzon importning xaridor foydasi kattaroq bo‘lishi mumkin.</li><li><strong>Muzokara vositasi:</strong> tahdid imtiyoz keltirishi mumkin, ammo muvaffaqiyatsizlikda o‘z zararimiz yoki ishonchlilik yo‘qotishi qoladi.</li></ol>'''))
review.append(q('review',6,'Erkin savdoga bir tomonlama va ko‘p tomonlama o‘tishning farqi va misollari?', '''<p>Bir tomonlama usul — o‘z cheklovini mustaqil kamaytirish; kitobdagi misol XIX asr Buyuk Britaniyasi. Ko‘p tomonlama usul — hamkorlar bilan o‘zaro kamaytirish; NAFTA, GATT muzokaralari misol. Ikkinchi usul xorij bozorini ham ochishi va eksportchi guruhlarning siyosiy qo‘llovini yig‘ishi mumkin; kelishuv chiqmasligi esa erkinlashishni to‘xtatishi mumkin.</p>'''))
section('c9-review','Nazorat savollari: 6 ta javob',['Questions for Review 1–6'],''.join(review),'9-bob · Manbadagi nazorat savollari')

apps=[]
apps.append(q('application',1,'Kanada vino import qiladi. Yevropadagi sovuq yoz uzum hosilini kamaytirsa, narx va farovonlik qanday o‘zgaradi?', '''<h4>a) Erkin savdo holati</h4><p>Kanada importi jahon ishlab chiqarishining kichik qismi: Kanada narxni qabul qiladi. Pᵥ &lt; P₀ bo‘lgani uchun vino import qilinadi. 3-rasm belgilari bilan CS = A + B + D, PS = C, TS = A + B + C + D. Ichki ishlab chiqarish Qˢ, iste’mol Qᴰ, import ularning farqidir.</p><h4>b) Gulf Stream o‘zgarishi va hosil yo‘qotilishi</h4><p>Yevropaning uzum hosili kamayishi jahon vino taklifini qisqartiradi; odatdagi boshqa shartlar o‘zgarmasa, jahon narxi Pᵥ′ ga ko‘tariladi. Kanada ham qimmatroq narx to‘laydi. Grafik yangi narx hali P₀ dan past, Kanada importchi bo‘lib qoladigan holatni ko‘rsatadi.</p>'''+chart('wine','Kanada vino bozori: jahon narxi oshishi','Pᵥ′ &gt; Pᵥ, lekin Pᵥ′ &lt; P₀. Ishlab chiqarish Qˢ dan Qˢ′ ga o‘sadi, iste’mol Qᴰ dan Qᴰ′ ga kamayadi. Jigarrang maydon PS o‘sishi; qizg‘ish maydon Kanadaning sof zararidir.')+table(['Ko‘rsatkich','Dastlab','Narx oshgach','Chiziqli holatda o‘zgarish'],[['CS','CS₀','CS₀ − xaridor zarari','−Δp(Qᴰ + Qᴰ′)/2'],['PS','PS₀','PS₀ + sotuvchi foydasi','+Δp(Qˢ + Qˢ′)/2'],['TS','CS₀ + PS₀','Oldingi TS − sof zarar','−Δp(M + M′)/2']])+'''<p>Bu yerda Δp = Pᵥ′ − Pᵥ, M va M′ — eski va yangi import. Kanada iste’molchisi zarar ko‘radi, ishlab chiqaruvchisi yutadi; import musbat bo‘lsa jami zarar bor. Chiziqli bo‘lmagan chiziqlarda tegishli egri chiziqlar ostidagi maydon olinadi. <strong>Chegara:</strong> narx P₀ dan ham yuqoriga chiqib, Kanada eksportchiga aylansa, boshlang‘ich import holatiga nisbatan jami o‘zgarishning ishorasi oshish miqdoriga bog‘liq. Masala narxning aniq kattaligini bermaydi, shuning uchun odatdagi javob import davom etishi sharti bilan aytiladi.</p>'''))

apps.append(q('application',2,'AQSh avtomobil importiga tarif qo‘yadi. Import, iste’molchi zarari, ishlab chiqaruvchi foydasi, tushum va sof yo‘qotishni ajrating.', '''<p>AQSh ushbu masalada jahon avtomobil bozorida narxni qabul qiluvchi deb berilgan. Tarif t narxni Pᵥ dan Pᵥ + t ga oshiradi. Mahalliy avtomobil ham qimmatlashadi. Grafikdagi belgilar gazlama uchun ishlatilgan belgilar bilan bir xil iqtisodiy ma’noga ega.</p>'''+chart('tariff','Avtomobil importiga tarif','Import Q₁ᴰ − Q₁ˢ dan Q₂ᴰ − Q₂ˢ ga kamayadi. Xaridorning C + D + E + F zarari ishlab chiqaruvchi C foydasi, davlat E tushumi va D + F sof yo‘qotishga ajraladi.')+'''<p><strong>Import qisqarishi</strong> = (Q₂ˢ − Q₁ˢ) + (Q₁ᴰ − Q₂ᴰ). <strong>CS o‘zgarishi</strong> = −(C + D + E + F); <strong>PS o‘zgarishi</strong> = +C; <strong>tushum</strong> = E = t(Q₂ᴰ − Q₂ˢ); <strong>DWL</strong> = D + F. D — xorij avtomobilini olishdan qimmatroq mahalliy ishlab chiqarishga o‘tish, F — jahon narxida foydali bo‘lgan xaridning bekor bo‘lishi. Sonlar berilmagan, shuning uchun dollar qiymatini o‘ylab topmaymiz.</p>'''))

apps.append(q('application',3,'Xitoy kiyim sanoati kengayib, jahon narxini pasaytirdi. Importchi AQSh va eksportchi Dominikan Respublikasini taqqoslang.', '''<h4>a) Importchi mamlakat</h4><p>Pᵥ₂ &lt; Pᵥ₁ &lt; P₀. Narxning pasayishi CS ni oshiradi, PS ni kamaytiradi. Ishlab chiqarish qisqaradi, iste’mol va import ko‘payadi. Xaridor foydasi mahalliy korxona zararidan katta; TS oshadi.</p>'''+chart('importfall','Kiyim importchisi: jahon narxi pasayadi','1 — eski holat, 2 — yangi holat. Yashil maydon sof foyda: importchi mamlakat ko‘proq birlikni arzon jahon narxida oladi.')+'''<h4>b) Eksportchi mamlakat</h4><p>P₀ &lt; Pᵥ₂ &lt; Pᵥ₁. Pastroq narxda mahalliy iste’molchi yutadi, ishlab chiqaruvchi zarar ko‘radi; ishlab chiqarish va eksport qisqaradi. Sotuvchi zarari xaridor foydasidan katta, TS kamayadi.</p>'''+chart('exportfall','Kiyim eksportchisi: jahon narxi pasayadi','Eksportchi ikki holatda ham eksportchi bo‘lib qolgan. Qizg‘ish maydon sof zarar: chetga sotiladigan mahsulotdan olinadigan qiymat kamaygan.')+'''<h4>c) O‘xshashlik va farq</h4><p>Ikkala mamlakatda ham CS oshadi va PS kamayadi. Jami natija savdo yo‘nalishiga bog‘liq: importchi arzonroq sotib oladi, eksportchi arzonroq sotadi. AQShning umumiy manfaatida pasayish ma’qul; Dominikan Respublikasining umumiy eksport manfaatida xavotirli. Biroq AQSh kiyim ishlab chiqaruvchisi qarshi, Dominikan iste’molchisi esa rozi bo‘lishi mumkin. Agar narx savdosiz narxni kesib o‘tib, savdo yo‘nalishi almashsa, yangi holat qayta hisoblanadi.</p>'''))

apps.append(q('application',4,'Arzon importdan qiynalayotgan eski yog‘och sanoati lobbichisi qaysi dalillarni ishlatadi? Iqtisodiy jihatdan qaysilari kuchliroq?', '''<h4>a) Siyosiy ishontirish</h4><p>Ikki mantiqli tanlov — ish o‘rinlari va adolatsiz raqobat. Birinchisi yopilishi mumkin bo‘lgan korxona, ishchi va hududni aniq ko‘rsatadi; ikkinchisi xorij qoidalari yoki subsidiyasini «teng sharoit» bilan bog‘laydi. Mudofaa uchun zarur yog‘och mahsuloti isbotlansa, xavfsizlik dalili ham ishlatilishi mumkin. Bu bashorat yagona to‘g‘ri javobga ega emas. Eski sanoatni «yosh tarmoq» deb himoyalash esa berilgan vaziyatga sust mos keladi.</p><h4>b) Iqtisodiy jihatdan shartli ravishda kuchli dalillar</h4><p><strong>Xavfsizlik:</strong> uzilishning katta ijtimoiy zarari bo‘lsa himoya mantiqli; lekin firma da’vosi bo‘rttirilishi va xarid xarajati oshishi mumkin. <strong>Yosh sanoat:</strong> kelajakdagi o‘rganish foydasi katta bo‘lsa vaqtinchalik yordam muhokama qilinadi; kim yutishini topish, xarajatni qoplash va yordamni tugatish qiyin, investor nega moliyalamasligi ham tushuntirilishi kerak. <strong>Muzokara vositasi:</strong> haqiqiy o‘zaro erkinlashish chiqsa foyda bor; tahdid muvaffaqiyatsiz bo‘lsa o‘z iste’molchimizga zarar yuklanadi. Bu tanlovlar dalilning shartlarini tekshirishni talab qiladi; «har qanday himoya yaxshi» xulosasini bermaydi.</p>'''))

apps.append(q('application',5,'Textiliada futbolka $20 va 3 mln dona. Savdo ochilgach narx $16, iste’mol 4 mln, ishlab chiqarish 1 mln. Grafik va yutuq o‘zgarishlarini hisoblang.', '''<h4>a) Miqdorlar</h4><p>Savdosiz P₀ = $20, Q₀ = 3 mln. Erkin savdoda Pᵥ = $16, Qˢ = 1 mln, Qᴰ = 4 mln. Import = 4 − 1 = <strong>3 mln dona</strong>. Narx $4 ga tushgan. Prezidentning Adam Smith asarini o‘qib bozorni ochishi manbaning hikoya qismidir.</p>'''+textilia_chart()+'''<h4>b) Maydonlardan hisoblash</h4><p>Masalaning uchburchak haqidagi ko‘rsatmasiga muvofiq berilgan nuqtalar orasidagi talab va taklifni chiziqli deb olamiz. Million dona bilan dollarning ko‘paytmasi million dollar beradi.</p><div class="formula"><p>ΔCS = 3 mln × $4 + ½ × (4 − 3) mln × $4 = <strong>+$14 mln</strong>.</p><p>ΔPS = −[1 mln × $4 + ½ × (3 − 1) mln × $4] = <strong>−$8 mln</strong>.</p><p>ΔTS = $14 mln − $8 mln = <strong>+$6 mln</strong>.</p></div><p>CS hisobida avvalgi 3 mln xaridning narx tejalishi va yangi 1 mln xaridning uchburchak foydasi bor. PS yo‘qotishida qolgan 1 mln ishlab chiqarishning pastroq narxi va to‘xtatilgan 2 mln birlikning yo‘qolgan yutug‘i bor. Sof foyda = ½ × $4 × [(3 − 1) + (4 − 3)] mln = $6 mln. Chiziqlilik berilmasa, faqat uch nuqtadan aniq maydon topib bo‘lmaydi.</p>'''))

apps.append(q('application',6,'Xitoy oziq-ovqat narxini pasaytirish uchun don eksportiga soliq qo‘ydi. Narx, CS, PS, davlat tushumi va jami farovonlikni tahlil qiling.', '''<h4>a) Boshlang‘ich eksport bozori</h4><p>Jahon narxi savdosiz narxdan yuqori: Pᵥ &gt; P₀; Q₁ˢ &gt; Q₁ᴰ va farq eksport. Quyidagi standart grafikda jahon narxi o‘zgarmaydi va eksport davom etadi deb olinadi. Xitoy katta ishlab chiqaruvchi ekani sabab bu shart haqiqiy holatni to‘liq tavsiflashga yetmasligi mumkin; masala uchun asosiy modelni ochiq aytamiz.</p>'''+chart('exporttax','Eksport solig‘i: ichki don narxi tushadi','Soliq bilan ichki narx Pᵥ − t. Eksport Q₁ˢ − Q₁ᴰ dan Q₂ˢ − Q₂ᴰ ga kamayadi. R davlat tushumi; ikki qizg‘ish uchburchak jami sof yo‘qotish.')+'''<h4>b) Ichki narx</h4><p>Eksportchi chetda Pᵥ olsa ham, har birlikdan t soliq to‘laydi; uning sof oladigan narxi Pᵥ − t. Ichki xaridor ham shu darajada sotib oladi. Narx pasayadi, iste’mol ko‘payadi, ishlab chiqarish kamayadi.</p><h4>c) Guruhlar va tushum</h4><p>CS oshadi, PS kamayadi; davlat t × qolgan eksport daromadini oladi. Soliqni chet el xaridori to‘liq to‘laydi, deb bo‘lmaydi: bu modelda jahon narxi o‘zgarmaydi, ichki sotuvchi oladigan sof narx pasayadi.</p><h4>d) Jami natija</h4><p>CS + PS + soliq tushumi kamayadi. Bir yo‘qotish — chetga qimmat sotish mumkin bo‘lgan birliklarning ichkarida pastroq qiymatli iste’molga o‘tishi; ikkinchisi — xarajati jahon narxidan past bo‘lgan ayrim ishlab chiqarishning to‘xtashi. Chiziqli holatda DWL = ½t[(Q₁ˢ − Q₂ˢ) + (Q₂ᴰ − Q₁ᴰ)]. Eksport butunlay to‘xtasa, ichki narx P₀ va tushum nol. Agar Xitoy jahon narxini sezilarli o‘zgartirsa, milliy farovonlikka narxlar nisbatining ta’siri ham qo‘shiladi; oddiy kichik mamlakat xulosasi shunda yetarli emas.</p>'''))

apps.append(q('application',7,'Importchi mamlakatda talab elastikligi haqidagi uch bayonot to‘g‘rimi?', '''<h4>a) «Talab elastikligi kattaroq bo‘lsa, savdo foydasi kattaroq»</h4><p><strong>Boshqa shartlar o‘zgarmaganda to‘g‘ri.</strong> Bir xil savdosiz muvozanat, jahon narxi va taklifni ushlaymiz. Talab narx pasayishiga ko‘proq javob bersa, qo‘shimcha iste’mol uchburchagi kattalashadi. Chiziqli holatda sof foyda = ½(P₀ − Pᵥ)[(Q₀ − Qˢ) + (Qᴰ − Q₀)]. Turli mamlakatning narxlari, boshlang‘ich hajmi va taklifi ham o‘zgarsa, elastiklikning o‘zi bilan foydani tartiblash mumkin emas.</p><h4>b) «Talab mutlaqo noelastik bo‘lsa, savdo foydasi yo‘q»</h4><p><strong>Noto‘g‘ri.</strong> Qᴰ o‘zgarmasa ham, ichki qimmat ishlab chiqarishning bir qismi arzon import bilan almashtiriladi. Iste’molni kengaytirish foydasi nol, ishlab chiqarish xarajatini tejash foydasi musbat bo‘lishi mumkin.</p>'''+chart('inelastic','Mutlaqo noelastik talabda import','Talab vertikal: iste’mol Q₀ da qoladi. Narx tushganda taklif Qˢ ga qisqaradi; yashil uchburchak qimmat ichki ishlab chiqarishni arzon import bilan almashtirish foydasidir.')+'''<h4>c) «Talab mutlaqo noelastik bo‘lsa, iste’molchi yutmaydi»</h4><p><strong>Noto‘g‘ri.</strong> U o‘sha miqdorni arzonroq oladi: ΔCS = (P₀ − Pᵥ)Q₀ &gt; 0. Miqdor o‘zgarmasligi narx tejalishi yo‘qligini anglatmaydi. Vertikal talabning yuqori chegarasi berilmaganda CS ning mutlaq darajasini aniqlamasligimiz mumkin, lekin narx pasayishidan uning o‘zgarishi aniq. Agar taklif ham umuman o‘zgarmasa va import paydo bo‘lmasa, alohida chegaraviy holatda sof yangi savdo foydasi nol bo‘lishi mumkin.</p>'''))

apps.append(q('application',8,'Import tarifi o‘rniga xuddi shu miqdordagi soliq barcha gazlama iste’moliga qo‘yilsa nima bo‘ladi?', '''<h4>a) Ishlab chiqarish va iste’mol</h4><p>Har bir sotib olingan birlik, ichki yoki import bo‘lishidan qat’i nazar, t soliq to‘laydi. Xaridor Pᵥ + t to‘laydi, lekin ishlab chiqaruvchi sof Pᵥ oladi. Shuning uchun iste’mol tarifdagidek <strong>Q₂ᴰ</strong>, ishlab chiqarish esa erkin savdodagidek <strong>Q₁ˢ</strong>. Import Q₂ᴰ − Q₁ˢ. Tarifdagi Q₂ˢ ga ishlab chiqarish o‘sishi bu safar yuz bermaydi.</p>'''+chart('consumption','Barcha iste’molga soliq','Xaridor narxi Pᵥ + t, sotuvchi sof narxi Pᵥ. Davlat tushumi butun Q₂ᴰ iste’moliga qo‘yilgan soliqdan keladi. F yagona sof yo‘qotish; tarifdagi D ishlab chiqarish buzilishi bu yerda yo‘q.')+'''<h4>b) Manbaning 4-rasmi maydonlari bilan jadval</h4>'''+table(['Ko‘rsatkich','Erkin savdo','Iste’mol solig‘i','O‘zgarish'],[['CS','A + B + C + D + E + F','A + B','−(C + D + E + F)'],['PS','G','G','0'],['Davlat tushumi','0','C + D + E','+(C + D + E)'],['TS','A + B + C + D + E + F + G','A + B + C + D + E + G','−F']])+'''<h4>c) Tarif bilan taqqoslash</h4><p>Iste’mol solig‘i tushumi tQ₂ᴰ; tarif tushumi t(Q₂ᴰ − Q₂ˢ). Birinchisi tQ₂ˢ miqdor ko‘proq: manbadagi C + D. Iste’mol solig‘ining DWL i F, tarifniki D + F; birinchisi kichikroq, chunki ishlab chiqarishni sun’iy ravishda ko‘paytirmaydi. Ikkala siyosat ham qimmat xaridor narxi sabab iste’molni qisqartiradi. Bu taqqoslash bir xil t, import saqlanishi va oddiy model uchun.</p>'''))

apps.append(q('application',9,'AQSh yiliga 1 mln televizor oladi: 400 ming ichki, 600 ming import. Narx $100 tushib, xarid 1,2 mln, ichki ishlab chiqarish 200 ming bo‘ldi. Natija va $100 tarifni hisoblang.', '''<h4>a) Texnologiya sabab arzonlashish</h4><p>Eski narx Pᴴ, yangi narx Pᴸ = Pᴴ − $100. Mutlaq narx berilmagan. Arzonlashish xaridorga foyda, ichki ishlab chiqaruvchiga zarar keltiradi. Import 600 mingdan <strong>1 mln</strong> donaga o‘sadi: 1,2 mln − 0,2 mln. Grafikda shu nuqtalar va narx oralig‘i ko‘rsatilgan.</p>'''+tv_chart()+'''<h4>b) Yutuq o‘zgarishi</h4><p>Berilgan nuqtalar orasida chiziqli chiziqlar va boshqa shartlar o‘zgarmasligini olamiz.</p><div class="formula"><p>ΔCS = $100 × (1 mln + 1,2 mln)/2 = <strong>+$110 mln</strong>.</p><p>ΔPS = −$100 × (0,4 mln + 0,2 mln)/2 = <strong>−$30 mln</strong>.</p><p>ΔTS = $110 mln − $30 mln = <strong>+$80 mln</strong>.</p></div><p>Xaridor foydasining $100 mln qismi avvalgi xarid narxining tejalishi, $10 mln qismi yangi 200 ming xaridning uchburchagi. Ishlab chiqaruvchi zararining $20 mln qismi qolgan 200 ming dona narxining tushishi, $10 mln qismi ishlab chiqarishi to‘xtagan 200 ming donaning uchburchagidir.</p><h4>c) Yangi jahon narxiga $100 tarif</h4><p>Ichki narx Pᴴ ga qaytadi. Iste’mol 1 mln, ishlab chiqarish 0,4 mln, import 0,6 mln. <strong>Tushum = $100 × 600 000 = $60 mln.</strong> DWL = ½ × $100 × 200 000 + ½ × $100 × 200 000 = <strong>$20 mln</strong>. Yangi erkin savdoga nisbatan CS −$110 mln, PS +$30 mln, davlat +$60 mln: jami −$20 mln. AQSh farovonligi nuqtayi nazaridan yomonroq; ichki televizor ishlab chiqaruvchilari va ularning ayrim ishchilari qo‘llashi mumkin. Dastlabki eski narx holatiga nisbatan tarifdan keyin ham +$60 mln davlat tushumi qoladi; bu tarifning yangi erkin savdodan yaxshiligini bildirmaydi.</p><h4>d) Arzonlashish texnologiya emas, Xitoyning $100 subsidiyasi bo‘lsa</h4><p>AQSh uchun bir xil narx va miqdorlar berilsa, yuqoridagi milliy CS, PS, tushum va DWL hisoblari o‘zgarmaydi. Subsidiyani Xitoy moliyalaydi; u AQSh xarajati emas. Xorij siyosatini yoqtirmaslik arzon import foydasini bekor qilmaydi. Butun dunyo farovonligini baholashda esa Xitoy soliq to‘lovchisi va ishlab chiqarish buzilishlarini ham hisoblash kerak; bu masalada ular uchun ma’lumot yo‘q.</p>'''))

apps.append(q('application',10,'Kichik po‘lat eksportchisi har eksport tonnasiga subsidiya beradi. Narx, miqdorlar va barcha yutuqlarga ta’siri qanday?', '''<p>Subsidiya s bo‘lsin. Jahon narxi o‘zgarmaydi. Firma xorijga sotganda Pᵥ + s olishi mumkin, shu sabab ichki xaridorga undan past narxda sotishga qiziqmaydi. Ichki narx <strong>Pᵥ + s</strong> ga ko‘tariladi. Ichki ishlab chiqarish Q₁ˢ dan Q₂ˢ ga o‘sadi, iste’mol Q₁ᴰ dan Q₂ᴰ ga qisqaradi. Eksport Q₂ˢ − Q₂ᴰ gacha ortadi.</p>'''+chart('subsidy','Eksport subsidiyasi: ko‘proq savdo, kamroq jami yutuq','Ko‘k to‘rtburchak davlat xarajati s(Q₂ˢ − Q₂ᴰ). Qizg‘ish uchburchaklar ortiqcha ishlab chiqarish va kamaygan foydali iste’molning sof yo‘qotishidir.')+'''<p>CS kamayadi, PS oshadi. Davlat tushumi manfiy: <strong>−s(Q₂ˢ − Q₂ᴰ)</strong>. Bu xarajatni ham qo‘shganda TS kamayadi. Chiziqli holatda <strong>DWL = ½s[(Q₂ˢ − Q₁ˢ) + (Q₁ᴰ − Q₂ᴰ)]</strong>. Qo‘shimcha ishlab chiqarilgan ayrim birlikning xarajati Pᵥ dan yuqori; subsidiya ularni baribir foydali ko‘rsatadi. Ayrim ichki xaridor mahsulotni Pᵥ dan ko‘proq qadrlaydi, lekin yuqori ichki narxda ololmaydi. Demak, eksportni ko‘paytirishning o‘zi samaradorlik mezoni emas. Davlat ishlab chiqaruvchi foydasidan ko‘proq xarajat qilgani uchun subsidiya ushbu kichik mamlakat modelida yaxshi siyosat hisoblanmaydi.</p>'''))
section('c9-applications','Masalalar va qo‘llanishlar: 10 ta yechim',['Problems and Applications 1–10'],''.join(apps),'9-bob · Barcha qismlari bilan ishlangan masalalar')

quizzes=[]
quizzes.append(q('quick',1,'9-1: Autarkada jun kostyum 3 unsiya oltin, qo‘shnilarda 2 unsiya. Savdo ochilsa nima bo‘ladi?', '''<p><strong>Javob: d.</strong> Ichki narx jahon narxidan yuqori, demak Autarka kostyum ishlab chiqarishda nisbiy ustunlikka ega emas va importchi bo‘ladi. Oltin birlik sifatida berilgan; 3 bilan 2 ni taqqoslash yo‘nalishni aniqlaydi. Arzon xorij kostyumi ichki narxni tushiradi.</p>'''))
quizzes.append(q('quick',2,'9-1: Openia po‘lat eksport qiladi. Eksport taqiqlansa narx va foyda oluvchi guruh?', '''<p><strong>Javob: b — narx pastroq, iste’molchilar yutadi.</strong> Eksportda jahon narxi savdosiz narxdan yuqori. Taqiq ichki talab va taklif muvozanatiga qaytarib, narxni tushiradi. Ishlab chiqaruvchi zarar ko‘radi, ichki po‘lat xaridori arzonroq oladi.</p>'''))
quizzes.append(q('quick',3,'9-2: Ectenia kofe savdosini ochgach, ichki narx tushdi. Ishlab chiqarish va savdo yo‘nalishi?', '''<p><strong>Javob: c.</strong> Ichki ishlab chiqarish kamayadi, mamlakat kofe importchisiga aylanadi. Narxning tushishi jahon narxi savdosiz narxdan pastligini bildiradi; talab ko‘payishi va taklif kamayishi orasidagi farq import bilan qoplanadi.</p>'''))
quizzes.append(q('quick',4,'9-2: Mamlakat importchiga aylansa, CS, PS va TS qanday o‘zgaradi?', '''<p><strong>Javob: a.</strong> PS kamayadi, CS va TS oshadi. CS ning B + D foydasi PS ning B zararidan katta; D musbat sof foyda. Shuning uchun jami ta’sir ushbu modelda noaniq deb aytilmaydi.</p>'''))
quizzes.append(q('quick',5,'9-2: Importchi tarif qo‘ysa, qaysi miqdor oshadi?', '''<p><strong>Javob: b — ichki taklif etilgan miqdor.</strong> Narx oshib, taklif egri chizig‘i bo‘ylab ishlab chiqarish ko‘payadi. Talab etilgan miqdor, import va samaradorlik kamayadi. Bu taklif chizig‘ining o‘ngga siljishi emas.</p>'''))
quizzes.append(q('quick',6,'9-2: Qaysi siyosat ishlab chiqaruvchiga foyda, xaridorga zarar berib, savdoni ham ko‘paytiradi?', '''<p><strong>Javob: c.</strong> Jahon narxi savdosiz ichki narxdan yuqori bo‘lganda savdoni ochish. Narx ko‘tarilib, eksport paydo bo‘ladi. Import tarifini oshirish ham sotuvchiga foyda berishi mumkin, lekin u savdo hajmini kamaytiradi; shu sabab savolning barcha shartiga mos kelmaydi.</p>'''))
quizzes.append(q('quick',7,'9-3: Brobdingnag arqon ishlab chiqaruvchilarini subsidiyalaydi. Importchi Lilliput uchun eng samarali siyosat?', '''<p><strong>Javob: a — subsidiyalangan narxda savdoni davom ettirish.</strong> Lilliput xaridorining arzon narxdan foydasi ichki ishlab chiqaruvchi zararidan katta. Subsidiyani xorij moliyalaydi. Importga tarif, savdoni to‘xtatish yoki o‘z subsidiyasi oddiy kichik mamlakat modelida qo‘shimcha buzilish keltiradi.</p>'''))
quizzes.append(q('quick',8,'9-3: Ko‘p tomonlama savdo bitimlari odatda nimaga intiladi?', '''<p><strong>Javob: c.</strong> Turli mamlakatlarda tariflarni bir vaqtda pasaytirib, himoya uchun siyosiy bosimni yumshatish. Import raqibi qarshi bo‘lsa ham, xorij bozorining ochilishidan yutadigan eksportchi kelishuvni qo‘llaydi. Maqsad tariflarni tenglashtirish yoki faqat yosh sanoatga qoldirish emas.</p>'''))
section('c9-quick','QuickQuiz: 8 ta javob va sabablari',['QuickQuiz 1–8','QuickQuiz Answers'],''.join(quizzes),'9-bob · Manbadagi tezkor savollar')

section('c9-s13','Atamalar va og‘zaki imtihon rejasi',['Key Concepts','Chapter in a Nutshell','og‘zaki takror'],'''
<div class="key-concepts"><dl><dt>Jahon narxi (world price)</dt><dd>Mahsulot xalqaro bozorda sotiladigan narx.</dd><dt>Tarif (tariff)</dt><dd>Import mahsulotiga qo‘yilgan soliq.</dd><dt>Nisbiy ustunlik (comparative advantage)</dt><dd>Mahsulotning muqobil xarajati boshqaga nisbatan pastligi.</dd><dt>Narxni qabul qiluvchi (price taker)</dt><dd>Jahon narxini o‘z harakati bilan sezilarli o‘zgartirmaydigan ishtirokchi.</dd><dt>CS / PS / TS</dt><dd>Iste’molchi yutug‘i / ishlab chiqaruvchi yutug‘i / jami yutuq. Soliq bo‘lsa TS ga davlat tushumi, subsidiya bo‘lsa davlat xarajati ham qo‘shiladi.</dd><dt>Sof yo‘qotish (deadweight loss, DWL)</dt><dd>Buzilgan ishlab chiqarish yoki yo‘qolgan foydali almashinuv sabab hech kim olmagan yutuq.</dd><dt>Kvota rentasi (quota rent)</dt><dd>Import huquqi egasining ichki va jahon narxlari farqidan daromadi.</dd></dl></div>
<h3>Og‘zaki javobni shu tartibda tuzing</h3>
<ol class="step-list"><li>Savdosiz muvozanat P₀ ni va jahon narxi Pᵥ ni taqqoslang; kichik mamlakat farazini ayting.</li><li>Eksport yoki import yo‘nalishini aniqlang; ishlab chiqarish, iste’mol va ularning farqini ko‘rsating.</li><li>CS va PS maydonlari bilan kim yutishi va kim zarar ko‘rishini tushuntiring; jami sof foydani ajrating.</li><li>Tarifni qo‘shib, xaridor zararini ishlab chiqaruvchi foydasi, davlat tushumi va ikkita DWL ga ajrating.</li><li>Kvotada rentaning kimga tegishini, qo‘shimcha savdo foydalarini va beshta himoya dalilining cheklovlarini ayting.</li><li>Samaradorlik bilan taqsimotni farqlang; zarar ko‘rgan odamga yordam avtomatik emasligini eslating.</li></ol>
<h3>Imtihondagi yetti xato</h3>
<ul><li>«Savdo ochilsa hamma darhol yutadi»: g‘oliblar va zarar ko‘ruvchilar bor.</li><li>«Eksport narxni tushiradi»: bu bobda eksportchi narxi savdosiz darajadan ko‘tariladi.</li><li>«Import barcha ichki ishlab chiqarishni tugatadi»: Qˢ musbat qolishi mumkin.</li><li>«Tarif tushumi t × eski import»: tarifdan keyingi import olinadi.</li><li>«Davlat tushumi ham sof yo‘qotish»: tushum qayta taqsimot, DWL hech kimga tegmaydi.</li><li>«Kvota foydasi davlatga tushadi»: ruxsatnoma kimga va qanday berilganiga bog‘liq.</li><li>«Ko‘proq eksport doim samarali»: eksport subsidiyasi savdoni oshirib, TS ni kamaytirishi mumkin.</li></ul>
<p class="recap">Bobning asosiy mantiqi: savdo narxni jahon imkoniyatlariga moslashtiradi, resurslarni nisbiy ustunlik tomon yo‘naltiradi va jami yutuq yaratadi. Shu yutuqning kimga tegishi hamda moslashishda kim qiynalishi siyosat muhokamasining muhim qismidir.</p>
''')

html='\n\n'.join(parts)+'\n'
visible=re.sub(r'<svg\b.*?</svg>','',html,flags=re.S)
visible=re.sub(r'<[^>]+>',' ',visible)
word_count=len(visible.split())
metadata={
    'id':'chapter-09',
    'title':'Xalqaro savdo: kim yutadi va kim zarar ko‘radi?',
    'englishTitle':'Application: International Trade',
    'lead':'Savdosiz narxni jahon narxi bilan taqqoslab, import va eksportni aniqlaymiz. Iste’molchi, ishlab chiqaruvchi va davlat yutuqlari orqali erkin savdo, tarif, kvota hamda subsidiyaning oqibatlarini tushuntiramiz.',
    'sourcePages':[169,187],
    'sections':sections,
    'sourceReviewCount':6,'sourceApplicationCount':10,'sourceQuickQuizCount':8,
    'reviewAnswered':6,'applicationsAnswered':10,'quickQuizAnswered':8,
    'topicCoverage':['Kirish','9-1','9-1a','9-1b','9-2','9-2a','9-2b','9-2c','9-2d','9-2e','9-3','9-3a','9-3b','9-3c','9-3d','9-3e','9-4','Figures 1–4','FYI: Import Quotas','Case Study: Trade Agreements and the World Trade Organization','Ask the Experts: Trade Deals and Tariffs','In the News: Trade as a Tool for Economic Development','Questions to Discuss 1–2','Chapter in a Nutshell','Key Concepts','Questions for Review 1–6','Problems and Applications 1–10','QuickQuiz 1–8','QuickQuiz Answers'],
    'wordCount':word_count,'diagramCount':diagram_count,'interactiveTypes':['trade'],'warnings':[]
}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'chapter-09.html').write_text(html,encoding='utf-8')
(OUT/'chapter-09.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'words':word_count,'sections':len(sections),'diagrams':diagram_count},ensure_ascii=False))
