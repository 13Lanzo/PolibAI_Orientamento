import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const svgDir = path.join(root, 'svg');
const htmlDir = path.join(root, 'html');
const dataDir = path.join(root, 'data');
for (const dir of [svgDir, htmlDir, dataDir]) fs.mkdirSync(dir, { recursive: true });

const C = {
  ink: '#202124', muted: '#5F6368', grid: '#DADCE0', blue: '#0072B2',
  orange: '#E69F00', green: '#009E73', red: '#D55E00', purple: '#CC79A7',
  paleBlue: '#DCEEF8', paleRed: '#F9E1D8', paleGreen: '#DDF3EB', white: '#FFFFFF'
};

const esc = (s) => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const text = (x, y, value, opts = {}) => {
  const { size = 24, anchor = 'start', weight = 400, fill = C.ink, rotate = 0, italic = false } = opts;
  const transform = rotate ? ` transform="rotate(${rotate} ${x} ${y})"` : '';
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" font-size="${size}" font-weight="${weight}" fill="${fill}"${italic ? ' font-style="italic"' : ''}${transform}>${esc(value)}</text>`;
};
const line = (x1, y1, x2, y2, stroke = C.grid, width = 2, dash = '') =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="${width}"${dash ? ` stroke-dasharray="${dash}"` : ''}/>`;
const rect = (x, y, w, h, fill, stroke = 'none', sw = 0, rx = 0) =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" rx="${rx}"/>`;
const circle = (cx, cy, r, fill, stroke = 'none', sw = 0) =>
  `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;

function svgDoc(title, desc, body, width = 1200, height = 700) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="title desc">
<title id="title">${esc(title)}</title><desc id="desc">${esc(desc)}</desc>
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="${C.muted}"/></marker>
</defs>
<style>text{font-family:"Latin Modern Sans","TeX Gyre Heros",Arial,sans-serif} .axis{stroke:${C.ink};stroke-width:2} .arrow{stroke:${C.muted};stroke-width:3;fill:none;marker-end:url(#arrow)}</style>
${body}
</svg>`;
}

function writeFigure(name, title, desc, body, width = 1200, height = 700) {
  const svg = svgDoc(title, desc, body, width, height);
  fs.writeFileSync(path.join(svgDir, `${name}.svg`), svg, 'utf8');
  const html = `<!doctype html><meta charset="utf-8"><style>@page{size:180mm 105mm;margin:0}html,body{margin:0;width:180mm;height:105mm;display:grid;place-items:center;background:white}svg{width:180mm;height:auto;display:block}</style>${svg}`;
  fs.writeFileSync(path.join(htmlDir, `${name}.html`), html, 'utf8');
}

// 1. Utilizzo delle quote (scala logaritmica per rendere visibili valori molto diversi).
{
  const data = [
    { name: 'RPM', value: 0.025, label: '0,025%', color: C.blue },
    { name: 'TPM input', value: 6.5975, label: '6,60%', color: C.orange },
    { name: 'RPD', value: 0.003333, label: '0,0033%', color: C.green }
  ];
  const x0 = 245, x1 = 1100, y0 = 555;
  const xmin = -3, xmax = 2;
  const sx = (v) => x0 + ((Math.log10(v) - xmin) / (xmax - xmin)) * (x1 - x0);
  let b = text(600, 48, 'Utilizzo massimo delle quote Gemini API', { size: 30, anchor: 'middle', weight: 500 });
  b += text(600, 82, 'Picco osservato rispetto al limite disponibile — scala logaritmica', { size: 19, anchor: 'middle', fill: C.muted });
  const ticks = [0.001, 0.01, 0.1, 1, 10, 100];
  for (const t of ticks) {
    const x = sx(t); b += line(x, 115, x, y0, C.grid, 1);
    b += text(x, y0 + 34, `${String(t).replace('.', ',')}%`, { size: 18, anchor: 'middle', fill: C.muted });
  }
  const ys = [190, 325, 460];
  data.forEach((d, i) => {
    const y = ys[i];
    b += text(x0 - 24, y + 9, d.name, { size: 23, anchor: 'end', weight: 500 });
    b += rect(x0, y - 22, Math.max(3, sx(d.value) - x0), 44, d.color, 'none', 0, 4);
    b += circle(sx(d.value), y, 8, d.color);
    b += text(sx(d.value) + 18, y + 8, d.label, { size: 21, weight: 500 });
  });
  b += line(x0, y0, x1, y0, C.ink, 2);
  b += text((x0 + x1) / 2, 645, 'Quota utilizzata (%)', { size: 22, anchor: 'middle', weight: 500 });
  b += text(1120, 150, 'TPM è il vincolo dominante', { size: 18, anchor: 'end', fill: C.orange, weight: 500 });
  writeFigure('quota-utilization', 'Utilizzo massimo delle quote Gemini API', 'RPM 0,025%, TPM 6,60%, RPD 0,0033%. Il consumo TPM è dominante.', b);
}

// 2. Profilo dei token nelle due sessioni. Valori approssimati dalla lettura dei grafici.
{
  const sessions = [
    { name: '8 set.', input: 650000, output: 1100 },
    { name: '17 set.', input: 1300000, output: 2800 }
  ];
  const xCenters = [435, 845], plotTop = 115, plotBottom = 550;
  const ymin = 3, ymax = Math.log10(2000000);
  const sy = (v) => plotBottom - ((Math.log10(v) - ymin) / (ymax - ymin)) * (plotBottom - plotTop);
  let b = text(600, 48, 'Token elaborati nelle sessioni di prova', { size: 30, anchor: 'middle', weight: 500 });
  b += text(600, 82, 'Valori approssimati dai grafici AI Studio — asse verticale logaritmico', { size: 19, anchor: 'middle', fill: C.muted });
  const ticks = [1000, 10000, 100000, 1000000];
  for (const t of ticks) {
    const y = sy(t); b += line(180, y, 1090, y, C.grid, 1);
    const lab = t >= 1000000 ? '1 M' : t >= 1000 ? `${t / 1000} k` : `${t}`;
    b += text(160, y + 7, lab, { size: 18, anchor: 'end', fill: C.muted });
  }
  sessions.forEach((s, i) => {
    const xc = xCenters[i], w = 92;
    const yi = sy(s.input), yo = sy(s.output);
    b += rect(xc - 112, yi, w, plotBottom - yi, C.blue, 'none', 0, 3);
    b += rect(xc + 20, yo, w, plotBottom - yo, C.orange, 'none', 0, 3);
    b += text(xc - 66, yi - 14, `≈${(s.input / 1000000).toLocaleString('it-IT', { maximumFractionDigits: 2 })} M`, { size: 20, anchor: 'middle', weight: 500 });
    b += text(xc + 66, yo - 14, `≈${(s.output / 1000).toLocaleString('it-IT', { maximumFractionDigits: 1 })} k`, { size: 20, anchor: 'middle', weight: 500 });
    b += text(xc, 590, s.name, { size: 22, anchor: 'middle', weight: 500 });
  });
  b += line(180, plotBottom, 1090, plotBottom, C.ink, 2);
  b += rect(430, 628, 24, 18, C.blue); b += text(466, 644, 'Input', { size: 19 });
  b += rect(600, 628, 24, 18, C.orange); b += text(636, 644, 'Output', { size: 19 });
  b += text(38, 335, 'Token', { size: 22, anchor: 'middle', weight: 500, rotate: -90 });
  writeFigure('token-profile', 'Token elaborati nelle sessioni di prova', 'Il volume dei token di input è centinaia di volte superiore all’output.', b);
}

// 3. Saturazione TPM al crescere delle richieste.
{
  const perRequest = 263900, quota = 4000000;
  const x0 = 150, x1 = 1100, y0 = 565, y1 = 115;
  const sx = (x) => x0 + (x / 17) * (x1 - x0);
  const sy = (y) => y0 - (y / 4500000) * (y0 - y1);
  let b = text(600, 48, 'Saturazione della quota TPM', { size: 30, anchor: 'middle', weight: 500 });
  b += text(600, 82, 'Scenario calcolato con 263.900 token di input per richiesta', { size: 19, anchor: 'middle', fill: C.muted });
  for (let x = 0; x <= 16; x += 2) {
    b += line(sx(x), y1, sx(x), y0, C.grid, 1); b += text(sx(x), y0 + 34, x, { size: 18, anchor: 'middle', fill: C.muted });
  }
  for (let m = 0; m <= 4; m++) {
    b += line(x0, sy(m * 1000000), x1, sy(m * 1000000), C.grid, 1);
    b += text(x0 - 18, sy(m * 1000000) + 7, `${m} M`, { size: 18, anchor: 'end', fill: C.muted });
  }
  const points = [];
  for (let x = 0; x <= 17; x += 0.25) points.push(`${sx(x)},${sy(x * perRequest)}`);
  b += `<polyline points="${points.join(' ')}" fill="none" stroke="${C.blue}" stroke-width="5"/>`;
  b += line(x0, sy(quota), x1, sy(quota), C.red, 4, '12 8');
  b += text(x1 - 4, sy(quota) - 14, 'Limite: 4 M TPM', { size: 20, anchor: 'end', fill: C.red, weight: 500 });
  const threshold = quota / perRequest;
  b += line(sx(threshold), y0, sx(threshold), sy(quota), C.red, 2, '7 6');
  b += circle(sx(threshold), sy(quota), 9, C.red);
  b += text(sx(threshold) - 18, sy(quota) + 55, '≈15,2 richieste/min', { size: 21, anchor: 'end', fill: C.red, weight: 500 });
  b += line(x0, y0, x1, y0, C.ink, 2); b += line(x0, y0, x0, y1, C.ink, 2);
  b += text((x0 + x1) / 2, 650, 'Richieste AI al minuto', { size: 22, anchor: 'middle', weight: 500 });
  b += text(42, 335, 'Token input al minuto', { size: 22, anchor: 'middle', weight: 500, rotate: -90 });
  writeFigure('tpm-saturation', 'Saturazione della quota TPM', 'Con 263.900 token per richiesta la quota di 4 milioni TPM è raggiunta a circa 15,2 richieste al minuto.', b);
}

const box = (x, y, w, h, label, fill, sub = '') => {
  let s = rect(x, y, w, h, fill, C.ink, 2, 8);
  s += text(x + w / 2, y + h / 2 - (sub ? 7 : -7), label, { size: 21, anchor: 'middle', weight: 500 });
  if (sub) s += text(x + w / 2, y + h / 2 + 24, sub, { size: 16, anchor: 'middle', fill: C.muted });
  return s;
};
const arrow = (x1, y1, x2, y2, color = C.muted, dash = '') =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="3" marker-end="url(#arrow)"${dash ? ` stroke-dasharray="${dash}"` : ''}/>`;

// 4. Architettura attuale e punto di congestione.
{
  let b = text(600, 45, 'Architettura attuale e origine del collo di bottiglia', { size: 29, anchor: 'middle', weight: 500 });
  b += box(45, 255, 190, 100, 'Angular SPA', C.paleBlue, 'chatbot / advisor');
  b += box(305, 255, 190, 100, 'Flask API', C.paleBlue, 'sincrona');
  b += box(575, 95, 230, 105, 'Knowledge base', C.paleRed, '53 documenti');
  b += box(575, 255, 230, 105, 'Contesto completo', C.paleRed, '≈244k token/richiesta');
  b += box(900, 255, 240, 105, 'Gemini API', C.paleBlue, 'sessione globale');
  b += box(575, 475, 230, 100, 'KPI + cronologia', C.paleRed, 'ripetuti nel prompt');
  b += arrow(235, 305, 305, 305);
  b += arrow(495, 305, 575, 305);
  b += arrow(805, 305, 900, 305, C.red);
  b += arrow(690, 200, 690, 255, C.red);
  b += arrow(690, 475, 690, 360, C.red);
  b += text(852, 278, 'TPM', { size: 19, anchor: 'middle', fill: C.red, weight: 500 });
  b += text(1018, 425, 'Risposta breve', { size: 19, anchor: 'middle', fill: C.green, weight: 500 });
  b += `<path d="M1018 360 C1018 425 400 425 400 355" fill="none" stroke="${C.green}" stroke-width="3" marker-end="url(#arrow)"/>`;
  b += text(600, 650, 'Il corpus è allegato quasi integralmente: il sistema usa long context più che retrieval selettivo.', { size: 20, anchor: 'middle', fill: C.muted, italic: true });
  writeFigure('current-architecture', 'Architettura attuale e collo di bottiglia', 'La knowledge base e i KPI completi sono inviati a Gemini, causando un elevato consumo TPM.', b);
}

// 5. Architettura proposta.
{
  let b = text(600, 45, 'Architettura proposta per l’esercizio multiutente', { size: 29, anchor: 'middle', weight: 500 });
  b += box(35, 270, 165, 95, 'Angular SPA', C.paleBlue, 'streaming');
  b += box(250, 270, 190, 95, 'API gateway', C.paleGreen, 'auth + rate limit');
  b += box(500, 270, 190, 95, 'Intent router', C.paleGreen, 'instradamento');
  b += box(765, 85, 205, 95, 'Servizi locali', C.paleBlue, 'mappe / KPI');
  b += box(765, 255, 205, 95, 'File Search', C.paleGreen, 'top-k documenti');
  b += box(765, 430, 205, 95, 'Session store', C.paleGreen, 'stato per utente');
  b += box(1030, 255, 140, 95, 'Gemini', C.paleBlue, 'prompt ridotto');
  b += arrow(200, 317, 250, 317); b += arrow(440, 317, 500, 317);
  b += arrow(690, 300, 765, 135); b += arrow(690, 317, 765, 302); b += arrow(690, 335, 765, 477);
  b += arrow(970, 302, 1030, 302, C.green);
  b += arrow(970, 477, 1085, 350, C.green);
  b += `<path d="M1100 350 C1100 605 355 605 355 365" fill="none" stroke="${C.green}" stroke-width="3" marker-end="url(#arrow)"/>`;
  b += box(500, 520, 190, 70, 'Telemetry', C.paleBlue, 'latenza + token + errori');
  b += arrow(595, 365, 595, 520);
  b += text(600, 650, 'Retrieval selettivo, isolamento delle sessioni e controllo del carico riducono latenza e rischio di saturazione.', { size: 20, anchor: 'middle', fill: C.muted, italic: true });
  writeFigure('proposed-architecture', 'Architettura proposta', 'Il router usa servizi deterministici oppure recupera pochi frammenti rilevanti prima di chiamare Gemini.', b);
}

// 6. Modello di misura della latenza, senza valori inventati.
{
  let b = text(600, 48, 'Scomposizione della latenza end-to-end', { size: 30, anchor: 'middle', weight: 500 });
  b += text(600, 82, 'Schema di misura consigliato — nessun tempo è stato stimato', { size: 19, anchor: 'middle', fill: C.muted });
  const xs = [105, 285, 475, 710, 930, 1095];
  const labels = ['Invio UI', 'Arrivo Flask', 'Prompt pronto', 'Risposta Gemini', 'JSON pronto', 'Render UI'];
  const colors = [C.blue, C.green, C.orange, C.red, C.purple];
  const segs = ['rete locale', 'pre-processing', 'inferenza / tool', 'post-processing', 'rendering'];
  b += line(xs[0], 315, xs.at(-1), 315, C.ink, 3);
  xs.forEach((x, i) => {
    b += circle(x, 315, 10, i === 3 ? C.red : C.blue);
    b += text(x, i % 2 === 0 ? 255 : 385, `t${i}`, { size: 20, anchor: 'middle', weight: 500 });
    b += text(x, i % 2 === 0 ? 225 : 420, labels[i], { size: 17, anchor: 'middle', fill: C.muted });
  });
  for (let i = 0; i < segs.length; i++) {
    b += rect(xs[i] + 10, 300, xs[i + 1] - xs[i] - 20, 30, colors[i], 'none', 0, 3);
    b += text((xs[i] + xs[i + 1]) / 2, 470 + (i % 2) * 38, segs[i], { size: 17, anchor: 'middle', fill: colors[i], weight: 500 });
  }
  b += text(600, 555, 'T totale = t5 − t0', { size: 24, anchor: 'middle', weight: 500 });
  b += text(600, 595, 'Riportare p50, p95 e p99 per endpoint e livello di concorrenza', { size: 20, anchor: 'middle', fill: C.muted });
  writeFigure('latency-decomposition', 'Scomposizione della latenza end-to-end', 'Timeline dei punti di misura dal browser al rendering della risposta.', b);
}

fs.writeFileSync(path.join(dataDir, 'observed-metrics.csv'), [
  'metric,observed,limit,utilization_percent,precision',
  'RPM,1,4000,0.025,exact_dashboard',
  'TPM_input,263900,4000000,6.5975,exact_dashboard',
  'RPD,5,150000,0.003333,exact_dashboard',
  'input_tokens_2026-09-08,650000,, ,approx_from_graph',
  'output_tokens_2026-09-08,1100,, ,approx_from_graph',
  'requests_2026-09-08,3,, ,approx_from_graph',
  'input_tokens_2026-09-17,1300000,, ,approx_from_graph',
  'output_tokens_2026-09-17,2800,, ,approx_from_graph',
  'requests_2026-09-17,5,, ,exact_dashboard_peak'
].join('\n') + '\n', 'utf8');

fs.writeFileSync(path.join(dataDir, 'tpm-saturation.csv'), [
  'requests_per_minute,input_tokens_per_request,tokens_per_minute,quota_percent',
  ...Array.from({ length: 18 }, (_, rpm) => `${rpm},263900,${rpm * 263900},${((rpm * 263900 / 4000000) * 100).toFixed(4)}`)
].join('\n') + '\n', 'utf8');

console.log(`Generated 6 SVG figures in ${svgDir}`);
