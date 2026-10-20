# BOB_QOSHISH.md — kitobdan yangi bob(lar) qo‘shish

**Odam uchun (bir marta o‘qing):**

```bash
git clone https://github.com/uzbtrust/mankiw-chapters.git
cd mankiw-chapters
claude
```

Kerakli boblar bor **kitob PDF faylini** shu `mankiw-chapters` papkasining o‘ziga (README.md yoniga) qo‘ying.
Claude Code’da modelni eng kuchlisiga qo‘yib yozing:

> **BOB_QOSHISH.md ni o‘qi va kitobdan 11, 12, 13-boblarni qo‘sh**

Claude kerakli dasturlarni o‘zi o‘rnatadi. Keyin PDF’dan boblarni topadi, har birini qolgan boblar uslubida yozib
tekshiradi va GitHub’ga yuboradi. GitHub kod so‘rasa, kodni loyiha egasi telefonida kiritadi. Oxirida Claude
saytni Vercel’ga chiqarish-chiqarmaslikni so‘raydi.

Sessiya uzilib qolsa (limit, kompyuter o‘chdi), yangi sessiyada shunday yozing:
**`BOB_QOSHISH.md bo‘yicha davom et`**.

---

## AI uchun: vazifa va qat’iy qoidalar

Sen o‘zbekcha Mankiw o‘quv saytiga foydalanuvchi aytgan har bir bob uchun ikki fayl yaratasan:
`content/chapters/chapter-NN.html` va `chapter-NN.json`. Bobni `content/course.json` ga ulaysan, tekshirasan va
GitHub’ga push qilasan.

**Bob tayyor hisoblanadi, qachonki:**
* `npm run check -- N` va to‘liq `npm run build` xatosiz o‘tsa;
* §6 dagi sifat ro‘yxatining hammasi bajarilgan bo‘lsa;
* commit `main` ga push qilingan bo‘lsa.

Sifat o‘lchovi — mavjud 1–10-boblar. Yangi bob ular yonida begona ko‘rinmasin.

1. **Ishni o‘zing qil, subagent (Agent / Task) ishlatma.** Boblar ketma-ket bajariladi (11 → 12 → 13). Parallel
   agentlar limitni tez tugatadi.
2. **Tegish mumkin bo‘lgan fayllar:**
   * yangi `chapter-NN.html` va `chapter-NN.json`;
   * `content/course.json`.

   `src/`, `scripts/`, `RULE.md`, `docs/`, `package.json` va mavjud boblarga tegma. Qoida xato yoki bajarib
   bo‘lmaydigan tuyulsa, uni o‘zgartirma — yakuniy hisobotda yoz.
3. **Kitob PDF va `reference/source-text/` hech qachon git’ga qo‘shilmaydi** (mualliflik huquqi, ochiq repo).
   `.gitignore` buni to‘sadi. `git add -A` / `git add .` ishlatma, fayllarni nomi bilan qo‘sh.
4. **Yetishmayotgan dasturni so‘ramasdan o‘zing o‘rnat** (§0). Foydalanuvchidan faqat shularni so‘raysan:
   * PDF yo‘q yoki kerakli bob PDF’da yo‘q (§3);
   * boblar ketma-ketligida bo‘shliq bor (§2);
   * GitHub kodi kiritilganini tasdiqlash (§8);
   * Vercel’ga chiqarish (§9);
   * parol yoki tugma bosishni talab qiladigan o‘rnatish.
5. **Kitobdan tashqariga chiqma.** Yangi statistika, soxta manba, o‘ylab topilgan "kitobdagi misol" yo‘q.
   O‘zing o‘ylagan misol faqat `Oddiy misol.` kartasida bo‘ladi.
6. **Ish yo‘qolmasin:**
   * holat faylini yuritib bor (§2.4);
   * har 3–4 bo‘limdan keyin lokal commit qil;
   * har tugagan bobdan keyin push qil.
7. Foydalanuvchi bilan **o‘zbek tilida**, qisqa gaplash.

---

## 0. Kerakli dasturlar — tekshir va yetishmaganini o‘rnat

Kerak: `git`, `node` ≥ 18 (+ `npm`), Python ≥ 3.8, `gh` (GitHub CLI). Ixtiyoriy: `pdftotext` (poppler).

```bash
git --version; node --version; npm --version; gh --version
python3 --version || python --version || py -3 --version
```

**Windows** (Claude Code Git Bash’da ishlaydi). Yetishmaganini `winget` bilan o‘rnat:

```bash
winget install --id OpenJS.NodeJS.LTS -e --silent --accept-source-agreements --accept-package-agreements
winget install --id GitHub.cli        -e --silent --accept-source-agreements --accept-package-agreements
winget install --id Python.Python.3.12 -e --silent --accept-source-agreements --accept-package-agreements
export PATH="$PATH:/c/Program Files/nodejs:/c/Program Files/GitHub CLI:$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts"
```
`winget` yo‘q bo‘lsa (eski Windows), o‘rnatuvchini yuklab, jim rejimda o‘rnat:
* Node: <https://nodejs.org> MSI;
* gh: <https://cli.github.com> MSI;
* Python: <https://python.org>, `python-installer.exe /quiet PrependPath=1`.

Windows’da Python buyrug‘i `py -3` bo‘lishi mumkin — `npm run …` buni o‘zi topadi (`scripts/py.cjs`).

**macOS:**

```bash
xcode-select -p >/dev/null 2>&1 || xcode-select --install   # git va python3 shu bilan keladi
```
`xcode-select --install` oyna ochadi. Foydalanuvchiga "Install tugmasini bosing" deb ayt va tugashini kut.
Keyin `brew` bo‘lsa: `brew install node gh poppler`. `brew` bo‘lmasa (parolsiz yo‘l):

```bash
curl -fsSL -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm install --lts
mkdir -p ~/.local/bin && cd /tmp
ARCH=$( [ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64 )
URL=$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest | grep -o "https://[^\"]*macOS_${ARCH}.zip" | head -1)
curl -fsSL -o gh.zip "$URL" && unzip -oq gh.zip && cp gh_*/bin/gh ~/.local/bin/ && cd -
export PATH="$HOME/.local/bin:$PATH"
```

**Linux (Debian/Ubuntu):** `sudo apt-get update && sudo apt-get install -y git nodejs npm python3 gh poppler-utils`.

**Loyiha kutubxonalari** (har doim, repo papkasida):

```bash
npm install
```

PDF o‘qish uchun `pdftotext` bo‘lmasa: `python3 -m pip install --user pypdf` (Windows: `py -3 -m pip install --user pypdf`).
Skript qaysi biri borligini o‘zi aniqlaydi.

## 1. O‘qish (majburiy, oxirigacha)

1. **`RULE.md`** — asosiy shartnoma:
   * tushuntirish uslubi (§3), bob skeleti (§4), komponentlar (§5);
   * LaTeX (§6), chizmalar (§7), JSON (§8), yakuniy ro‘yxat (§11).
2. **`docs/DESIGN.md`** §1–§2 — sayt kim uchun va nega shunday ko‘rinadi.
3. **Namuna boblar** — HTML’ni ochib, qanday yozilganini ko‘r:
   * `chapter-05.html` (`c5-s3`) — formula kartasi, izoh, jadval, bosqichli hisob, `Oddiy misol.`, `Keng tarqalgan xato.`;
   * `chapter-10.html` — eng so‘nggi bob: davlat sektori mavzusi, javoblar, og‘zaki bo‘lim;
   * `chapter-07.html`, `chapter-04.html` — ko‘p chizmali boblar: SVG namunalari.

Har yangi bobni boshlashdan oldin RULE.md §3–§7 ni **qayta o‘qi**: uzun ishda kontekst siqiladi va qoidalar
"esdan chiqadi".

## 2. So‘rovni tushunish va tayyorgarlik

1. **Bob raqamlari** foydalanuvchi xabaridan olinadi: "11, 12, 13", "11–13", "14-bob".
2. **Holat:**
   ```bash
   git pull --rebase origin main
   npm install
   npm run status          # mavjud boblar va ularning holati
   ```
3. **Ketma-ketlik.** Boblar `chapter-01 … chapter-NN` uzluksiz bo‘lishi shart (build tekshiradi). Mavjud oxirgi bob
   `M` bo‘lsa:
   * so‘ralgan bob allaqachon bor bo‘lsa — foydalanuvchiga ayt va uni o‘tkazib yubor. Faqat aniq "qayta yoz" desa,
     qayta yoz;
   * bo‘shliq bo‘lsa (masalan, `M = 10`, so‘rov "14") — `AskUserQuestion`: *"Boblar uzluksiz bo‘lishi kerak.
     11–13 ham qo‘shilsinmi?"*. Variantlar: "Ha, 11–14 hammasi" / "Yo‘q, to‘xta".
   * Tartib har doim o‘sib boradi: 11, keyin 12, keyin 13.
4. **Holat fayli** — `build/bob-qoshish-holat.md` (git’ga kirmaydi). Har bob boshida va har 3–4 bo‘limda yangila:
   ```
   So‘rov: 11, 12, 13
   11: tayyor, push qilindi (abc1234)
   12: yozilmoqda — c12-s1…c12-s6 tayyor, keyingisi: c12-s7 (12-3a)
   13: kutmoqda
   ```
   Sessiya uzilib "davom et" deyilsa, shu fayl, `git log --oneline -10` va `npm run check -- N` bilan qayerdaligingni top.
5. **Commit muallifi** (bo‘lmasa):
   ```bash
   git config user.name  >/dev/null || git config user.name  "Mankiw yordamchi"
   git config user.email >/dev/null || git config user.email "yordamchi@users.noreply.github.com"
   ```
6. Foydalanuvchiga bir qatorda ayt: *"11, 12, 13-boblarni ketma-ket qo‘shaman (har biri tugagach GitHub’ga yuboraman)."*

## 3. Kitob PDF va bob matni

Kitob PDF **loyiha ildizida** turadi (`./*.pdf`). Bir nechta PDF bo‘lishi mumkin (masalan, "Chapters 1–10" va
to‘liq kitob).

1. **Qaysi PDF’da qaysi bob bor:**
   ```bash
   ls *.pdf
   node scripts/py.cjs scripts/extract_chapter.py "./<fayl>.pdf" --list
   ```
   Chiqish namunasi:
   `Bob 11: PDF 231-252 (kitob 211-232, offset -20)  Public Goods and Common Resources  [Part IV The Economics of the Public Sector]`.
   * PDF umuman yo‘q bo‘lsa — `AskUserQuestion`: *"Kitob PDF faylini (11-bob bor nusxasini) loyiha papkasiga qo‘ying"*.
     Variantlar: "Qo‘ydim" / "To‘xta".
   * Kerakli bob hech qaysi PDF’da yo‘q bo‘lsa (masalan, faqat 1–10-boblar fayli bor) — xuddi shunday so‘ra.
     **Kitobsiz yangi bob yozilmaydi.**
   * `--list` hech narsa topmasa (boshqa dizayndagi PDF), qo‘lda top va sahifalarni ber:
     `--find "Public Goods and Common Resources"` → `--chapter 11 --pages A-B --offset K`.
2. **Matnni ajrat:**
   ```bash
   node scripts/py.cjs scripts/extract_chapter.py "./<fayl>.pdf" --chapter 11
   ```
   Natija `reference/source-text/chapter-11.txt` ga yoziladi. Har sahifa
   `=== KITOB SAHIFASI 211; PDF SAHIFASI 231 ===` bilan boshlanadi. Bob nomi va qismi (`[Part …]`) ham chiqadi —
   ularni yozib ol.
3. **Matnni to‘liq o‘qi** — bo‘lib-bo‘lib, har sahifasini, qisqartirmasdan (Read: `offset`/`limit`). Bob oxirida
   quyidagi bloklar bor: `Chapter in a Nutshell`, `Key Concepts`, `Questions for Review`,
   `Problems and Applications` va `QuickQuiz Answers`.

## 4. Inventar va reja (yozishdan oldin)

`build/bob-NN-inventar.md` ga yoz. Bu faylsiz yozishni boshlama:

```
# Bob 11 — Public Goods and Common Resources (kitob s. 211–232) — Part IV
Bo‘limlar:  11-1 …, 11-1a …, 11-1b …, 11-2 …
Qutilar:    Case Study «…» (s. 215), In the News «…» (s. 220), Ask the Experts «…» (s. 224), FYI «…»
Rasmlar:    Figure 1 — … (s. 213); Table 1 — … (s. 214)
QuickQuiz:  3 blok, jami 9 savol; javoblar: 1-c, 2-a, …
Key Concepts (to‘liq): …
Review: 6 ta.  Problems: 8 ta.
Nutshell:   …
REJA:
  c11-s1  Kirish · …              ← bob kirish hikoyasi
  c11-s2  11-1a · …               ← 11-1, 11-1a, Figure 1
  …
  c11-s9  11-3 · Manbadagi holat  ← Case Study
  (keyin terms, quick, review, apps, oral)
```

**Reja qoidalari:**
* `s1` — `Kirish · …` (bob boshidagi hikoya va markaziy savol).
* Kitobning har bir kichik bo‘limi (`11-1a`) alohida dars bo‘limi bo‘ladi. Juda qisqalarini birlashtir:
  `11-2b–c · …`.
* Katta quti (Case Study, In the News) o‘z bo‘limida (`11-2 · Manbadagi holat`) yoki tegishli bo‘lim ichida
  `div.example` sifatida beriladi.
* `Conclusion` → `Yakun · …` (ixtiyoriy).
* Mo‘ljal: **10–16 dars bo‘limi**, 6–9 ming so‘z, kitobdagi har bir rasm uchun SVG chizma.
  Mavjud boblar ham shu hajmda.

## 5. Bobni yozish

### 5.1 Faylni bosqichma-bosqich yarat

`chapter-NN.html` uzun bo‘ladi (chizmalar bilan 100–170 KB):
* Avval faylni `s1–s3` bilan yarat, keyin har bir bo‘limni oxiriga qo‘shib bor (Edit / kichik Python skript).
  Bitta katta yozishda xato oson yo‘qoladi.
* Har 3–4 bo‘limdan keyin lokal commit qil: `Bob 11: jarayonda (s1–s4)`.
* `npm run check -- 11` ni oraliqda ham ishlat. Oxirgi bo‘limlar hali yo‘qligi haqidagi xabarlar oxirida yo‘qoladi.

### 5.2 Dars bo‘limi namunasi (RULE.md §3 ritmi)

```html
<section class="lesson-section" id="c11-s2"><div class="section-kicker">11-1a · Istisno qilinishi</div><h2>Kimni foydalanishdan to‘xtatib bo‘ladi?</h2>
<p>Sodda ta’rif: 2–4 qisqa gap, ≤ 80 so‘z. Inglizcha atama birinchi marta qavsda: <strong>istisno qilinadigan</strong> (excludable).</p>
<p>Nega muhim / qanday ishlaydi — yana bitta fikr.</p>
<div class="callout"><strong>Oddiy misol.</strong> Mahalliy hayotdan: bozor, non, taksi, metro, telefon, talaba.</div>
<h3>Kitobdagi misol: …</h3>
<p>Kitobning aniq misoli va raqamlari (o‘zgartirmasdan).</p>
<figure class="diagram">…SVG (§5.3)…<figcaption>Kitobning 1-rasmi: nimani ko‘rsatadi va qanday o‘qiladi (1–3 gap).</figcaption></figure>
<div class="warning"><strong>Keng tarqalgan xato.</strong> Talabalar ko‘p adashadigan joy.</div>
<div class="recap"><strong>Qisqasi.</strong> Bo‘limning asosiy fikri bir-ikki gapda.</div>
</section>
```

* 2 tadan ortiq hisob bo‘lsa: formula kartasi + `ol.step-list` (namuna — `chapter-05.html#c5-s3`).
* Raqamli ma’lumot ≥ 2 qator bo‘lsa — jadval (`.table-wrap`, ustun nomida birlik).
* Ikki tushuncha solishtirilsa — `.comparison` yoki jadval. Bir nechta teng tushuncha — `.concept-grid`.
* Formulalar faqat LaTeX bilan va telefonga sig‘adigan qilib (RULE.md §6):
  * bir nechta tenglama — `gathered`;
  * uzun tenglama — `aligned`;
  * qadamlarda kasr — `\dfrac`.
* Interaktiv model (`div.interactive`) faqat RULE.md §5.13 dagi mavjud turlardan, mos bo‘lsa. Mos tur bo‘lmasa
  qo‘yilmaydi.

### 5.3 Chizmalar (SVG)

Kitobdagi har bir Figure — **qo‘lda chizilgan inline SVG**. Rasm fayli yoki skrinshot ishlatilmaydi. Namuna
(`chapter-10.html` dan):

```html
<figure class="diagram"><svg viewBox="0 0 640 360" width="100%" role="img" aria-labelledby="c11-f1-title c11-f1-desc" font-family="sans-serif" font-size="14"><title id="c11-f1-title">Qisqa nom</title><desc id="c11-f1-desc">Chizmada nima borligi, 1–2 gap.</desc><path d="M80 30V300H580" fill="none" stroke="#81918b" stroke-width="2"/><text x="16" y="24">Narx</text><text x="500" y="344">Miqdor</text><path d="M100 60L540 280" fill="none" stroke="#17695f" stroke-width="3"/><path d="M100 280L540 60" fill="none" stroke="#c06843" stroke-width="3"/><text x="470" y="270" fill="#17695f">Talab</text><text x="470" y="60" fill="#c06843">Taklif</text><path d="M80 170H320V300" fill="none" stroke="#81918b" stroke-dasharray="5 5"/><circle cx="320" cy="170" r="5" fill="#17695f"/><text x="34" y="176">P*</text><text x="308" y="322">Q*</text><text x="64" y="319">0</text></svg><figcaption>…</figcaption></figure>
```

* Faqat RULE.md §7 ranglari (talab `#17695f`, taklif `#c06843`, o‘qlar `#81918b`, maydonlar jadvaldagi fill’lar).
* Narx — vertikal o‘q, miqdor — gorizontal. Yorliqlar o‘zbekcha, chiziq nomi chiziq yonida.
* ID’lar `c11-f1`, `c11-f2` … — bob ichida yagona. Matn bir-birini va chiziqlarni qoplamasin. Yorliq
  `viewBox` dan chiqmasin.
* Aniq raqamli misolda nuqtalar haqiqiy miqyosda turadi. Sxematik bo‘lsa, figcaption’da shunday deb yoz.
* Kitobdagi jadval (Table) — HTML jadval, rasm emas.

### 5.4 Oxirgi besh bo‘lim

* **`cN-terms`** — kitobning **to‘liq** Key Concepts ro‘yxati (§5.10): `dt` (o‘zbekcha + `span.en`) va bir gapli `dd`.
* **`cN-quick`** — barcha QuickQuiz savollari, butun bob bo‘yicha 1 dan uzluksiz raqamlanadi. Javoblar kitobning
  `QuickQuiz Answers` blokidan olinadi. Namuna:
  ```html
  <details class="answer" data-kind="quick" data-q="1"><summary><span class="q-number">01</span> 11-1 bo‘yicha: …savol mazmuni…?</summary><div class="answer-body"><p><strong>To‘g‘ri javob: c) variant matni.</strong> 1–3 gap nega; boshqa variantlar nega noto‘g‘ri.</p><p>Variantlar: <strong>a)</strong> …; <strong>b)</strong> …; <strong>c)</strong> …; <strong>d)</strong> ….</p></div></details>
  ```
* **`cN-review`** — har bir Questions for Review: `<p><strong>Qisqa javob.</strong> …</p>` + izoh.
* **`cN-apps`** — har bir Problems and Applications **to‘liq yechiladi**:
  * kitobdagi raqamlar o‘zgarmaydi;
  * ko‘p qismli masala `<h4>a)</h4>…`, hisob formula + `step-list`, grafik so‘ralsa — SVG;
  * oxirida `<p><strong>Javob:</strong> …</p>`.
* **`cN-oral`** — `ul.recap` (5–8 fikr), `<h3>Og‘zaki javob rejasi</h3>` + `ol.step-list`,
  `<div class="warning"><strong>Imtihon tuzoqlari.</strong><ul>…</ul></div>`.

Kicker’lardagi sonlar (`QuickQuiz · 9 savol`) haqiqiy `<details>` soniga teng bo‘lishi kerak.

### 5.5 `chapter-NN.json` (RULE.md §8)

Shablon — `chapter-10.json` dan nusxa:
* `id`; `title` (o‘zbekcha, qisqa); `englishTitle` (kitobdagi nom); `lead` (1–2 gap).
* `sourcePages`: `[kitob boshi, kitob oxiri]` — `--list` dagi **kitob** sahifalari, PDF emas.
* `sections`: HTML bilan bir xil tartib, `title` = `h2`, `sourceTopics` — kitobdagi qaysi bo‘limlar.
* `source…Count` — kitobdagi haqiqiy son; `…Answered` — xuddi shu son.
* `topicCoverage` — inventardagi barcha bo‘lim va qutilar.
* `warnings` — shubhali joylar (masalan, "Figure 3 sxematik chizildi").
* `wordCount`, `diagramCount`, `interactiveTypes` ni build o‘zi to‘ldiradi.

### 5.6 `content/course.json`

Bobni o‘z qismiga qo‘sh. Qism `--list` chiqishidagi `[Part …]` dan olinadi:
* Qism mavjud bo‘lsa (masalan, `IV QISM` — Part IV), uning `chapters` ro‘yxatiga qo‘sh: `[10, 11, 12]`.
* Yangi qism bo‘lsa, oxiriga yangi obyekt qo‘sh: `{ "label": "V QISM", "title": "…", "chapters": [13] }`.
  `label` — kitobdagi rim raqami + ` QISM`. `title` — inglizcha nomning qisqa o‘zbekcha tarjimasi.
* Mavjud uslub: "Iqtisodiy fikrlash", "Bozorlar qanday ishlaydi?", "Bozorlar va farovonlik",
  "Davlat sektori iqtisodiyoti".
* `taughtInClass` ga tegma.

## 6. Tekshirish (har bob uchun)

1. Qoidalar:
   ```bash
   npm run check -- 11     # "Bob 11: RULE.md bo‘yicha xato yo‘q ✓" chiqquncha tuzat
   npm run build           # butun sayt, qat’iy rejim; course.json ham tekshiriladi
   ```
2. **Inventar bilan solishtir:**
   * har bir kitob bo‘limi, quti, Figure, Table, Key Concept bormi;
   * QuickQuiz / Review / Problems soni kitob bilan tengmi.
3. **Hisoblarni qayta tekshir.** Har bir raqamli javobni kichik Python bilan qayta hisobla (foiz, maydon, soliq
   tushumi, sof yo‘qotish, elastiklik, xarajat). Javob va matndagi raqam bir xil bo‘lsin.
4. **Ko‘z bilan ko‘r.** Brauzer vositasi bo‘lsa:
   * `npm run dev` → `http://localhost:4173/#bob-11` (port band bo‘lsa:
     `node scripts/py.cjs -m http.server 4180 --directory dist` → `http://localhost:4180/#bob-11`);
   * 360 px va kompyuter kengligida, yorug‘ va qorong‘u rejimda;
   * chizma yorliqlari ustma-ust tushmasin, jadval o‘qilsin, sahifa yon tomonga surilmasin.

   Vosita bo‘lmasa — hisobotda "ko‘z bilan tekshirilmadi" deb yoz.
5. **RULE.md §11 ro‘yxati** — bandma-band.
6. **Til:** `o‘ g‘` — U+2018, tutuq — U+2019. Kirill harf yo‘q. Paragraflar qisqa, bitta fikr.

## 7. Commit (har bob tugaganda)

```bash
git add content/chapters/chapter-11.html content/chapters/chapter-11.json content/course.json
git commit -m "Bob 11: Jamoat ne’matlari va umumiy resurslar qo‘shildi"
```

## 8. GitHub’ga push (har bob tugaganda)

1. **Ruxsat bormi:** `git push --dry-run origin main`. O‘tsa — 3-bandga o‘t.
2. **Bo‘lmasa — bir martalik kirish (device login).** Buyruqni **fon rejimida** ishga tushir va chiqishini o‘qi:
   ```bash
   gh auth login --hostname github.com --git-protocol https --web --skip-ssh-key
   ```
   Chiqishda `! First copy your one-time code: XXXX-XXXX` qatori bo‘ladi. Foydalanuvchiga yoz:
   > Kod: **XXXX-XXXX**. Loyiha egasi telefonida **https://github.com/login/device** ni ochib, kodni kiritadi va
   > **Authorize** bosadi. Kod 15 daqiqa amal qiladi.

   Keyin `AskUserQuestion`: *"Kod kiritildimi?"*. Variantlar: "Ha" / "Kod eskirdi, yangisini ber".
   Kirilgach `gh auth setup-git`. Bu kirishni **sen qilganingni** eslab qol (§10).
3. **Yuborish:**
   ```bash
   git pull --rebase origin main
   npm run build            # rebase’dan keyin ham xatosiz bo‘lsin
   git push origin main
   ```
   Konflikt bo‘lsa — to‘xta va foydalanuvchiga ayt. **Hech qachon `git push --force` ishlatma.**

## 9. Vercel’ga chiqarish (barcha boblar tugagach, bir marta)

`AskUserQuestion`: *"Boblar GitHub’da. Saytni hozir Vercel’ga ham chiqaraymi?"*. Variantlar: "Ha, chiqar" /
"Yo‘q, keyin". "Ha" bo‘lsa:

```bash
vercel --version || npm install -g vercel
vercel whoami                      # kirilmagan bo‘lsa: vercel login (ekrandagi havola/kod — foydalanuvchi tasdiqlaydi)
test -f .vercel/project.json || vercel link --yes --team dostonbekuzdevs-projects --project mankiw-chapters
npm run deploy                     # qat’iy build + vercel deploy --prod
curl -s https://mankiw-chapters.vercel.app/ | grep -o 'chapters/chapter-11\.[0-9a-f]*\.html'   # yangi bob jonli saytda
```

Vercel loyihasi loyiha egasining hisobida. Boshqa hisob bilan `link` yoki `deploy` ishlamasa, majburlama.
Foydalanuvchiga ayt: *"Saytni egasi chiqaradi: `git pull && npm run deploy`"*.

## 10. Yakun va hisobot

1. §8 da **sen** `gh auth login` qilgan bo‘lsang, tokenni o‘chir:
   ```bash
   gh auth logout --hostname github.com --user uzbtrust
   ```
   Foydalanuvchining o‘z oldindan kirgan hisobiga tegma.
2. Hisobot (qisqa, o‘zbekcha), har bob uchun:
   * nomi;
   * dars bo‘limlari soni, chizmalar soni, so‘zlar soni;
   * QuickQuiz / Review / Problems: yozilgan / kitobda;
   * commit havolasi `https://github.com/uzbtrust/mankiw-chapters/commit/<sha>`.

   Oxirida: sayt manzili (chiqarilgan bo‘lsa), shubhali joylar (masalan, sxematik chizmalar) va
   ko‘z bilan tekshirilmagan narsalar.

## 11. Build xabarlari va tuzatish

| Xabar (`npm run check`) | Tuzatish |
|---|---|
| `bo‘limlar tartibi/ID` | `cN-s1…cN-sK` uzluksiz, keyin `terms, quick, review, apps, oral` |
| `kicker «…» → «N-1a · Qisqa mavzu»` | `11-1a · …`, `Kirish · …`, `Yakun · …`, `Ilova · …` |
| `JSON sections[].title h2 bilan bir xil bo‘lsin` | JSON dagi `title` ni h2 matniga tenglashtir |
| `kickerda 9, aslida 8 savol` | kicker sonini yoki `<details>` sonini to‘g‘rila |
| `review expected 6, actual 5` | JSON `sourceReviewCount` = kitobdagi son, hammasini javobla |
| `.callout «Oddiy misol. / Muhim. / Eslatma.» bilan boshlansin` | kartaning birinchi `<strong>` yorlig‘i |
| `QuickQuiz javobi «To‘g‘ri javob: b) …»` | `<p><strong>To‘g‘ri javob: b) variant matni.</strong> …` |
| `formula telefonga sig‘maydi` / `\qquad` | `gathered` / `aligned` bilan qatorlarga bo‘l (RULE.md §6) |
| `qadamdagi formula telefonga sig‘maydi` | `a/b` → `\dfrac{a}{b}` yoki ikki `\( … \)` ga bo‘l |
| `paragraf 95 so‘z (> 80)` | ikki paragrafga bo‘l |
| `jadval: <thead> va <tbody>` / `.table-wrap` | `<div class="table-wrap"><table><thead>…</thead><tbody>…</tbody></table></div>` |
| `<sub>/<sup> o‘rniga LaTeX` | `Q<sub>d</sub>` → `\(Q_d\)` |
| `LaTeX xatolari: …` | ko‘rsatilgan ifodani tuzat (`&lt;` / `&gt;`, `\%`, qavslar juftligi) |
| `content/course.json: parts[].chapters 1…N` | yangi bobni bir qismga, faqat bir marta qo‘sh |
| `Boblar 1 dan uzluksiz raqamlanishi kerak` | oradagi bob yo‘q — §2.3 |
| `Cyrillic text` | kirill harfni lotinga almashtir |
