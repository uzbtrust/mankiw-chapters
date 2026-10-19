# TUGATISH.md — bitta bobni tugatib, GitHub’ga yuborish

> **Bu fayl faqat mavjud 1–10-boblar uchun:** ular allaqachon yozilgan, vazifa — ularni yangi yagona dizayn va
> tuzilishga (`RULE.md`) keltirish. Kitob PDF aniqlik uchun ishlatiladi (to‘liq atamalar, QuickQuiz variantlari).
> Yangi boblar (11+) qo‘shish — alohida tizim, `RULE.md` §2.

**Odam uchun (bir marta o‘qing):**

```bash
git clone https://github.com/uzbtrust/mankiw-chapters.git
cd mankiw-chapters
claude
```

Loyiha egasi Telegram’da yuborgan **kitob PDF faylini shu `mankiw-chapters` papkasining o‘ziga** (README.md yoniga)
qo‘ying. Keyin Claude Code ichida modelni **Opus 5.5** ga qo‘ying va yozing: **`TUGATISH.md ni o‘qi va bajar`**.
Claude o‘zi kerakli dasturlarni o‘rnatadi, navbatdagi bobni o‘zi aniqlaydi (masalan 1–3 tayyor bo‘lsa — 4-bob), uni tugatadi va oxirida sizga bitta kod beradi — o‘sha kodni loyiha
egasiga (Telegram’da) yuborasiz, u telefonidan kiritadi, Claude ishni GitHub’ga yuboradi. Tamom.

---

## AI uchun: vazifa va qat’iy qoidalar

Sen shu repozitoriyadagi o‘zbekcha Mankiw o‘quv saytining **bitta bobini** `RULE.md` andozasiga keltirasan va
GitHub’ga push qilasan. Bob tayyor deb hisoblanadi, qachonki: `npm run check -- N` → `xato yo‘q ✓`, mazmun yo‘qolmagan
(§4.4), va o‘zgarish `main` ga push qilingan.

1. **Ishni o‘zing qil. Subagent (Agent / Task tool) ishlatma**, parallel ish yo‘q — bitta bob, ketma-ket.
2. **Faqat ikki fayl o‘zgaradi:** `content/chapters/chapter-NN.html` va `content/chapters/chapter-NN.json`.
   `src/`, `scripts/`, `RULE.md`, `docs/`, `package.json`, boshqa boblar — tegilmaydi. Qoida noto‘g‘ri yoki bajarib
   bo‘lmaydigan tuyulsa, uni o‘zgartirma — yakuniy hisobotda yoz.
3. **Ish yo‘qolmasin:** har 2–3 bo‘limdan keyin lokal commit qil (§5). Limit tugab sessiya uzilsa, keyingi sessiyada
   foydalanuvchi "TUGATISH.md ni davom ettir" deydi — `git log` va `npm run check -- N` dan qayerdaligingni top.
4. **Deploy qilma** (Vercel loyiha egasida). Faqat GitHub’ga push.
5. **Yetishmayotgan dastur bo‘lsa — so‘ramasdan o‘zing o‘rnat** (§0). Foydalanuvchidan faqat quyidagilarni so‘raysan:
   kitob PDF topilmasa — uni papkaga qo‘yish (§3), GitHub kodi kiritilganini tasdiqlash (§6), hamda
   o‘rnatish parol yoki tugma bosishni talab qilsa.
6. Foydalanuvchi bilan **o‘zbek tilida**, qisqa gaplashing.

---

## 0. Kerakli dasturlar — tekshir va yetishmaganini o‘rnat

Kerak: `git`, `node` ≥ 18 (+ `npm`), Python ≥ 3.8, `gh` (GitHub CLI). Tekshirish:

```bash
git --version; node --version; npm --version; gh --version
python3 --version || python --version || py -3 --version
```

**Windows** (Claude Code Git Bash’da ishlaydi; `git` allaqachon bor). Yetishmaganini `winget` bilan o‘rnat:

```bash
winget install --id OpenJS.NodeJS.LTS -e --silent --accept-source-agreements --accept-package-agreements
winget install --id GitHub.cli        -e --silent --accept-source-agreements --accept-package-agreements
winget install --id Python.Python.3.12 -e --silent --accept-source-agreements --accept-package-agreements
# o‘rnatilgandan keyin joriy shell PATH’ni ko‘rmasligi mumkin — qo‘shib qo‘y:
export PATH="$PATH:/c/Program Files/nodejs:/c/Program Files/GitHub CLI:$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts"
```
`winget` yo‘q bo‘lsa (eski Windows): Node — <https://nodejs.org> MSI, gh — <https://cli.github.com> MSI, Python —
<https://python.org> (curl bilan yuklab `msiexec /i … /quiet` / `python-installer.exe /quiet PrependPath=1`).
Windows’da Python buyrug‘i `py -3` bo‘lishi mumkin — `npm run …` buyruqlari buni o‘zi topadi (`scripts/py.cjs`).

**macOS:**

```bash
xcode-select -p >/dev/null 2>&1 || xcode-select --install   # git va python3 shu bilan keladi
```
`xcode-select --install` oyna ochadi — foydalanuvchiga "Install tugmasini bosing" deb ayt va tugashini kut.
Keyin `brew` bo‘lsa: `brew install node gh`. `brew` bo‘lmasa (parolsiz yo‘l):

```bash
curl -fsSL -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm install --lts
mkdir -p ~/.local/bin && cd /tmp
ARCH=$( [ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64 )
URL=$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest | grep -o "https://[^\"]*macOS_${ARCH}.zip" | head -1)
curl -fsSL -o gh.zip "$URL" && unzip -oq gh.zip && cp gh_*/bin/gh ~/.local/bin/ && cd -
export PATH="$HOME/.local/bin:$PATH"
```

**Linux (Debian/Ubuntu):** `sudo apt-get update && sudo apt-get install -y git nodejs npm python3 gh`
(gh topilmasa: <https://github.com/cli/cli/blob/trunk/docs/install_linux.md>).

**Loyiha kutubxonalari** (har doim, repo papkasida):

```bash
npm install
```
Kitob PDF’dan matn ajratish uchun (§3) `pdftotext` (poppler) bo‘lmasa: `python3 -m pip install --user pypdf`
(Windows: `py -3 -m pip install --user pypdf`). Skript o‘zi qaysi biri borligini aniqlaydi.

---

## 1. O‘qish (majburiy, oxirigacha)

1. **`RULE.md`** — bob tuzilishi (§4), komponentlar (§5), tushuntirish uslubi (§3), LaTeX (§6), chizma ranglari (§7),
   JSON (§8). Bu asosiy shartnoma.
2. **`docs/DESIGN.md`** — dizayn qoidalari (nima uchun shunday ko‘rinadi). `src/` ga tegmaysan, lekin komponentni
   to‘g‘ri tanlash uchun o‘qi.
3. **Namunalar:** `content/chapters/chapter-05.html` ichidagi `id="c5-s3"` bo‘limi (formula kartasi + izoh, jadval,
   bosqichma-bosqich hisob, `Oddiy misol.`, `Keng tarqalgan xato.`, `Qisqasi.`) va `chapter-03.html` (uslub).

## 2. Bobni tanlash — o‘zing aniqla, so‘rama

```bash
git pull --rebase origin main
npm run status
```
Oxirgi qator `Keyingi bob: N` — **shu bobni ol** (eng kichik raqamli tugallanmagan bob). Masalan 1, 2, 3-boblar
`✓ tayyor` bo‘lsa — 4-bobni qilasan. Foydalanuvchidan bob raqamini so‘rama. Faqat foydalanuvchi o‘z xabarida aniq
bob aytgan bo‘lsa ("7-bobni qil") — o‘shani ol. `Keyingi bob: yo‘q` bo‘lsa — "Hamma boblar tayyor" deb ayt va to‘xta.

Commit muallifi (so‘ramasdan):

```bash
git config user.name  >/dev/null || git config user.name  "Mankiw yordamchi"
git config user.email >/dev/null || git config user.email "yordamchi@users.noreply.github.com"
```
Ishni boshlashdan oldin foydalanuvchiga bir qatorda ayt: *"N-bobni boshlayapman (1…N−1 tayyor)."*
Quyida `N` — bob raqami (masalan 4), `NN` — ikki xonali (04).

## 3. Kitob PDF va bob matni

Kitob PDF **har doim loyiha ildizida** turadi (`./*.pdf`, README.md yonida). U git’ga kirmaydi (`.gitignore`) —
hech qachon `git add` qilma.

1. Top: `ls *.pdf`. Yo‘q bo‘lsa — foydalanuvchiga ayt: *"Kitob PDF faylini (egasi Telegram’da yuborgan) shu loyiha
   papkasiga qo‘ying va «tayyor» deb yozing"* (`AskUserQuestion`: "Tayyor" / "PDF yo‘q, kitobsiz davom et").
   "Kitobsiz" tanlansa — pastdagi **zaxira qoidalar** bilan ishlash.
2. Bob matnini ajrat. PDF 209 sahifali "Chapters 1-10" fayli bo‘lsa (`pdfinfo` yoki skript chiqishi), sahifalar:

| Bob | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| `--pages` | 1-16 | 17-44 | 45-60 | 61-86 | 87-110 | 111-132 | 133-152 | 153-168 | 169-188 | 189-209 |

```bash
node scripts/py.cjs scripts/extract_chapter.py ./<fayl>.pdf --chapter N --pages A-B
```
   Boshqa fayl (butun kitob) bo‘lsa: avval `--find "Chapter N"` va `--find "Chapter N+1"` bilan sahifalarni top.
   Natija: `reference/source-text/chapter-NN.txt`.
3. Matnni **to‘liq** o‘qi (bo‘lib-bo‘lib). Undan ol: **Key Concepts** to‘liq ro‘yxati, **QuickQuiz variantlari** matni,
   bo‘lim raqamlari (`N-1a` …). Bob HTML’idagi raqamlar va savol shartlari kitob bilan mosligini ham tekshir.

Asosiy mazmun — bobning hozirgi `chapter-NN.html` / `.json`: uni qayta joylaysan va soddalashtirasan; yangi fakt,
raqam, statistika qo‘shilmaydi (kitobda bo‘lib, bobda tushib qolgan muhim narsa bo‘lsa — qo‘shish mumkin).

**Zaxira qoidalar (kitob yo‘q bo‘lsa):** QuickQuiz `To‘g‘ri javob: c) …` matni hozirgi javobdagi to‘g‘ri variant
mazmunidan ("Javob: b — PPF ustida" → `To‘g‘ri javob: b) nuqta PPF ustida bo‘ladi.`), noto‘g‘ri variantlarni o‘ylab
topma; atamalar — bobda ta’riflangan asosiy tushunchalar; kicker raqami — mavjud kicker / JSON `topicCoverage` dan.

## 4. Bobni RULE.md andozasiga keltirish

**4.1 Boshlash:**

```bash
npm run check -- N        # barcha buzilgan qoidalar ro‘yxati — shu ro‘yxat sening ish rejang
```

**4.2 Nima qilinadi** (RULE.md bilan birga):

1. **Skelet (RULE.md §4):** dars bo‘limlari `cN-s1…cN-sK` (uzluksiz), keyin `cN-terms`, `cN-quick`, `cN-review`,
   `cN-apps`, `cN-oral` — belgilangan kicker va h2 sarlavhalar bilan. Kicker: `<kitob raqami> · <qisqa mavzu>`
   (`7-1a · To‘lashga tayyorlik`), birinchi bo‘lim `Kirish · …`. Aralash bo‘limlardagi atamalar ro‘yxati, og‘zaki reja,
   tuzoqlar — `cN-terms` / `cN-oral` ga ko‘chadi. Har `<details class="answer">` o‘z bo‘limida.
   JSON `sections` — HTML bilan bir xil tartib, `title` = h2 matni.
2. **`cN-terms`:** kitobning **to‘liq** Key Concepts ro‘yxati (§3) `<div class="key-concepts"><dl>` ichida:
   `<dt>O‘zbekcha atama <span class="en">english term</span></dt><dd>bir gapli sodda ta’rif</dd>`.
3. **`cN-oral`:** `ul.recap` (5–8 asosiy fikr) + `<h3>Og‘zaki javob rejasi</h3><ol class="step-list">` +
   `<div class="warning"><strong>Imtihon tuzoqlari.</strong><ul>…</ul></div>`.
4. **QuickQuiz:** har javob `<p><strong>To‘g‘ri javob: c) variant matni.</strong> 1–3 gap nega.</p>` bilan boshlanadi.
5. **Karta yorliqlari (RULE.md §5):** callout → `Oddiy misol.` / `Muhim.` / `Eslatma.`; warning →
   `Keng tarqalgan xato.` / `Imtihon tuzoqlari.` / `Diqqat.`; recap → `Qisqasi.`.
6. **Formulalar → LaTeX (RULE.md §6):** asosiy formulalar `.formula` kartada (`formula-title` + `formula-legend`),
   matndagi belgilar `\( … \)`. `<sub>`, `<sup>`, "P×Q", "Q₂−Q₁" kabi oddiy matn formula qolmasin.
   Bir nechta tenglama — har biri alohida qatorda (`gathered`), uzuni `aligned` bilan bo‘linadi: telefonga sig‘ishini build tekshiradi.
7. **Soddalik:** paragraf ≤ 80 so‘z; bitta paragraf — bitta fikr; qisqa gaplar. 2 tadan ortiq hisob — formula +
   `ol.step-list` yoki jadval (aynan `c5-s3` dagidek). Ko‘p qismli masala: `<h4>a)</h4>…<h4>b)</h4>…`, oxirida aniq javob.
   Raqamli ma’lumot ≥ 2 qator — jadval (ustun nomida birlik).
8. **Dars bo‘limlarida ritm** (2–3-boblardagidek): sodda ta’rif → `Oddiy misol.` → kitobdagi misol/grafik →
   `Keng tarqalgan xato.` → kerak bo‘lsa `Qisqasi.`. Yangi fakt yoki statistika o‘ylab topilmaydi.

**4.3 Xavfsiz tahrirlash:** fayl uzun bitta HTML bo‘lagi. Bo‘limma-bo‘lim ishlang (Edit tool yoki bitta bo‘limni
almashtiradigan kichik Python skript). **Butun faylni xotiradan qayta yozma.** Har bir `<figure class="diagram">` SVG
**baytma-bayt o‘zgarmaydi** (faqat tegishli bo‘limga ko‘chirish mumkin). Interaktiv `div` va barcha savol raqamlari
(`data-kind`, `data-q`) saqlanadi. O‘zgartirgan har bir hisobni qayta tekshir.

**4.4 Mazmun yo‘qolmaganini tekshir** (oxirida):

```bash
mkdir -p build && git show origin/main:content/chapters/chapter-NN.html > build/before-NN.html
node -e "const f=require('fs');for(const p of ['build/before-NN.html','content/chapters/chapter-NN.html']){const s=f.readFileSync(p,'utf8');const t=s.replace(/<svg[\s\S]*?<\/svg>/g,'').replace(/<[^>]+>/g,' ');console.log(p,'svg',(s.match(/<svg/g)||[]).length,'details',(s.match(/<details/g)||[]).length,'soz',t.split(/\s+/).filter(Boolean).length)}"
```
`svg` va `details` soni bir xil; so‘zlar soni 5% dan ko‘p kamaymagan bo‘lsin (oshishi mumkin).

**4.5 Yakun:** `npm run check -- N` → `Bob N: RULE.md bo‘yicha xato yo‘q ✓`.

## 5. Lokal commit (ish davomida ham, oxirida ham)

```bash
git add content/chapters/chapter-NN.html content/chapters/chapter-NN.json
git commit -m "Bob N: RULE.md andozasi (jarayonda)"     # oxirgisida: "Bob N: RULE.md andozasiga keltirildi"
```

## 6. GitHub’ga bir martalik kirish va push

1. Kirilganmi? `gh auth status`. Agar **`uzbtrust`** hisobi faol bo‘lsa — 3-bandga o‘t. Boshqa (masalan, o‘z) hisobingiz
   bilan kirilgan bo‘lsa ham 2-bandni bajar — gh ikkinchi hisobni qo‘shadi va uni faol qiladi.
2. Kirish (device login). Buyruqni **fon rejimida** ishga tushir (Bash `run_in_background`), chiqishini o‘qi:

   ```bash
   gh auth login --hostname github.com --git-protocol https --web --skip-ssh-key
   ```
   Chiqishda `! First copy your one-time code: XXXX-XXXX` qatori bo‘ladi. Foydalanuvchiga aniq shunday yoz:

   > Kod: **XXXX-XXXX**. Shu kodni loyiha egasiga yuboring. U telefonida **https://github.com/login/device** ni ochib,
   > kodni kiritadi va **Authorize** bosadi. Kod 15 daqiqa amal qiladi.

   Keyin `AskUserQuestion`: "Egasi kodni kiritdimi?" — variantlar: "Ha, kiritdi" / "Kod eskirdi, yangisini ber".
   "Ha" bo‘lsa fon jarayoni tugashini kut va `gh auth status` bilan tekshir. Eskirgan bo‘lsa — jarayonni to‘xtatib,
   2-bandni qaytadan bajar.
3. Yuborish:

   ```bash
   gh auth setup-git
   git pull --rebase origin main      # boshqalar boshqa boblarni yuborgan bo‘lishi mumkin
   npm run check -- N                 # rebase’dan keyin ham ✓ bo‘lsin
   git push origin main
   ```
   Rebase’da konflikt bo‘lsa (kimdir aynan shu bobni o‘zgartirgan) — to‘xta, foydalanuvchiga ayt, majburan push qilma.
   **Hech qachon `git push --force` ishlatma.**
4. **Egasining tokenini kompyuterdan o‘chir** (push muvaffaqiyatli bo‘lsa ham, bo‘lmasa ham):

   ```bash
   gh auth logout --hostname github.com --user uzbtrust
   ```

## 7. Yakuniy hisobot (foydalanuvchiga, qisqa)

* `Bob N tayyor ✓` va commit havolasi: `https://github.com/uzbtrust/mankiw-chapters/commit/<sha>`;
* bo‘limlar oldin → keyin; so‘z, `svg`, `details` soni oldin → keyin;
* topilgan va tuzatilgan hisob xatolari;
* RULE.md da noto‘g‘ri tuyulgan qoida bo‘lsa — shu yerda yoz.

Keyin foydalanuvchiga: *"Yana bir bob qilamizmi?"* — "ha" desa §2 dan boshla (`npm run status` keyingi bobni ko‘rsatadi;
yangi sessiyada boshlash yaxshiroq — kontekst toza bo‘ladi, sessiya o‘chirib yuborilsa ham hech narsa yo‘qolmaydi,
chunki tayyor boblar GitHub’da).

**Bir vaqtda ikki kishi ishlasa:** ikkalasi bir xil "keyingi bob"ni olishi mumkin. Push paytida `git pull --rebase`
konflikt bersa yoki `npm run status` shu bobni allaqachon `✓` desa — foydalanuvchiga ayt; o‘z variantingni majburan
yuborma. Buning oldini olish uchun egasi har kimga bob raqamini aytishi mumkin ("TUGATISH.md ni bajar, 6-bobni qil").
