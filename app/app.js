"use strict";

/* ================= state ================= */
const S = {
  catalog: null,
  progress: null,
  track: null,          // id of track shown in the sidebar
  lesson: null,         // current lesson payload
  saveTimer: null,
  busy: false,
};

const $ = (sel, root) => (root || document).querySelector(sel);
const el = (tag, attrs, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) n.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) {
    if (k == null || k === false) continue;
    n.append(k instanceof Node ? k : document.createTextNode(String(k)));
  }
  return n;
};
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function store(key, val) {
  try {
    if (val === undefined) return localStorage.getItem("ks-" + key);
    localStorage.setItem("ks-" + key, val);
  } catch (e) { return null; }
}

/* ================= api ================= */
async function api(path, body) {
  const opts = body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  };
  let res;
  try { res = await fetch(path, opts); }
  catch (e) { throw new Error("Can't reach the Keystone server. Is its window still open?"); }
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) throw new Error(data.error || ("HTTP " + res.status));
  return data;
}

/* ================= python highlighter ================= */
const KW = new Set(("False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield match case").split(" "));
const BI = new Set(("print len range int float str bool list dict set tuple type input abs min max sum sorted reversed enumerate zip map filter round open isinstance any all repr id hash iter next super object Exception ValueError TypeError KeyError IndexError ZeroDivisionError NameError AttributeError RuntimeError StopIteration self").split(" "));

function highlight(code) {
  const re = /(#[^\n]*)|("""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|[rRbBfF]{0,2}"(?:\\.|[^"\\\n])*"?|[rRbBfF]{0,2}'(?:\\.|[^'\\\n])*'?)|(\b\d[\d_]*\.?\d*(?:e[+-]?\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)/g;
  let out = "", last = 0, m;
  while ((m = re.exec(code))) {
    out += esc(code.slice(last, m.index));
    const t = m[0];
    if (m[1]) out += `<span class="tok-com">${esc(t)}</span>`;
    else if (m[2]) out += `<span class="tok-str">${esc(t)}</span>`;
    else if (m[3]) out += `<span class="tok-num">${esc(t)}</span>`;
    else if (KW.has(t)) out += `<span class="tok-kw">${t}</span>`;
    else if (BI.has(t)) out += `<span class="tok-bi">${t}</span>`;
    else if (code[re.lastIndex] === "(") out += `<span class="tok-fn">${t}</span>`;
    else out += esc(t);
    last = re.lastIndex;
  }
  return out + esc(code.slice(last));
}

/* ================= sql highlighter ================= */
const SQLKW = new Set(("select from where and or not in is null as order by asc desc limit offset group having distinct join inner left right outer full cross on using insert into values update set delete create table drop alter add column primary key foreign references unique check default index view if exists between like glob case when then else end begin commit rollback transaction with recursive union all except intersect explain query plan integer text real blob numeric autoincrement over partition rows range preceding following current row pragma").split(" "));
const SQLFN = new Set(("count sum avg min max round abs length lower upper trim substr replace coalesce ifnull nullif date time datetime strftime julianday printf row_number rank dense_rank lag lead total cast typeof instr group_concat").split(" "));

function highlightSql(code) {
  const re = /(--[^\n]*|\/\*[\s\S]*?(?:\*\/|$))|('(?:''|[^'])*'?)|(\b\d+\.?\d*\b)|([A-Za-z_][A-Za-z0-9_]*)/g;
  let out = "", last = 0, m;
  while ((m = re.exec(code))) {
    out += esc(code.slice(last, m.index));
    const t = m[0];
    if (m[1]) out += `<span class="tok-com">${esc(t)}</span>`;
    else if (m[2]) out += `<span class="tok-str">${esc(t)}</span>`;
    else if (m[3]) out += `<span class="tok-num">${esc(t)}</span>`;
    else if (SQLKW.has(t.toLowerCase())) out += `<span class="tok-kw">${t}</span>`;
    else if (SQLFN.has(t.toLowerCase())) out += `<span class="tok-fn">${t}</span>`;
    else out += esc(t);
    last = re.lastIndex;
  }
  return out + esc(code.slice(last));
}

function highlightFor(lang) {
  if (lang === "sql") return highlightSql;
  if (lang === "python" || lang === "py" || !lang) return highlight;
  return esc;
}

/* ================= markdown ================= */
function inline(s) {
  const codes = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return "\u0000" + (codes.length - 1) + "\u0000"; });
  s = esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*\w])\*(?!\s)(.+?)\*(?!\w)/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => "<code>" + esc(codes[+i]) + "</code>");
}

function markdown(src) {
  const lines = src.replace(/\r\n/g, "\n").split("\n");
  let html = "", i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^```/.test(line)) {
      const lang = line.slice(3).trim();
      const buf = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
      i++;
      const code = buf.join("\n");
      html += `<pre><code>${lang === "python" || lang === "py" ? highlight(code) : lang === "sql" ? highlightSql(code) : esc(code)}</code></pre>`;
      continue;
    }
    if (/^#{1,3} /.test(line)) {
      const n = line.match(/^#+/)[0].length + 1;
      html += `<h${n}>${inline(line.replace(/^#+ /, ""))}</h${n}>`;
      i++; continue;
    }
    if (/^> ?/.test(line)) {
      const buf = [];
      while (i < lines.length && /^> ?/.test(lines[i])) buf.push(lines[i++].replace(/^> ?/, ""));
      html += `<blockquote>${markdown(buf.join("\n"))}</blockquote>`;
      continue;
    }
    if (/^\|/.test(line)) {
      const rows = [];
      while (i < lines.length && /^\|/.test(lines[i])) rows.push(lines[i++]);
      const cells = r => r.replace(/^\||\|$/g, "").split("|").map(c => c.trim());
      let t = "<table><thead><tr>" + cells(rows[0]).map(c => `<th>${inline(c)}</th>`).join("") + "</tr></thead><tbody>";
      for (const r of rows.slice(2)) t += "<tr>" + cells(r).map(c => `<td>${inline(c)}</td>`).join("") + "</tr>";
      html += t + "</tbody></table>";
      continue;
    }
    if (/^\s*([-*]|\d+\.) /.test(line)) {
      const ordered = /^\s*\d+\./.test(line);
      const items = [];
      while (i < lines.length && /^\s*([-*]|\d+\.) /.test(lines[i])) {
        let item = lines[i++].replace(/^\s*([-*]|\d+\.) /, "");
        while (i < lines.length && /^ {2,}\S/.test(lines[i]) && !/^\s*([-*]|\d+\.) /.test(lines[i])) item += " " + lines[i++].trim();
        items.push(`<li>${inline(item)}</li>`);
      }
      html += ordered ? `<ol>${items.join("")}</ol>` : `<ul>${items.join("")}</ul>`;
      continue;
    }
    if (!line.trim()) { i++; continue; }
    const buf = [];
    while (i < lines.length && lines[i].trim() && !/^(```|#{1,3} |> ?|\||\s*([-*]|\d+\.) )/.test(lines[i])) buf.push(lines[i++]);
    html += `<p>${inline(buf.join(" "))}</p>`;
  }
  return html;
}

/* ================= toasts & dialogs ================= */
function toast(html, ms) {
  const t = el("div", { class: "toast", html });
  $("#toasts").append(t);
  setTimeout(() => t.remove(), ms || 4200);
}
function showDialog(node) {
  const body = $("#dialogBody");
  body.innerHTML = "";
  body.append(node);
  $("#dialog").showModal();
}

/* ================= top bar ================= */
function renderTop() {
  const p = S.progress;
  if (!p) return;
  $("#levelNum").textContent = "Lv " + p.level;
  const span = p.level_next - p.level_floor;
  $("#xpFill").style.width = Math.min(100, ((p.xp - p.level_floor) / span) * 100) + "%";
  $("#xpText").textContent = `${p.xp} / ${p.level_next} XP`;
  $("#streakNum").textContent = p.streak;
  $("#streakStat").classList.toggle("on", p.active_today);
  $("#streakStat").title = p.active_today
    ? `Daily streak: ${p.streak} day(s). Done for today.`
    : `Daily streak: ${p.streak} day(s). Finish a lesson today to keep it going.`;
}

function applyProgress(newP) {
  const old = S.progress;
  S.progress = newP;
  renderTop();
  if (old && newP.level > old.level) {
    toast(`<b>Level up!</b> You're now level ${newP.level}.`, 5500);
  }
  if (old && newP.streak > old.streak && newP.streak > 1) {
    toast(`<b>${newP.streak}-day streak.</b> Keep it going tomorrow.`);
  }
}

function announce(res) {
  if (res.first_time && res.earned > 0) toast(`<b>+${res.earned} XP</b> Lesson complete.`);
  else if (res.first_time) toast(`<b>Lesson complete.</b> No XP this time, since you viewed the solution.`);
  for (const a of res.new_achievements || []) toast(`<b>Achievement:</b> ${esc(a.title)}<br><span class="muted">${esc(a.desc)}</span>`, 6000);
  if (res.progress) applyProgress(res.progress);
  renderSidebar();
}

/* ================= sidebar ================= */
function trackOf(lessonId) { return lessonId ? lessonId.split(":")[0] : null; }

// Lessons that sit behind the furthest one you've finished but aren't done:
// usually stepping stones added in an update. They're optional catch-ups,
// and "Continue" ignores them so an update never moves your place.
function catchUpIds() {
  // Worked out per track, so starting another track early doesn't flag
  // everything you haven't reached yet in this one.
  if (!S.progress || !S.catalog) return new Set();
  const done = new Set(S.progress.done);
  const out = new Set();
  for (const track of S.catalog.tracks) {
    const ids = track.chapters.flatMap(c => c.lessons.map(l => l.id));
    let furthest = -1;
    ids.forEach((id, i) => { if (done.has(id)) furthest = i; });
    ids.slice(0, Math.max(furthest, 0)).forEach(id => { if (!done.has(id)) out.add(id); });
  }
  return out;
}

function renderSidebar() {
  const sb = $("#sidebar");
  const cat = S.catalog;
  if (!cat) return;
  const done = new Set(S.progress ? S.progress.done : []);
  if (!S.track) S.track = store("track") || cat.tracks[0].id;
  const track = cat.tracks.find(t => t.id === S.track) || cat.tracks[0];
  const openState = JSON.parse(store("open-" + track.id) || "{}");

  sb.innerHTML = "";
  const tabs = el("div", { class: "track-tabs" });
  cat.tracks.forEach((t, n) => tabs.append(el("button", {
    class: "track-tab" + (t.id === track.id ? " active" : ""),
    title: t.title,
    onclick: () => { S.track = t.id; store("track", t.id); renderSidebar(); },
  }, `${n + 1}. ${t.title}`)));
  sb.append(tabs);

  const catchUp = catchUpIds();
  const all = track.chapters.flatMap(c => c.lessons.map(l => l.id));
  const pct = all.length ? Math.round(all.filter(i => done.has(i)).length / all.length * 100) : 0;
  sb.append(el("div", { class: "track-head" },
    el("h2", {}, track.title, " ", track.playable ? null : el("span", { class: "badge" }, "Planned")),
    el("p", {}, track.blurb),
    track.prereq ? el("p", {}, "Before this: " + track.prereq) : null,
    track.playable ? el("div", { class: "prog", title: pct + "% complete" }, el("div", { style: `width:${pct}%` })) : null,
  ));

  track.chapters.forEach((ch, ci) => {
    const ids = ch.lessons.map(l => l.id);
    const nDone = ids.filter(i => done.has(i)).length;
    const holdsCurrent = S.lesson && ids.includes(S.lesson.id);
    const isOpen = holdsCurrent || openState[ci] === true || (openState[ci] === undefined && ci === 0 && !S.lesson);
    const d = el("details", { class: "chapter", open: isOpen });
    d.addEventListener("toggle", () => {
      const st = JSON.parse(store("open-" + track.id) || "{}");
      st[ci] = d.open;
      store("open-" + track.id, JSON.stringify(st));
    });
    d.append(el("summary", {},
      el("span", { class: "caret" }, "▸"),
      `${ci + 1}. ${ch.title}`,
      el("span", { class: "count" }, track.playable ? `${nDone}/${ids.length}` : "")));
    if (track.playable) {
      ch.lessons.forEach(l => d.append(el("a", {
        class: "lesson-link" + (done.has(l.id) ? " done" : "") + (S.lesson && S.lesson.id === l.id ? " current" : "") + (catchUp.has(l.id) ? " catchup" : ""),
        href: "#/l/" + encodeURIComponent(l.id),
        title: catchUp.has(l.id) ? "Behind where you've reached. Optional catch-up: it doesn't affect your place." : null,
      }, el("span", { class: "dot", html: done.has(l.id) ? '<svg viewBox="0 0 12 12" width="10"><path d="M2 6.5l2.5 2.5L10 3.5" stroke="#0f1a12" stroke-width="2" fill="none"/></svg>' : "" }),
        l.title, catchUp.has(l.id) ? el("span", { class: "badge catchup-badge" }, "catch-up") : null, el("span", { class: "kind" }, l.kind))));
    } else {
      d.append(el("div", { class: "planned" },
        ch.summary ? el("div", {}, ch.summary) : null,
        el("ul", {}, ch.planned_topics.map(t => el("li", {}, t)))));
    }
    sb.append(d);
  });
}

/* ================= home ================= */
function nextLessonId() {
  const done = new Set(S.progress.done);
  const order = S.catalog.order;
  const last = S.progress.last_lesson;
  if (last && order.includes(last) && !done.has(last)) return last;
  if (last && order.includes(last)) {
    for (let i = order.indexOf(last) + 1; i < order.length; i++) if (!done.has(order[i])) return order[i];
  }
  return order.find(i => !done.has(i)) || null;
}

function renderHome() {
  S.lesson = null;
  const p = S.progress, cat = S.catalog;
  const main = $("#main");
  main.innerHTML = "";
  const nextId = nextLessonId();
  const done = new Set(p.done);
  const home = el("div", { class: "home" });
  home.append(
    el("h1", {}, p.done.length ? "Welcome back" : "Welcome to Keystone"),
    el("p", { class: "sub" }, p.done.length
      ? (p.active_today ? "You've studied today. Anything extra is a bonus." : "One lesson today keeps your streak alive.")
      : "Work through the tracks in order, or jump to whatever you need. Everything is saved on this PC."),
  );
  if (nextId) {
    const meta = cat.tracks.flatMap(t => t.chapters.flatMap(c => c.lessons.map(l => ({ ...l, chapter: c.title, track: t.title })))).find(l => l.id === nextId);
    home.append(el("div", { class: "card", style: "max-width:560px;margin-bottom:22px" },
      el("p", {}, `${meta.track} · ${meta.chapter}`),
      el("h3", {}, meta.title),
      el("div", { class: "next-row" },
        el("a", { class: "btn primary", href: "#/l/" + encodeURIComponent(nextId), style: "text-decoration:none" }, p.done.length ? "Continue" : "Start the first lesson"))));
  }
  const behind = S.catalog.order.filter(id => catchUpIds().has(id));
  if (behind.length) {
    home.append(el("div", { class: "card", style: "max-width:560px;margin-bottom:22px" },
      el("p", {}, "Catch-up lessons"),
      el("h3", {}, `${behind.length} lesson${behind.length === 1 ? "" : "s"} behind where you've reached`),
      el("p", {}, "These are mostly stepping stones added in an update, marked \"catch-up\" in the menu. Everything you've passed is still passed. They're optional for you, and Continue still picks up where you left off."),
      el("div", { class: "next-row" },
        el("a", { class: "btn small", href: "#/l/" + encodeURIComponent(behind[0]), style: "text-decoration:none" }, "Open the first one"))));
  }
  home.append(el("div", { class: "cards" },
    el("div", { class: "card" }, el("p", {}, "Level"), el("div", { class: "big" }, p.level), el("p", {}, `${p.level_next - p.xp} XP to level ${p.level + 1}`)),
    el("div", { class: "card" }, el("p", {}, "Total XP"), el("div", { class: "big" }, p.xp), el("p", {}, `${p.done.length} lessons complete`)),
    el("div", { class: "card" }, el("p", {}, "Current streak"), el("div", { class: "big" }, p.streak), el("p", {}, `Longest: ${p.longest_streak} day(s)`)),
    el("div", { class: "card" }, el("p", {}, "Achievements"), el("div", { class: "big" }, p.achievements.filter(a => a.earned).length + " / " + p.achievements.length),
      el("button", { class: "btn small", onclick: showAchievements }, "View all")),
  ));

  home.append(el("h2", { class: "section-title" }, "Last 16 weeks"));
  const heat = el("div", { class: "heat" });
  const days = new Set(p.days);
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const start = new Date(today); start.setDate(start.getDate() - (16 * 7 - 1));
  // first row is Monday, last cell is today
  const offset = (start.getDay() + 6) % 7;
  start.setDate(start.getDate() - offset);
  for (let d = new Date(start); d <= today; d.setDate(d.getDate() + 1)) {
    const iso = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    heat.append(el("span", { class: (days.has(iso) ? "on" : "") + (d.getTime() === today.getTime() ? " today" : ""), title: iso }));
  }
  home.append(heat);

  home.append(el("h2", { class: "section-title" }, "Tracks"));
  const cards = el("div", { class: "cards" });
  cat.tracks.forEach((t, n) => {
    const ids = t.chapters.flatMap(c => c.lessons.map(l => l.id));
    const nd = ids.filter(i => done.has(i)).length;
    cards.append(el("div", { class: "card" },
      el("h3", {}, `${n + 1}. ${t.title}`),
      el("p", {}, t.blurb),
      t.playable
        ? el("div", {}, el("div", { class: "prog" }, el("div", { style: `width:${ids.length ? nd / ids.length * 100 : 0}%` })),
            el("p", { style: "margin-top:6px" }, `${nd} of ${ids.length} lessons · ${t.chapters.length} chapters`))
        : el("p", {}, el("span", { class: "badge" }, "Planned"), ` ${t.chapters.length} chapters outlined`),
      el("button", { class: "btn small", onclick: () => { S.track = t.id; store("track", t.id); renderSidebar(); $("#sidebar").classList.remove("hidden"); } }, "Open in menu"),
    ));
  });
  home.append(cards);
  home.append(el("p", { class: "muted", style: "margin-top:30px;font-size:13px" },
    el("button", { class: "btn small", onclick: resetAll }, "Reset all progress"),
    "  A backup of your old progress is kept in the data folder."));
  main.append(home);
  renderSidebar();
}

function showAchievements() {
  const box = el("div", {}, el("h2", { style: "margin-top:0" }, "Achievements"));
  S.progress.achievements.forEach(a => box.append(el("div", { class: "ach" + (a.earned ? " got" : "") },
    el("div", { class: "medal" }, a.earned ? "★" : "?"),
    el("div", {}, el("div", { style: "font-weight:600" }, a.title), el("div", { class: "muted", style: "font-size:13px" }, a.desc)),
    el("div", { class: "when" }, a.earned || ""))));
  showDialog(box);
}

async function resetAll() {
  const typed = prompt("This clears all XP, streaks and saved code. Type RESET to confirm.");
  if (typed !== "RESET") return;
  try {
    await api("/api/reset-all", { confirm: "RESET" });
    S.progress = await api("/api/progress");
    renderTop(); renderHome();
    toast("Progress reset. Your old data was backed up.");
  } catch (e) { toast(esc(e.message)); }
}

/* ================= lesson view ================= */
async function openLesson(id) {
  let les;
  try { les = await api("/api/lesson?id=" + encodeURIComponent(id)); }
  catch (e) { $("#main").innerHTML = `<div class="home"><h1>Couldn't open that lesson</h1><p>${esc(e.message)}</p></div>`; return; }
  S.lesson = les;
  S.track = les.track; store("track", les.track);
  if (window.innerWidth <= 900) $("#sidebar").classList.add("hidden");
  renderSidebar();
  const main = $("#main");
  main.innerHTML = "";

  const reading = el("div", { class: "reading" },
    el("div", { class: "crumb" }, `${trackTitle(les.track)} · ${les.chapter}`),
    el("h1", {}, les.title),
    el("div", { class: "md", html: markdown(les.body || "") }));

  if (les.kind === "code") {
    reading.append(el("div", { class: "hints", id: "hintBox" }));
    main.append(el("div", { class: "lesson" }, reading, buildWorkbench(les)));
    renderHints(les.hints, les.hint_count);
  } else if (les.kind === "quiz") {
    reading.append(buildQuiz(les));
    main.append(el("div", { class: "lesson single" }, reading));
  } else {
    if (les.widget && les.widget.startsWith("packages")) reading.append(buildPackagePanel(les.widget.split(":")[1] || "engineering"));
    reading.append(el("div", { class: "next-row" },
      les.state.done
        ? el("span", { class: "muted" }, "Completed.")
        : el("button", { class: "btn primary", onclick: async (ev) => {
            ev.target.disabled = true;
            try { announce(await api("/api/read", { id: les.id })); goNext(); }
            catch (e) { toast(esc(e.message)); ev.target.disabled = false; }
          } }, `Mark as read (+${les.xp} XP)`),
      navButtons()));
    main.append(el("div", { class: "lesson single" }, reading));
  }
  reading.scrollTop = 0;
}

function trackTitle(id) { const t = S.catalog.tracks.find(t => t.id === id); return t ? t.title : id; }

function neighbour(delta) {
  const order = S.catalog.order;
  const i = order.indexOf(S.lesson.id);
  return order[i + delta] || null;
}
function goNext() { const n = neighbour(1); location.hash = n ? "#/l/" + encodeURIComponent(n) : "#/"; }
function navButtons() {
  const prev = neighbour(-1), next = neighbour(1);
  return el("span", { style: "display:flex;gap:8px;margin-left:auto" },
    prev ? el("a", { class: "btn small", href: "#/l/" + encodeURIComponent(prev), style: "text-decoration:none" }, "← Previous") : null,
    next ? el("a", { class: "btn small", href: "#/l/" + encodeURIComponent(next), style: "text-decoration:none" }, "Next →") : null);
}

/* ---------- quiz ---------- */
function buildQuiz(les) {
  const wrap = el("div", {});
  wrap.append(el("div", { class: "md", html: markdown(les.question) }));
  const opts = el("div", { class: "quiz-opts" });
  const result = el("div", {});
  let locked = les.state.done;
  les.options.forEach((o, n) => {
    const b = el("button", { class: "quiz-opt", html: inline(o) });
    if (les.state.done && n === les.answer) b.classList.add("right");
    b.addEventListener("click", async () => {
      if (locked) return;
      try {
        const res = await api("/api/answer", { id: les.id, choice: n });
        if (res.correct) {
          locked = true;
          b.classList.add("right");
          result.innerHTML = "";
          result.append(el("div", { class: "banner good" }, "Correct."),
            res.explain ? el("div", { class: "md", html: markdown(res.explain) }) : "",
            el("div", { class: "next-row" }, el("button", { class: "btn primary", onclick: goNext }, "Continue →")));
          announce(res);
        } else {
          b.classList.add("wrong");
          b.disabled = true;
          result.innerHTML = "";
          result.append(el("div", { class: "banner bad" }, "Not quite. Have another look and try again."));
        }
      } catch (e) { toast(esc(e.message)); }
    });
    opts.append(b);
  });
  wrap.append(opts, result);
  if (les.state.done && les.explain) {
    result.append(el("div", { class: "banner good" }, "Completed."), el("div", { class: "md", html: markdown(les.explain) }));
  }
  wrap.append(el("div", { class: "next-row" }, navButtons()));
  return wrap;
}

/* ---------- package installer panel (engineering track) ---------- */
function buildPackagePanel(group) {
  const box = el("div", { class: "pkg-panel" }, el("p", { class: "muted" }, "Checking which packages are installed..."));
  let timer = null;
  const draw = st => {
    box.innerHTML = "";
    const missing = st.packages.filter(p => !p.installed);
    box.append(
      el("h3", {}, "Packages on this computer"),
      el("table", {}, el("tbody", {}, st.packages.map(p => el("tr", {},
        el("td", {}, el("code", {}, p.name)),
        el("td", { class: p.installed ? "ok" : "missing" }, p.installed ? `installed (${p.version})` : "not installed"))))),
      el("p", { class: "muted" }, `Keystone is running on Python ${st.python}.`));
    if (st.running) {
      box.append(el("p", {}, "Installing. This can take a few minutes on a slow connection..."));
    } else if (missing.length) {
      box.append(el("button", { class: "btn primary", onclick: async ev => {
        ev.target.disabled = true;
        try { await api("/api/install-packages", { group }); poll(); }
        catch (e) { toast(esc(e.message)); ev.target.disabled = false; }
      } }, `Install ${missing.map(p => p.name).join(", ")}`));
    } else {
      box.append(el("p", { class: "ok" }, "Everything this track needs is installed."));
    }
    if (st.log) box.append(el("pre", { class: "pkg-log" }, st.log));
  };
  const poll = async () => {
    clearTimeout(timer);
    try {
      const st = await api("/api/packages?group=" + encodeURIComponent(group));
      if (!box.isConnected && timer !== null) return;  // lesson closed meanwhile
      draw(st);
      if (st.running) timer = setTimeout(poll, 2000);
    } catch (e) { box.innerHTML = ""; box.append(el("p", {}, "Couldn't check packages: " + e.message)); }
  };
  poll();
  return box;
}

/* ---------- code workbench ---------- */
function buildWorkbench(les) {
  const initial = les.state.code != null ? les.state.code : les.starter;
  const ta = el("textarea", { spellcheck: "false", autocapitalize: "off", autocomplete: "off", "aria-label": "Code editor" });
  const pre = el("pre", { "aria-hidden": "true" });
  const gutter = el("div", { class: "gutter" });
  ta.value = initial;
  const paint = highlightFor(les.lang);

  const sync = () => {
    pre.innerHTML = paint(ta.value) + "\n";
    const n = ta.value.split("\n").length;
    gutter.textContent = Array.from({ length: n }, (_, i) => i + 1).join("\n");
    pre.scrollTop = ta.scrollTop; pre.scrollLeft = ta.scrollLeft;
    gutter.scrollTop = ta.scrollTop;
  };
  ta.addEventListener("input", () => { sync(); scheduleSave(les.id, ta.value); });
  ta.addEventListener("scroll", () => { pre.scrollTop = ta.scrollTop; pre.scrollLeft = ta.scrollLeft; gutter.scrollTop = ta.scrollTop; });
  ta.addEventListener("keydown", e => editorKeys(e, ta, sync, les));
  sync();

  const out = el("div", { class: "console", id: "console" },
    el("p", { class: "label" }, "Output"),
    el("p", { class: "muted" }, les.state.done
      ? "You've already passed this one. Feel free to experiment."
      : les.lang === "sql" ? "Run your query to see the rows it returns. Submit when you think it's right."
      : les.lang === "text" ? "Type your answer, then Submit. There's nothing to run for this one."
      : "Run your code to see what it prints. Submit when you think it's right."),
    el("p", { class: "kbd" }, "Shortcuts: Ctrl+Enter runs, Ctrl+Shift+Enter submits."));

  const hintBtn = el("button", { class: "btn", id: "hintBtn", onclick: () => getHint(les) }, "Hint");
  const solBtn = el("button", { class: "btn", id: "solBtn", disabled: !les.solution_unlocked, title: "Unlocks after 3 failed submissions", onclick: () => getSolution(les, ta, sync) }, "Solution");

  const bar = el("div", { class: "toolbar" },
    el("button", { class: "btn", title: "Ctrl+Enter", onclick: () => doRun(les, ta) }, "Run"),
    el("button", { class: "btn primary", title: "Ctrl+Shift+Enter", onclick: () => doSubmit(les, ta) }, "Submit"),
    el("span", { class: "spacer" }),
    hintBtn, solBtn,
    el("button", { class: "btn", title: "Put the starter code back", onclick: async () => {
      if (!confirm("Replace your code with the starter code?")) return;
      const r = await api("/api/reset-lesson", { id: les.id });
      ta.value = r.starter; sync();
    } }, "Reset"));

  const editor = el("div", { class: "editor" }, gutter, el("div", { class: "code-wrap" }, pre, ta));
  const bench = el("div", { class: "workbench" }, bar, editor, out);
  setTimeout(() => ta.focus(), 50);
  updateHintBtn(les);
  return bench;
}

function editorKeys(e, ta, sync, les) {
  const IND = "    ";
  const { selectionStart: s, selectionEnd: en, value: v } = ta;
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    if (e.shiftKey) doSubmit(les, ta); else doRun(les, ta);
    return;
  }
  const insert = (text, selS, selE) => {
    ta.setRangeText(text, selS, selE, "end");
    ta.dispatchEvent(new Event("input"));
  };
  if (e.key === "Tab") {
    e.preventDefault();
    const lineStart = v.lastIndexOf("\n", s - 1) + 1;
    if (s === en && !e.shiftKey) { insert(IND, s, en); return; }
    // indent or dedent every selected line
    const lineEnd = v.indexOf("\n", en - (en > s && v[en - 1] === "\n" ? 1 : 0));
    const end = lineEnd === -1 ? v.length : lineEnd;
    const block = v.slice(lineStart, end).split("\n");
    const changed = block.map(l => e.shiftKey ? l.replace(/^ {1,4}/, "") : IND + l).join("\n");
    ta.setRangeText(changed, lineStart, end, "select");
    ta.dispatchEvent(new Event("input"));
    return;
  }
  if (e.key === "Enter" && s === en) {
    e.preventDefault();
    const lineStart = v.lastIndexOf("\n", s - 1) + 1;
    const line = v.slice(lineStart, s);
    let indent = line.match(/^ */)[0];
    if (/:\s*(#.*)?$/.test(line)) indent += IND;
    insert("\n" + indent, s, en);
    return;
  }
  if (e.key === "Backspace" && s === en && s > 0) {
    const lineStart = v.lastIndexOf("\n", s - 1) + 1;
    const before = v.slice(lineStart, s);
    if (before.length && /^ +$/.test(before)) {
      e.preventDefault();
      const remove = before.length % 4 || 4;
      insert("", s - remove, s);
    }
  }
}

function scheduleSave(id, code) {
  clearTimeout(S.saveTimer);
  S.saveTimer = setTimeout(() => api("/api/save", { id, code }).catch(() => {}), 800);
}

function renderConsole(res, mode) {
  const c = $("#console");
  if (!c) return;
  c.innerHTML = "";
  if (mode === "submit") {
    if (res.passed) c.append(el("div", { class: "banner good" },
      res.first_time ? (res.earned ? `All checks passed. +${res.earned} XP` : "All checks passed.") : "All checks passed again."));
    else c.append(el("div", { class: "banner bad" }, "Not there yet. See which checks failed below."));
    if (res.passed) c.append(el("div", { class: "next-row", style: "margin:0 0 10px" },
      el("button", { class: "btn primary", onclick: goNext }, "Next lesson →")));
  }
  c.append(el("p", { class: "label" }, "Output"));
  c.append(el("pre", {}, res.output ? res.output : el("span", { class: "muted" }, "(nothing printed)")));
  if (res.error) {
    c.append(el("p", { class: "label" }, "Error"));
    c.append(el("pre", { class: "err" }, res.error));
  }
  if (mode === "submit" && res.tests && res.tests.length) {
    c.append(el("p", { class: "label" }, "Checks"));
    res.tests.forEach(t => c.append(el("div", { class: "test " + (t.ok ? "ok" : "no") },
      el("span", { class: "mark" }, t.ok ? "✓" : "✗"),
      el("div", {}, el("div", {}, t.name), t.ok ? null : el("div", { class: "msg" }, t.message)))));
  }
}

async function doRun(les, ta) {
  if (S.busy) return;
  S.busy = true;
  const c = $("#console"); if (c) c.innerHTML = '<p class="muted">Running...</p>';
  try { renderConsole(await api("/api/run", { id: les.id, code: ta.value }), "run"); }
  catch (e) { if (c) c.innerHTML = `<pre class="err">${esc(e.message)}</pre>`; }
  S.busy = false;
}

async function doSubmit(les, ta) {
  if (S.busy) return;
  S.busy = true;
  const c = $("#console"); if (c) c.innerHTML = '<p class="muted">Checking...</p>';
  try {
    const res = await api("/api/submit", { id: les.id, code: ta.value });
    renderConsole(res, "submit");
    if (res.solution_unlocked) { const b = $("#solBtn"); if (b) b.disabled = false; }
    if (res.passed) { les.state.done = true; updateHintBtn(les); }
    else if (res.fails === 3) toast("The solution button is now unlocked, if you want it. Using it means no XP for this exercise.");
    announce(res);
  } catch (e) { if (c) c.innerHTML = `<pre class="err">${esc(e.message)}</pre>`; }
  S.busy = false;
}

function renderHints(hints, total) {
  const box = $("#hintBox");
  if (!box) return;
  box.innerHTML = "";
  hints.forEach((h, n) => box.append(el("div", { class: "hint" }, el("b", {}, `Hint ${n + 1}: `), el("span", { html: inline(h) }))));
}

function updateHintBtn(les) {
  const b = $("#hintBtn");
  if (!b) return;
  const used = les.hints.length, total = les.hint_count;
  if (!total) { b.disabled = true; b.textContent = "No hints"; return; }
  b.disabled = used >= total;
  b.textContent = used >= total ? "No more hints" : `Hint (${used}/${total})`;
  b.title = les.state.done ? "Hints are free once you've passed" : "Each hint costs 20% of this exercise's XP";
}

async function getHint(les) {
  if (!les.state.done && les.hints.length === 0 &&
      !confirm(`Each hint lowers the XP for this exercise by 20%. Show hint 1?`)) return;
  try {
    const r = await api("/api/hint", { id: les.id });
    les.hints = r.hints;
    renderHints(r.hints, r.hint_count);
    updateHintBtn(les);
    const box = $("#hintBox"); if (box && box.lastChild) box.lastChild.scrollIntoView({ behavior: "smooth", block: "nearest" });
    if (!les.state.done) toast(`This exercise is now worth <b>${r.xp_now} XP</b>.`);
  } catch (e) { toast(esc(e.message)); }
}

async function getSolution(les, ta, sync) {
  if (!les.state.done && !confirm("If you view the solution before passing, this exercise gives 0 XP. Show it anyway?")) return;
  try {
    const r = await api("/api/solution", { id: les.id });
    if (r.error) { toast(esc(r.error)); return; }
    const box = el("div", {},
      el("h2", { style: "margin-top:0" }, "Solution"),
      el("p", { class: "muted" }, "This is one correct answer. Yours might look different and still be right."),
      el("div", { class: "md", html: `<pre><code>${highlight(r.solution)}</code></pre>` }),
      el("button", { class: "btn", onclick: () => {
        if (!confirm("Replace your code with the solution?")) return;
        ta.value = r.solution; sync(); scheduleSave(les.id, ta.value); $("#dialog").close();
      } }, "Copy into the editor"));
    showDialog(box);
  } catch (e) { toast(esc(e.message)); }
}

/* ================= router & boot ================= */
async function route() {
  const h = location.hash;
  if (h.startsWith("#/l/")) await openLesson(decodeURIComponent(h.slice(4)));
  else renderHome();
}

async function boot() {
  $("#menuBtn").addEventListener("click", () => {
    const sb = $("#sidebar");
    sb.classList.toggle("hidden");
    store("sidebar", sb.classList.contains("hidden") ? "hidden" : "shown");
  });
  if (store("sidebar") === "hidden") $("#sidebar").classList.add("hidden");
  $("#trophyBtn").addEventListener("click", showAchievements);
  try {
    [S.catalog, S.progress] = await Promise.all([api("/api/catalog"), api("/api/progress")]);
  } catch (e) {
    $("#main").innerHTML = `<div class="home"><h1>Keystone couldn't start</h1><p>${esc(e.message)}</p></div>`;
    return;
  }
  renderTop();
  window.addEventListener("hashchange", route);
  route();
}
boot();
