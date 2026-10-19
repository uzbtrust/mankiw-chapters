#!/usr/bin/env node
/* LaTeX → MathML (Temml). build.py chaqiradi: stdin = [{tex, display}], stdout = [{html} | {error}].
   Natija oddiy MathML — brauzer o‘zi chizadi, sahifaga JS ham, shrift ham qo‘shilmaydi. */
const temml = require('temml');

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => (input += d));
process.stdin.on('end', () => {
  const items = JSON.parse(input || '[]');
  const out = items.map(({ tex, display }) => {
    try {
      return {
        html: temml.renderToString(tex, {
          displayMode: !!display,
          throwOnError: true,
          trust: false,
          annotate: true /* asl LaTeX <annotation> ichida saqlanadi: nusxa olish va qidiruv uchun */,
        }),
      };
    } catch (e) {
      return { error: String(e.message || e) };
    }
  });
  process.stdout.write(JSON.stringify(out));
});
