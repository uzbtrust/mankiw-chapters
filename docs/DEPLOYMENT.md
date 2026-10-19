# Nashr qilish

* Production: https://mankiw-chapters.vercel.app (Vercel loyihasi `mankiw-chapters`, `.vercel/project.json` orqali bog‘langan)
* Kod: GitHub `uzbtrust/mankiw-chapters` (kitob PDF va bob matnlari git’ga kirmaydi)
* Yig‘ish: `python3 scripts/build.py` → `dist/` (Vercel) + `outputs/iqtisodiyot-NN-bob.html` (internetsiz nusxa)
* Chiqarish: `npm run deploy` (ya’ni `vercel deploy --prod --yes`). `.vercelignore` faqat `dist/` va `vercel.json` ni qoldiradi.

## Yig‘ish nima qiladi
* `content/chapters` ni tekshiradi: teg balansi, savollar soni, kirill harf yo‘qligi va RULE.md andozasi (`check_standard`).
* `\( … \)` / `\[ … \]` dagi LaTeX ni MathML ga aylantiradi (`scripts/tex.cjs`, Temml). Brauzerda JS kerak emas.
* 4+ ustunli jadval kataklariga `data-label` yozadi (telefonda karta ko‘rinishi uchun).
* `src/partials` ni `src/index.html` ga ulaydi; `src/css/*.css` ni nom tartibida birlashtirib minify qiladi.
* `src/js/motion/*` + `src/js/app/*` ni bitta `app.<hash>.js` ga, GSAP (+ScrollTrigger, ScrollTo, SplitText,
  DrawSVG, CustomEase) ni `vendor.<hash>.js` ga, modellarni `models.<hash>.js` ga, qidiruvni `search.<hash>.json` ga yig‘adi.
* Boblar `chapters/chapter-NN.<hash>.html` bo‘lib alohida yuklanadi. Barcha hash’langan fayllar bir yil `immutable` keshlanadi.
* Internetsiz nusxada hammasi bitta HTML ichida.
* Oldingi hash’langan fayllarni o‘chirmaydi (ochiq turgan eski sahifalar ishlashda qolishi uchun). Tozalash: `--clean`.

## Hajm
Yig‘ish oxirida "Birinchi yuklash (gzip)" faqat ma’lumot uchun chop etiladi. Qat’iy byudjet yo‘q: sifat birinchi o‘rinda.
Bob, model va qidiruv ma’lumoti baribir kerak bo‘lganda yuklanadi, hash’langan fayllar keshlanadi.
