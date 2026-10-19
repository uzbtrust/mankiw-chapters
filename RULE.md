# RULE.md — Mankiw o‘quv saytiga bob qo‘shish va tahrirlash qoidalari

Bu fayl **har qanday AI modeli** (Claude, ChatGPT, Gemini …) yoki odam uchun yagona qo‘llanma.
Maqsad: qaysi model ishlamasin, yangi bob mavjud 1–10-boblar bilan **bir xil ko‘rinish, bir xil tuzilish va bir xil
tushuntirish uslubida** chiqishi. Tushuntirish sifati modelga qarab farq qilishi mumkin, lekin quyidagi qoidalar
o‘zgarmaydi va ularning ko‘pini `scripts/build.py` avtomatik tekshiradi (buzilsa yig‘ish to‘xtaydi).

> **AI uchun:** ishni boshlashdan oldin shu faylni oxirigacha o‘qing. Qoidalar ziddiyatga kelsa, shu fayl ustun.
> Namuna sifatida `content/chapters/chapter-03.html` va `chapter-05.html` (ayniqsa `c5-s3` bo‘limi) ni oching.

---

## 0. Sayt nima va kim uchun

* N. Gregory Mankiw, *Principles of Economics* (10-nashr) kitobining o‘zbekcha (lotin) o‘quv sayti.
* O‘quvchi **og‘zaki universitet imtihoniga** tayyorlanadi, ko‘pincha **telefonda** o‘qiydi.
* Shuning uchun: kitobga sodiqlik + sodda o‘zbekcha + qisqa paragraflar + aniq formulalar + yechilgan mashqlar.
* Sayt: <https://mankiw-chapters.vercel.app> · Kod: <https://github.com/uzbtrust/mankiw-chapters>.
* Mavjud 1–10-boblarni andozaga keltirish va push qilish tartibi: **`TUGATISH.md`**.
* Kitob PDF loyiha egasidan (Telegram) olinadi va **loyiha ildiziga** (`./*.pdf`) qo‘yiladi; git’ga kirmaydi.

## 1. Papkalar va qaysi faylga tegish mumkin

| Yo‘l | Nima | Bob qo‘shishda |
|---|---|---|
| `content/chapters/chapter-NN.html` | Bob matni (HTML bo‘lagi) | **yaratiladi** |
| `content/chapters/chapter-NN.json` | Bob metama’lumoti | **yaratiladi** |
| `content/course.json` | Qismlar (I QISM …) va qaysi bob qaysi qismda | **yangilanadi** |
| `reference/source-text/chapter-NN.txt` | Kitobdan ajratilgan matn (git’ga kirmaydi) | yaratiladi |
| `./*.pdf` (loyiha ildizi) | Kitob PDF (git’ga kirmaydi) | o‘qiladi |
| `src/` | Dizayn: CSS, JS, HTML qismlari | **tegilmaydi** (§9) |
| `scripts/build.py` | Yig‘ish + qoidalarni tekshirish | tegilmaydi |
| `dist/`, `outputs/`, `build/` | Avtomatik natija | **hech qachon qo‘lda tahrirlanmaydi** |

Bob soni avtomatik aniqlanadi: `chapter-01 … chapter-NN` uzluksiz bo‘lsa bas. Bosh sahifadagi "10 bob",
qidiruv matni, "05 / 12" kabi joylar o‘zi yangilanadi.

## 2. Yangi bob qo‘shish — ish tartibi (qadam-baqadam)

1. **Kitobdan ajratish.**
   ```bash
   node scripts/py.cjs scripts/extract_chapter.py ./KITOB.pdf --find "Chapter 11"     # bob boshlanish sahifasi
   node scripts/py.cjs scripts/extract_chapter.py ./KITOB.pdf --chapter 11 --pages 231-252 --offset -2
   ```
   Natija: `reference/source-text/chapter-11.txt` (har sahifa `=== KITOB SAHIFASI …; PDF SAHIFASI … ===` bilan).
   Butun matnni bo‘lib-bo‘lib, **qisqartirmasdan** o‘qing.
2. **Inventar tuzing** (yozishdan oldin, o‘zingiz uchun ro‘yxat):
   * kitob bo‘limlari va raqamlari: `11-1`, `11-1a`, `11-1b` …;
   * Case Study, In the News, FYI, Ask the Experts qutilari;
   * barcha Figure va Table lar (raqami, nima ko‘rsatadi);
   * QuickQuiz savollari (odatda 2–3 blok, jami soni), Questions for Review soni, Problems and Applications soni;
   * Key Concepts ro‘yxati, Summary.
3. **`chapter-NN.html` ni yozing** — §4 skelet, §5 komponentlar, §3 uslub, §6 formulalar, §7 chizmalar.
4. **`chapter-NN.json` ni yozing** — §8.
5. **`content/course.json`** — bobni tegishli qismga qo‘shing (yangi qism kerak bo‘lsa yangi obyekt).
6. **Yig‘ing va xatolarni tuzating:**
   ```bash
   npm install          # bir marta
   npm run check -- 11  # faqat shu bob: barcha buzilgan qoidalar ro‘yxati
   npm run status       # barcha boblar: qaysi biri tayyor
   npm run build        # butun sayt; xato bo‘lsa — xabar aniq qaysi qoida buzilganini aytadi
   npm run dev          # http://localhost:4173 — telefon kengligida (375 px) ham ko‘ring
   ```
7. **§11 yakuniy tekshiruv ro‘yxati** dan o‘ting.
8. **Chiqarish:** `git add` → `git commit` → `git push` (TUGATISH.md §5–§6). Deploy’ni faqat loyiha egasi qiladi (`npm run deploy`).

## 3. Tushuntirish uslubi (o‘zgarmas qoidalar)

**Ohang:** do‘stona domla — sodda, aniq, xotirjam. Kitobni tarjima qilmang, **o‘z so‘zingiz bilan tushuntiring**.

1. **Bitta paragraf — bitta fikr.** Paragraf **≤ 80 so‘z** (build tekshiradi), ideal 2–4 gap.
2. **Gap qisqa:** odatda ≤ 20–25 so‘z. Uzun gapni ikkiga bo‘ling.
3. **Har bir bo‘lim tartibi:** sodda ta’rif → nega/qanday ishlaydi → `Oddiy misol.` (mahalliy hayotdan:
   bozor, non, taksi, telefon, talaba) → kitobdagi misol/grafik → `Keng tarqalgan xato.` → (ixtiyoriy) `Qisqasi.`
4. **Hisob-kitob hech qachon paragraf ichida uzun zanjir bo‘lmaydi.** 2 tadan ortiq hisob bo‘lsa:
   formula → `ol.step-list` (har qadam: sarlavha + bitta hisob) yoki jadval. Namuna: `chapter-05.html#c5-s3`.
5. **Formula har doim LaTeX** (§6) va katta formula alohida `.formula` kartada, belgilar izohi bilan.
6. **Raqamli ma’lumot ≥ 2 qator bo‘lsa — jadval** (`.table-wrap > table`, ustun nomida birlik: "Narx ($)").
7. **Ikki tushuncha solishtirilsa** — `.comparison` yoki jadval (masalan, siljish vs chiziq bo‘ylab harakat).
8. **Inglizcha atama** birinchi uchraganda qavsda: *talab elastikligi (price elasticity of demand)*. Keyin faqat o‘zbekcha.
9. **Kitobdagi asl misollar** aniq belgilanadi: "Kitobdagi misol:", "Manbadagi holat:". O‘zingiz o‘ylab topgan misol —
   `Oddiy misol.` Ikkalasini aralashtirmang.
10. **Tarixiy raqamlar** (yil, statistika) "hozirgi" deb berilmaydi: "kitob yozilgan paytdagi (2019) ma’lumot".
11. **Yangi statistika, soxta manba, "100% to‘g‘ri" kabi da’vo qo‘shilmaydi.**
12. **Mashqlar:** barcha QuickQuiz, Questions for Review va Problems and Applications savollari **to‘liq yechiladi**.
    Kitobdagi aniq raqamlar saqlanadi. Grafik talab qiladigan savolga chizma + izoh.
13. **QuickQuiz javobi:** harf **va** variant matni, keyin **nega**: `To‘g‘ri javob: b) narx oshadi.` + 1–3 gap sabab.
14. **Og‘zaki imtihon bo‘limi** har bobda: eslab qolish ro‘yxati, javob rejasi, 5–8 tuzoq.

**Til:** o‘zbek lotin. `o‘` va `g‘` da **U+2018** (‘) belgisi, tutuq belgisi **U+2019** (’): *ta’sir, ma’no*.
Kirill harf yo‘q (build tekshiradi). Pul: `$4`, o‘nli kasr vergul bilan: `0,66`. Minus: `−` (U+2212). Oraliq: `1–3`.

## 4. Bob skeleti (qat’iy tartib — build tekshiradi)

Fayl — **faqat HTML bo‘lagi** (`<html>`, `<head>`, `<body>`, `<style>`, `<script>`, `on*=` atributlari taqiqlanadi).
Ildizda faqat `<section class="lesson-section">` lar, ichma-ich section yo‘q.

| # | `id` | `section-kicker` | `h2` | Mazmuni |
|---|---|---|---|---|
| 1 | `cN-s1` | `Kirish · Qisqa mavzu` | Bobning markaziy savoli | Muammo + hayotiy misol |
| 2…K | `cN-s2` … `cN-sK` | `N-1a · Qisqa mavzu` (kitob raqami) | Savol yoki aniq fikr | Kitobning har bir bo‘limi, Case Study, In the News |
| K+1 | `cN-terms` | `Atamalar` | `Asosiy atamalar` | `.key-concepts > dl` (§5.10) |
| K+2 | `cN-quick` | `QuickQuiz · 8 savol` | `Tezkor savollar: javob va sabab` | faqat `data-kind="quick"` |
| K+3 | `cN-review` | `Takrorlash · 7 savol` | `Takrorlash savollari` | faqat `data-kind="review"` |
| K+4 | `cN-apps` | `Masalalar · 10 topshiriq` | `Masalalar va qo‘llash` | faqat `data-kind="application"` |
| K+5 | `cN-oral` | `Og‘zaki imtihon` | `Og‘zaki javob rejasi va tuzoqlar` | `ul.recap` + `ol.step-list` + `div.warning` |

* `N` — bob raqami (`c11-s1`). Dars bo‘limlari `s1` dan boshlab **uzluksiz**; odatda 8–14 ta.
* Kicker chap qismi: kitob raqami `11-1`, `11-1a`, `11-2b–c` yoki `Kirish` / `Yakun` / `Ilova`; keyin ` · ` va ≤ 60 belgili mavzu.
  Kitob qutilari ham kitob raqami bilan: `11-2a · Manbadagi holat` , `11-3 · Yangilikda`.
* Kickerdagi savollar soni (`8 savol`) haqiqiy `<details>` soniga teng bo‘lishi shart.
* Dars bo‘limlarida `<details class="answer">` bo‘lmaydi — savollar faqat oxirgi uch bo‘limda.
* Har section boshlanishi aynan: `<section class="lesson-section" id="…"><div class="section-kicker">…</div><h2>…</h2>`.

## 5. Komponentlar (faqat shular — yangi class o‘ylab topilmaydi)

Har bir komponent dizayni `src/css/50-content.css` da tayyor. HTML aynan shunday yoziladi.

**5.1 Paragraf va sarlavhalar** — `<p>` (≤ 80 so‘z), bo‘lim ichida `<h3>`, kerak bo‘lsa `<h4>`. Muhim so‘z `<strong>`.

**5.2 Oddiy misol** (har dars bo‘limida kamida bittasi tavsiya etiladi)
```html
<div class="callout"><strong>Oddiy misol.</strong> Non narxi 10% oshsa ham, oila nonni deyarli kamaytirmaydi …</div>
```

**5.3 Formula kartasi** (§6)
```html
<div class="formula"><p class="formula-title">Talabning narx elastikligi</p>\[ E_d = \left| \frac{\%\Delta Q_d}{\%\Delta P} \right| \]<ul class="formula-legend"><li>\(E_d\) — talabning narx elastikligi</li><li>\(\%\Delta Q_d\) — talab miqdorining foiz o‘zgarishi</li></ul></div>
```

**5.4 Bosqichma-bosqich hisob / jarayon**
```html
<ol class="step-list"><li><strong>O‘rtacha narx</strong>\( (4 + 6)/2 = 5 \) dollar.</li><li><strong>Narxning foiz o‘zgarishi</strong>\( \dfrac{6-4}{5} = 0{,}40 \), ya’ni 40%.</li></ol>
```
Har `li`: `<strong>Qisqa sarlavha</strong>` + bitta hisob/fikr. Matnli jarayonda ham shunday (masalan, "1. Qaysi chiziq siljiydi?").

**5.5 Jadval**
```html
<div class="table-wrap"><table><thead><tr><th>Yo‘nalish</th><th>Narx o‘zgarishi</th><th>Miqdor o‘zgarishi</th><th>Elastiklik</th></tr></thead><tbody><tr><td>A → B</td><td>+50%</td><td>−33%</td><td>≈ 0,66</td></tr></tbody></table></div>
```
`thead` + `tbody` majburiy, `colspan`/`rowspan` ishlatmang. 4+ ustunli jadval telefonda avtomatik kartaga aylanadi
(birinchi ustun — karta sarlavhasi), shuning uchun birinchi ustunga qator nomini yozing.

**5.6 Taqqoslash**
```html
<div class="comparison"><div><h4>Chiziq bo‘ylab harakat</h4><p>Faqat tovarning o‘z narxi o‘zgaradi …</p></div><div><h4>Chiziqning siljishi</h4><p>Narxdan boshqa omil o‘zgaradi …</p></div></div>
```
Bir nechta teng tushuncha (masalan, 4 determinant) — `<div class="concept-grid">` + har biri `<div><h4>…</h4><p>…</p></div>`.

**5.7 Kitobdagi misol (uzunroq)** — `<div class="example"><h4>Kitobdagi misol: …</h4><p>…</p></div>`

**5.8 Ogohlantirish va xulosa**
```html
<div class="warning"><strong>Keng tarqalgan xato.</strong> Talab va talab miqdorini bir narsa deb o‘ylash …</div>
<div class="recap"><strong>Qisqasi.</strong> Bir-ikki gapda bo‘limning asosiy fikri.</div>
```

Kartalar **faqat** shu yorliqlar bilan boshlanadi (build tekshiradi):

| Komponent | Ruxsat etilgan birinchi `<strong>` |
|---|---|
| `div.callout` | `Oddiy misol.` · `Muhim.` · `Eslatma.` |
| `div.warning` | `Keng tarqalgan xato.` · `Imtihon tuzoqlari.` · `Diqqat.` |
| `div.recap` | `Qisqasi.` (`ul.recap` — yorliqsiz ro‘yxat) |

**5.9 Manba izohi** (kichik kulrang eslatma) — `<p class="source-note"><strong>Manba:</strong> 2019-yil ma’lumoti, kitob 5-2 bo‘limi.</p>`

**5.10 Atamalar** (`cN-terms` ichida, kitobning Key Concepts ro‘yxati to‘liq, ≥ 5 ta)
```html
<div class="key-concepts"><dl><dt>Talabning narx elastikligi <span class="en">price elasticity of demand</span></dt><dd>Narx 1% o‘zgarganda talab miqdori necha foiz o‘zgarishini ko‘rsatadi.</dd></dl></div>
```
Har `dt` da `<span class="en">`, har `dt` dan keyin bitta `dd` (bir gapli ta’rif).

**5.11 Savol-javob** (uch tur: `quick`, `review`, `application`; raqam `data-q` tur ichida takrorlanmaydi)
```html
<details class="answer" data-kind="review" data-q="1"><summary><span class="q-number">01</span> Elastiklik nimani o‘lchaydi?</summary><div class="answer-body"><p><strong>Qisqa javob.</strong> …</p><p>Izoh …</p></div></details>
```
* `summary` — savolning o‘zbekcha qisqa mazmuni (to‘liq shart javob ichida bo‘lishi mumkin).
* QuickQuiz: `<p><strong>To‘g‘ri javob: c) variant matni.</strong> Sabab …</p>`
* Masala: kerak bo‘lsa `formula`, `step-list`, `table-wrap`, `figure.diagram` javob ichida ham ishlatiladi.
  Ko‘p qismli masala: `<h4>a)</h4>` … `<h4>b)</h4>`.

**5.12 Og‘zaki imtihon bo‘limi** (`cN-oral`)
```html
<ul class="recap"><li>Eslab qolish kerak bo‘lgan 5–8 asosiy fikr …</li></ul>
<h3>Og‘zaki javob rejasi</h3><ol class="step-list"><li><strong>Ta’rif</strong>…</li></ol>
<div class="warning"><strong>Imtihon tuzoqlari.</strong><ul><li>…</li></ul></div>
```

**5.13 Interaktiv model** (ixtiyoriy, bobda ko‘pi bilan bitta)
```html
<div class="interactive" data-interactive="market"><p>Nimani o‘zgartirish va nimani kuzatish kerakligi.</p></div>
```
Mavjud turlar: `opportunity ppf advantage market elasticity controls welfare tax trade externality`
(`src/js/simulations.js`). Yangi bob uchun mos tur bo‘lmasa — **qo‘ymang** (yangi tur faqat JS bilan qo‘shiladi, §9).

## 6. Formulalar — LaTeX

Yig‘ish vaqtida LaTeX → MathML (Temml) ga aylanadi: brauzer o‘zi chiroyli chizadi, sahifaga JS qo‘shilmaydi.

* **Katta formula:** `\[ … \]` — faqat `.formula` ichida (yoki `answer-body` ichidagi `.formula`).
* **Matn ichidagi kichik ifoda:** `\( … \)` — belgilar (`\(Q_d\)`), qisqa tenglik (`\(P \times Q\)`).
* `.formula` ichida oddiy matn formula **taqiqlangan**; `<sub>`, `<sup>` ham taqiqlangan — hammasi LaTeX (build tekshiradi).
* Foiz: `\%`. O‘nli vergul: `0{,}40`. Minus: oddiy `-`. Ko‘paytma: `\times`. Taxminan: `\approx`. Cheksiz: `\infty`.
* O‘zbekcha so‘z formulada: `\text{Tushum} = P \times Q`.
* Kasr: displayda `\frac`, matn ichida `\dfrac` faqat `step-list` da; oddiy paragrafda kasrli ifoda bo‘lsa — display qiling.
* Modul (minus tashlanadi): `\left| … \right|`. Delta: `\Delta`.
* HTML ichida `<` va `>` ni `&lt;` va `&gt;` deb yozing (`\(E_d &gt; 1\)`).
* Formula xato bo‘lsa build aniq qaysi bob va qaysi ifoda ekanini aytadi.

## 7. Chizmalar (inline SVG)

```html
<figure class="diagram"><svg viewBox="0 0 640 360" width="100%" role="img" aria-labelledby="c11-f1-title c11-f1-desc"><title id="c11-f1-title">…</title><desc id="c11-f1-desc">…</desc> … </svg><figcaption>Chizma nimani ko‘rsatishi va qanday o‘qilishi, 1–3 gap.</figcaption></figure>
```
* `viewBox` kengligi 640 (keng chizma 960), balandlik zarurat bo‘yicha; `width="100%"`, qattiq px o‘lcham yo‘q.
* `title` + `desc` + `figcaption` majburiy; ID lar `cN-` bilan boshlanadi va bob ichida yagona.
* Narx — vertikal o‘q, miqdor — gorizontal. Egri chiziq nomi chiziq yonida yoziladi (D, S, D₂ …).
* Aniq raqamli misolda nuqtalar haqiqiy miqyosda chiziladi.
* Matn: `<g font-family="Arial, sans-serif" font-size="15" fill="#263c34">`.
* **Faqat shu ranglar** (CSS ularni yorug‘/qorong‘u rejimga o‘zi moslaydi — boshqa rang ishlatmang):

| Ma’no | Rang | Qayerda |
|---|---|---|
| Talab chizig‘i / asosiy chiziq | `#17695f` | `stroke`, nuqta `fill`, yorliq `text fill` |
| Taklif chizig‘i / ikkinchi chiziq | `#c06843` | xuddi shunday |
| Ikkinchi darajali talab (D₂, eski holat) | `#3f968a` | `stroke` |
| Ikkinchi darajali taklif (S₂) | `#a14e30` | `stroke`, `text fill` |
| Ijtimoiy egri chiziq | `#7d86a0` | `stroke`, `text fill` |
| O‘qlar, belgilar | `#81918b` (`stroke-width="2"`); uzilgan yordamchi chiziq: `#81918b` + `stroke-dasharray="6 6"` | |
| Matn | `#263c34` | |
| Iste’molchi ortiqchaligi | `#d4e9df` (och `#e0eee7`, to‘q `#b5d9cc`) | `polygon fill` |
| Ishlab chiqaruvchi ortiqchaligi | `#f2dacf` (och `#f7e8df`, to‘q `#e6bfa9`) | `polygon fill` |
| Sof yo‘qotish (deadweight loss) | `#f0bdb2` | `polygon fill` |
| Soliq tushumi | `#dec878` | `polygon fill` |
| Yutuq (savdodan foyda) | `#cbe7dd` | `polygon fill` |
| Neytral maydon | `#edf0ee` | `polygon fill` |

## 8. `chapter-NN.json`

```json
{
  "id": 11,
  "title": "Bobning o‘zbekcha nomi",
  "englishTitle": "Chapter title in English",
  "lead": "1–2 gap: bob nimani o‘rgatadi.",
  "sourcePages": [229, 250],
  "sections": [{ "id": "c11-s1", "title": "h2 matni bilan AYNAN bir xil", "sourceTopics": ["11-1"] }],
  "sourceReviewCount": 7, "sourceApplicationCount": 10, "sourceQuickQuizCount": 8,
  "reviewAnswered": 7, "applicationsAnswered": 10, "quickQuizAnswered": 8,
  "topicCoverage": ["11-1", "11-1a", "Case Study: …"],
  "wordCount": 0, "diagramCount": 0, "interactiveTypes": [],
  "warnings": ["Tarixiy raqamlar haqida eslatma va hokazo"]
}
```
* `sections` — HTML dagi barcha section lar, o‘sha tartibda; `title` = `h2` matni (build tekshiradi).
* `source…Count` — kitobdagi haqiqiy son; HTML dagi `<details>` soni shunga teng bo‘lishi shart.
* `wordCount`, `diagramCount`, `interactiveTypes` ni build o‘zi hisoblaydi (0 yoki [] qoldirsangiz bo‘ladi).

## 9. Dizayn tizimi (o‘zgarmas)

Dizayn tayyor va barcha boblar uchun **bir xil**. Bob qo‘shishda `src/` ga tegilmaydi — ko‘rinish faqat
§5 komponentlaridan keladi. Dizaynni o‘zgartirish kerak bo‘lsa, butun sayt uchun `docs/DESIGN.md` ga amal qiling.

* **Uslub:** "Apple, sokin" — ko‘p bo‘sh joy, katta sarlavhalar, kulrang kartalar, chegara chiziqlari kam.
* **Shrift:** tizim San Francisco (`-apple-system`); formulalar — tizim matematik shrifti (STIX Two Math).
  Veb-shrift, tashqi CDN, emoji, ikon-shrift yo‘q.
* **Rang:** bitta urg‘u rangi (Apple ko‘k). Talab = ko‘k, taklif = to‘q sariq — faqat ma’no uchun.
  Yorug‘ va qorong‘u rejim avtomatik (tokenlar `src/css/00-tokens.css`).
* **Harakat:** GSAP, sokin va qisqa; `prefers-reduced-motion` hurmat qilinadi. Kontent JS siz ham ko‘rinadi.
* **Telefon birinchi:** 375 px da gorizontal surilish yo‘q; keng chizma o‘z kartasi ichida suriladi,
  keng jadval kartaga aylanadi.
* **Yuklash:** boblar, modellar va qidiruv kerak bo‘lganda yuklanadi; internetsiz yagona HTML ham yig‘iladi.
* Yangi komponent yoki interaktiv tur kerak bo‘lsa: CSS `src/css/50-content.css`, JS `src/js/simulations.js`,
  qoidani shu faylga (§5) qo‘shing va build tekshiruvini `scripts/build.py` → `check_standard` da yangilang.

## 10. Build nimani tekshiradi

`npm run build` quyidagilardan biri buzilsa to‘xtaydi va sababini yozadi:

* bo‘limlar tartibi va ID lari (§4), kicker va h2 shakli, JSON `sections` bilan moslik;
* savollar soni (`source…Count` = `<details>` soni), raqamlar takrorlanmasligi, savollar to‘g‘ri bo‘limda;
* `cN-terms` da `dl` (≥ 5, har `dt` da `.en`), `cN-oral` da `recap` + `step-list` + `warning`;
* `.formula` ichida LaTeX, `<sub>/<sup>` yo‘qligi, LaTeX sintaksisi;
* jadvalda `thead/tbody` va `.table-wrap`; paragraf ≤ 80 so‘z;
* kirill harf yo‘qligi, teglar balansi, takroriy ID yo‘qligi, taqiqlangan teglar.

* `npm run check -- 11` — faqat 11-bobni tekshiradi va **barcha** muammolar ro‘yxatini chiqaradi (hech narsa yozmaydi).
  Bob ustida ishlayotganda shuni ishlating; "xato yo‘q ✓" chiqquncha tuzating.
* `npm run status` — har bir bob: `✓ tayyor` yoki nechta muammo qolgan.
* `node scripts/py.cjs scripts/build.py --lenient` — andoza xatolarini ogohlantirishga aylantiradi (faqat ish jarayonida).

## 11. Yakuniy tekshiruv ro‘yxati

- [ ] `npm run build` xatosiz.
- [ ] Kitobning har bir bo‘limi, qutisi, muhim chizmasi qamrab olingan (inventar bilan solishtiring).
- [ ] Barcha QuickQuiz / Review / Problems savollari javoblangan, raqamlar kitob bilan bir xil.
- [ ] Hisob-kitoblar qayta tekshirilgan (foiz, elastiklik, ortiqchalik maydoni, soliq yuki, imkoniyat xarajati).
- [ ] Telefon (375 px) da: formula sig‘adi, jadval o‘qiladi, chizma ko‘rinadi, gorizontal surilish yo‘q.
- [ ] Yorug‘ va qorong‘u rejimda o‘qiladi.
- [ ] Inglizcha atamalar faqat birinchi marta qavsda; `o‘ g‘` U+2018 bilan.

## 12. Chiqarish (Vercel va GitHub)

* GitHub: <https://github.com/uzbtrust/mankiw-chapters> (ochiq). kitob PDF (`./*.pdf`) va `reference/source-text`
  git’ga kirmaydi (mualliflik huquqi) — PDF’ni loyiha egasidan (Telegram) olib, loyiha ildiziga qo‘ying.
* Yordamchilar (do‘stlar) faqat o‘z bobini push qiladi — tartib `TUGATISH.md` da (bir martalik GitHub device login).
* Vercel loyihasi: `mankiw-chapters` (`.vercel/project.json`, faqat egasining kompyuterida).
  Egasi: `git pull` → `npm run build` → `npm run deploy` → <https://mankiw-chapters.vercel.app>.
* Windows / macOS / Linux: `npm run …` buyruqlari Python’ni o‘zi topadi (`scripts/py.cjs`); to‘g‘ridan-to‘g‘ri chaqirish:
  `node scripts/py.cjs scripts/build.py --check 11`.

## 13. Yangi AI uchun tayyor topshiriq matni

> Bu loyihadagi `RULE.md` ni to‘liq o‘qi va unga qat’iy amal qil. Namuna: `content/chapters/chapter-03.html`,
> `chapter-05.html` (`c5-s3`). Kitob: loyiha ildizidagi `./<fayl>.pdf`. Vazifa: 11–20-boblarni qo‘sh — har bob uchun
> `scripts/extract_chapter.py` bilan matnni ajrat, inventar tuz, `chapter-NN.html` va `.json` ni §3–§8 bo‘yicha yoz,
> `content/course.json` ni yangila, `npm run build` xatosiz o‘tguncha tuzat, §11 ro‘yxatidan o‘t.
> `src/`, `scripts/`, `dist/` ga tegma.
