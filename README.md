# Iqtisodiyot — Mankiw, 1–10 boblar

N. Gregory Mankiw, *Principles of Economics* (10-nashr) boblarining o‘zbekcha o‘quv sayti:
izohli darslar, chizmalar, interaktiv modellar va yechimli savollar. Og‘zaki imtihonga tayyorlanish uchun.

Sayt: <https://mankiw-presentation.vercel.app>

> **Yangi bob qo‘shish yoki bobni tahrirlash — avval [RULE.md](RULE.md) ni o‘qing.** U yerda kitobdan ajratish,
> tushuntirish uslubi, bob skeleti, komponentlar, LaTeX formulalar, chizma ranglari va tekshiruvlar yozilgan.
> Mavjud bobni tugatib GitHub’ga yuborish (do‘stlar uchun): **[TUGATISH.md](TUGATISH.md)**.

## Papka tuzilishi

```
content/chapters/   boblar: chapter-NN.html (dars) + chapter-NN.json (metama’lumot)  ← MANBA
content/course.json qismlar (I QISM …) va "darsda o‘tilgan" boblar
src/
  index.html        sahifa skeleti (partials ni ulaydi)
  partials/         head, chrome (yuqori panel), landing (bosh sahifa), reader (o‘qish), dialogs
  css/              00-tokens … 90-print — fayl nomi tartibida ulanadi (dizayn tokenlari 00 da)
  js/app/           ilova mantig‘i: marshrut, bob yuklash, qidiruv, sozlamalar
  js/motion/        GSAP animatsiyalari (hodisalar orqali ulanadi)
  js/simulations.js interaktiv modellar (kerak bo‘lganda yuklanadi)
scripts/build.py    saytni yig‘uvchi skript + RULE.md qoidalarini tekshirish
scripts/tex.cjs     LaTeX → MathML (Temml), build.py chaqiradi
scripts/extract_chapter.py  kitob PDF dan bob matnini sahifa belgilari bilan ajratish
RULE.md             bob qo‘shish/tahrirlashning yagona qoidalari (har qanday AI uchun)
docs/               DESIGN.md (dizayn va harakat qoidalari), DEPLOYMENT.md
reference/          kitob PDF va bob matnlari (nashr qilinmaydi, git’ga kirmaydi)
tools/legacy/       eski bir martalik tuzatish skriptlari (faqat tarix uchun)
dist/               yig‘ilgan sayt — Vercel’ga shu chiqadi (avtomatik yaratiladi, qo‘lda tahrirlamang)
outputs/            internetsiz ishlaydigan yagona HTML nusxa (avtomatik yaratiladi)
build/              yig‘ish hisobotlari (coverage.json, build-info.json)
```

## Ishlatish

```bash
npm install            # bir marta: GSAP, esbuild, Temml
npm run check -- 5     # faqat 5-bobni RULE.md bo‘yicha tekshirish
npm run status         # qaysi boblar tayyor
npm run build          # dist/ va outputs/iqtisodiyot-NN-bob.html
npm run dev            # yig‘ib (--lenient), http://localhost:4173 da ko‘rsatadi
npm run deploy         # yig‘ib, Vercel’ga chiqaradi (production)
```

`dist/index.html` va `outputs/*.html` har yig‘ishda qayta yoziladi — ularni qo‘lda tahrirlamang,
o‘zgartirishni `content/` yoki `src/` ga kiriting.

## Yuklash qoidalari (saqlansin)

* Bosh sahifa kichik; bob matni bob tanlanganda yuklanadi; modellar va qidiruv ma’lumoti kerak bo‘lganda.
* Hash’langan fayllar `immutable` keshlanadi (`vercel.json`). Eski hash’lar `dist/` da qoladi.
* Tashqi shrift va CDN yo‘q: shrift — tizim San Francisco (`-apple-system`). Animatsiya — mahalliy GSAP.
* Hajm bo‘yicha qat’iy chegara yo‘q — sifat birinchi o‘rinda.
* Dizayn va harakat qoidalari: [docs/DESIGN.md](docs/DESIGN.md).
