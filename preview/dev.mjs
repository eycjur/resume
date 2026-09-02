// ホットリロード付きプレビューサーバー（Ruby/Jekyll がない環境向けの簡易版）。
// Liquid は liquidjs、SCSS は dart-sass で処理する。ページ本文は raw HTML 前提
// （kramdown の Markdown 変換は行わない）なので、Markdown 記法を本文に書く場合は
// 本物の Jekyll（make jekyll）で確認すること。
import { Liquid } from 'liquidjs';
import * as sass from 'sass';
import fs from 'fs';
import http from 'http';
import path from 'path';
import { fileURLToPath } from 'url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(repo, '_preview');
const PORT = Number(process.env.PORT || 4000);
const HOST = process.env.HOST || '0.0.0.0';

const PAGES = [
  ['ja/index.md', 'ja/index.html'],
  ['en/index.md', 'en/index.html'],
  ['ja/products.md', 'ja/products/index.html'],
];
const WATCH_DIRS = ['ja', 'en', '_layouts', '_includes', '_sass', 'assets'];
const RELOAD_SNIPPET =
  "<script>new EventSource('/__reload').addEventListener('reload',()=>location.reload());</script>";

const engine = new Liquid();
engine.registerTag('seo', {
  parse() {},
  render: (ctx) => `<title>${ctx.environments.page?.title ?? 'preview'}</title>`,
});
engine.registerFilter('relative_url', (v) => v);
engine.registerFilter('append', (v, s) => String(v) + (s ?? ''));

function parseFrontMatter(raw) {
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!m) return { fm: {}, body: raw };
  const fm = Object.fromEntries(
    m[1].split('\n').map((l) => l.split(/:\s+/)).filter((a) => a.length === 2)
  );
  return { fm, body: m[2] };
}

async function buildHTML() {
  const layout = fs
    .readFileSync(path.join(repo, '_layouts/default.html'), 'utf8')
    .replace(/\{%\s*include head-custom.html\s*%\}/, () =>
      fs.readFileSync(path.join(repo, '_includes/head-custom.html'), 'utf8')
    );
  const site = { github: { build_revision: String(Date.now()) } };
  for (const [src, dest] of PAGES) {
    const { fm, body } = parseFrontMatter(fs.readFileSync(path.join(repo, src), 'utf8'));
    const page = { lang: fm.lang, nav: fm.nav, title: fm.title };
    const content = await engine.parseAndRender(body, { page, site });
    let html = await engine.parseAndRender(layout, { page, site, content });
    html = html.replace('</body>', `${RELOAD_SNIPPET}\n</body>`);
    const target = path.join(out, dest);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, html);
  }
  fs.writeFileSync(path.join(out, 'index.html'), '<meta http-equiv="refresh" content="0; url=/ja/">');
}

function buildCSS() {
  const scss = fs
    .readFileSync(path.join(repo, 'assets/css/style.scss'), 'utf8')
    .replace(/^---\n[\s\S]*?\n?---\n/, '');
  const result = sass.compileString(scss, {
    loadPaths: [path.join(repo, '_sass')],
    quietDeps: true,
    silenceDeprecations: ['import'],
  });
  const target = path.join(out, 'assets/css/style.css');
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, result.css);
}

function copyAssets() {
  fs.cpSync(path.join(repo, 'assets/products'), path.join(out, 'assets/products'), {
    recursive: true,
    force: true,
  });
}

const clients = new Set();
function notifyReload() {
  for (const res of clients) res.write('event: reload\ndata: 1\n\n');
}

let building = false;
let pending = null;
async function rebuild(reason, withAssets = false) {
  if (building) {
    pending = reason;
    return;
  }
  building = true;
  try {
    await buildHTML();
    buildCSS();
    if (withAssets) copyAssets();
    console.log(`[${new Date().toLocaleTimeString()}] rebuilt (${reason})`);
    notifyReload();
  } catch (e) {
    console.error(`[build error] ${e.message}`);
  } finally {
    building = false;
    if (pending) {
      const next = pending;
      pending = null;
      rebuild(next);
    }
  }
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.mp4': 'video/mp4',
  '.ico': 'image/x-icon',
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/__reload') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    });
    res.write(': connected\n\n');
    clients.add(res);
    req.on('close', () => clients.delete(res));
    return;
  }
  let filePath = path.join(out, decodeURIComponent(url.pathname));
  if (!filePath.startsWith(out)) {
    res.writeHead(403).end();
    return;
  }
  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, 'index.html');
  }
  if (!fs.existsSync(filePath)) {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('404: ' + url.pathname);
    return;
  }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath)] ?? 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
});

let timer = null;
for (const dir of WATCH_DIRS) {
  fs.watch(path.join(repo, dir), { recursive: true }, (event, filename) => {
    const withAssets = dir === 'assets';
    clearTimeout(timer);
    timer = setTimeout(() => rebuild(`${dir}/${filename ?? ''}`, withAssets), 150);
  });
}

await rebuild('initial', true);
server.listen(PORT, HOST, () => {
  console.log(`preview: http://localhost:${PORT}/ja/ (watching: ${WATCH_DIRS.join(', ')})`);
});
