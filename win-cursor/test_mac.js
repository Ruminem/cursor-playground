// SPDX-License-Identifier: Apache-2.0
// 시안 페이지의 "맥용 .cape 받기"(윈도우가 아닐 때 맨 아래 줄 적용 자리) 가 지금 dist 로 .cape 를 구울 수 있는지 본다.
// 굽는 코드(window.cpCape)를 따로 옮겨 적지 않고 preview.tpl.html 에서 그대로 떼어 node 에서 돌린다 — 페이지의 fetch 는
// dist 파일 읽기로, 캔버스는 받은 PNG 를 재는 흉내로 바꾼다. 구성표 전부 × 모양 전부를 한 번씩 누른다.
// 그림을 고쳐도 커서 파일 꼴(32·64px 가 든 .cur, rate·seq 가 든 .ani, dist 경로, 칸마다 같은 확장자)이
// 그대로면 통과하고, 그게 바뀌어 맥 버튼이 깨지면 여기서 걸린다.
// 사용법: win-cursor 에서 python build.py 뒤에 node test_mac.js (의존성 없음)
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const HERE = __dirname, read = p => fs.readFileSync(path.join(HERE, p));

const tpl = read('preview.tpl.html').toString('utf8');
const start = tpl.indexOf('// 맥용 .cape:'), end = tpl.indexOf('\n// 내 백업', start);
if (start < 0 || end < 0) { console.log('preview.tpl.html 에서 맥 버튼 코드를 못 찾음'); process.exit(1); }
const code = tpl.slice(start, end);

const schemes = JSON.parse(read('schemes.json')), shapes = JSON.parse(read('shapes.json'));
const MAC = JSON.parse(read('mac.json')), MAX = 24, PTS = 32;
const PNG = '89504e470d0a1a0a';
// 페이지의 animated() 와 같은 규칙: 구성표 안에 .ani 가 하나라도 있으면 그 구성표는 전부 .ani 로 받는다
const animated = sid => fs.readdirSync(path.join(HERE, 'dist', sid)).some(f => f.endsWith('.ani'));

// 한 번 누르기 = 페이지 코드를 새 판에 올리고 cpCape(). 끝나면 {xml, err, bad, missing}
function press(sid, shape, hue) {
  return new Promise(done => {
    const bad = [], missing = [];
    let xml = null;
    class Blob {
      constructor(parts) { this.parts = parts; this.size = parts.reduce((n, p) => n + (p.length || p.byteLength || 0), 0); }
      arrayBuffer() { return Promise.resolve(Buffer.concat(this.parts.map(p => Buffer.from(p)))); }
    }
    const canvas = () => {
      const cv = {
        width: 0, height: 0,
        getContext: () => ({
          drawImage(im, x, y, w, h) { if (w !== PTS && w !== 2 * PTS) bad.push(`그리는 크기 ${w}`); },
          getImageData: () => ({ data: new Uint8ClampedArray(cv.width * cv.height * 4) }),
          putImageData() {},
        }),
        // 굽는 PNG 대신 크기만 적은 표식. 줄 수(장 수)를 .cape 쪽에서 맞춰 본다
        toBlob: ok => ok(new Blob([Buffer.from(`${cv.width}x${cv.height}`)])),
      };
      return cv;
    };
    const window = {
      cpHue: () => hue, cpShape: () => shape, cpShapes: () => shapes, cpAnimated: () => animated(sid),
      cpRotate(d, deg) { if (deg !== hue) bad.push('색조가 안 넘어감'); },
    };
    const document = {
      querySelector: () => ({ getAttribute: () => sid }),
      createElement: tag => tag === 'canvas' ? canvas() : { click() {} },
    };
    const fetch = url => {
      const file = path.join(HERE, url);
      if (!fs.existsSync(file)) { missing.push(url); return Promise.resolve({ ok: false }); }
      const b = fs.readFileSync(file);
      const ab = b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
      return Promise.resolve({ ok: true, arrayBuffer: () => Promise.resolve(ab), json: () => Promise.resolve(JSON.parse(b)) });
    };
    // .cur 에서 떼어 낸 조각이 진짜 PNG 인지, 크기가 몇인지를 여기서 잰다 (IHDR 폭·높이)
    const createImageBitmap = blob => blob.arrayBuffer().then(b => {
      if (b.slice(0, 8).toString('hex') !== PNG) { bad.push('PNG 가 아닌 조각'); return {}; }
      const w = b.readUInt32BE(16), h = b.readUInt32BE(20);
      if (w !== h || ![32, 64, 128].includes(w)) bad.push(`그림 크기 ${w}x${h}`);
      return { width: w, height: h };
    });
    const URL = { createObjectURL: b => { xml = Buffer.concat(b.parts.map(p => Buffer.from(p))).toString('utf8'); return 'blob:'; }, revokeObjectURL() {} };
    const ctx = { window, document, fetch, createImageBitmap, Blob, URL, btoa: s => Buffer.from(s, 'binary').toString('base64'),
                  setTimeout, Promise, Math, String, Object, Number, Uint8Array, DataView, Error, JSON };
    vm.runInNewContext(code, ctx);
    window.cpCape().then(() => done({ xml, bad, missing }), err => done({ xml: null, err, bad, missing }));
  });
}

// 구운 .cape 가 Mousecape 가 받는 꼴인지
function check(xml) {
  const out = [];
  const body = xml.match(/<key>Cursors<\/key><dict>([\s\S]*?)<\/dict><key>HiDPI/);
  if (!body) return ['Cursors 가 없음'];
  const dicts = {};
  for (const m of body[1].matchAll(/<key>([^<]+)<\/key><dict>([\s\S]*?)<\/dict>/g)) dicts[m[1]] = m[2];
  for (const [rid, names] of Object.entries(MAC)) for (const n of names) {
    const d = dicts[n];
    if (!d) { out.push(`${rid} → ${n} 없음`); continue; }
    const num = k => Number((d.match(new RegExp(`<key>${k}</key><(?:real|integer)>([^<]+)<`)) || [])[1]);
    const count = num('FrameCount'), dur = num('FrameDuration'), hx = num('HotSpotX'), hy = num('HotSpotY');
    if (!(count >= 1 && count <= MAX)) out.push(`${rid}: 장 수 ${count}`);
    if (!(dur > 0)) out.push(`${rid}: 장 길이 ${dur}`);
    if (!(hx >= 0 && hx < PTS && hy >= 0 && hy < PTS)) out.push(`${rid}: 핫스팟 ${hx},${hy}`);
    const reps = [...d.matchAll(/<data>([^<]*)<\/data>/g)].map(m => Buffer.from(m[1], 'base64').toString());
    const want = [1, 2].map(s => `${PTS * s}x${PTS * s * count}`).join(' ');
    if (reps.join(' ') !== want) out.push(`${rid}: 그림판 ${reps.join(' ')} (${want} 이어야 함)`);
  }
  return out;
}

(async () => {
  const t0 = Date.now(), fails = [];
  let n = 0;
  for (const s of schemes) for (const sh of shapes) {
    // 색조 돌리기 길도 한 번씩 지나가게, 모양마다 구성표 하나는 120° 로 누른다
    const hue = s === schemes[shapes.indexOf(sh) % schemes.length] ? 120 : 0;
    const r = await press(s.id, sh.id, hue);
    n++;
    const why = [...r.bad];
    // 모양 쪽에 없는 칸은 기본 것으로 넘어가는 게 정상이라, 넘어갈 데도 없는 파일만 적는다
    const lost = r.missing.filter(u => !u.includes(`/${sh.id}/`));
    if (!r.xml) why.push(`구워지지 않음: ${r.err && r.err.message}` + (lost.length ? ` (없는 파일 ${lost.join(', ')})` : ''));
    else why.push(...check(r.xml));
    if (why.length) fails.push(`${s.id} × ${sh.id}: ${[...new Set(why)].slice(0, 5).join(' · ')}`);
  }
  console.log(`맥용 .cape ${n}벌 구움 (구성표 ${schemes.length}종 × 모양 ${shapes.length}가지) · 실패 ${fails.length} · ${((Date.now() - t0) / 1000).toFixed(1)}초`);
  fails.slice(0, 30).forEach(f => console.log('  ' + f));
  process.exit(fails.length ? 1 : 0);
})();
