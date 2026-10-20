#!/usr/bin/env node
/* Python skriptini har qanday OS da ishga tushirish: macOS/Linux — python3, Windows — py -3 yoki python.
   npm run … shu orqali ishlaydi:  node scripts/py.cjs scripts/build.py --check 5 */
const { spawnSync } = require('child_process');

const args = process.argv.slice(2);
const env = { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' };
const candidates =
  process.platform === 'win32'
    ? [['py', ['-3']], ['python', []], ['python3', []]]
    : [['python3', []], ['python', []]];

for (const [cmd, pre] of candidates) {
  const probe = spawnSync(cmd, [...pre, '-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'], {
    env,
    stdio: 'ignore',
  });
  if (probe.status !== 0) continue;
  const r = spawnSync(cmd, [...pre, ...args], { env, stdio: 'inherit' });
  process.exit(r.status ?? 1);
}
console.error('Python 3.8+ topilmadi. BOB_QOSHISH.md → §0 "Kerakli dasturlar" ga qarang.');
process.exit(1);
