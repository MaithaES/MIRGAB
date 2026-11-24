/* Mirgab AI engine - browser port of the Python engine (mirgab/engine.py).
 * Same knowledge base, same trained model weights, same fusion logic.
 * Usage: const E = MirgabEngine(data); E.analyze({text, url})
 */
(function (root) {
  function MirgabEngine(D) {
    // ---------------- text.py ----------------
    const DIAC = /[ً-ْٰـ]/g;
    function normalize(t) {
      t = (t || "").toLowerCase().replace(DIAC, "");
      t = t.replace(/[إأآٱ]/g, "ا").replace(/ة/g, "ه").replace(/ى/g, "ي").replace(/ؤ/g, "و").replace(/ئ/g, "ي");
      t = t.replace(/[٠-٩]/g, (d) => String("٠١٢٣٤٥٦٧٨٩".indexOf(d)));
      return t.replace(/\s+/g, " ").trim();
    }
    const URL_RE = /(https?:\/\/[^\s<>"']+|www\.[^\s<>"']+|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|ae|net|org|xyz|top|shop|online|site|info|io|co|me|live|vip|club|abudhabi|link|click|ly|gl)(?:\/[^\s<>"']*)?)/gi;
    function extractUrls(text) {
      const out = [];
      for (const m of (text || "").matchAll(URL_RE)) {
        const u = m[0].replace(/[.,;:!?)\]}،]+$/, "");
        if (u.includes("@") && !u.includes("/")) continue;
        if (!out.includes(u)) out.push(u);
      }
      return out;
    }
    const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    function contains(norm, p) {
      if (/^[a-z0-9 ]+$/.test(p)) return new RegExp("(?<![a-z0-9])" + esc(p) + "(?![a-z0-9])").test(norm);
      return norm.includes(p);
    }
    function detectIndicators(text) {
      const norm = normalize(text);
      let flags = [], trust = [];
      for (const [id, cat, w, pats, en, ar] of D.rules) {
        const hits = pats.filter((p) => contains(norm, p));
        if (hits.length) flags.push({ id, category: cat, weight: w, evidence: hits.slice(0, 3), en, ar, source: "text" });
      }
      for (const [id, w, pats, en, ar] of D.trust) {
        const hits = pats.filter((p) => contains(norm, p));
        if (hits.length) trust.push({ id, weight: w, evidence: hits.slice(0, 3), en, ar, source: "text" });
      }
      if (trust.some((t) => t.id === "never_ask")) flags = flags.filter((f) => f.id !== "sensitive_data");
      const m = norm.match(/(villa|فيلا|apartment|شقه)[^.\n]{0,60}?(\d[\d,]{2,})\s*(aed|dhs|درهم)/);
      if (m) {
        const price = parseInt(m[2].replace(/,/g, ""), 10);
        if (price < 1500 && (norm.includes("month") || norm.includes("شهري") || norm.includes("شهر")))
          flags.push({ id: "re_price_math", category: "real_estate", weight: 0.25, evidence: [m[0].slice(0, 50)],
            en: `Rent of ${price} AED/month for this property type is unrealistic`,
            ar: `إيجار ${price} درهم شهرياً لهذا النوع من العقارات غير واقعي`, source: "text" });
      }
      return [flags, trust];
    }

    // ---------------- url_analyzer.py ----------------
    const HOMO = { "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a" };
    function lev(a, b) {
      if (a === b) return 0;
      let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
      for (let i = 1; i <= a.length; i++) {
        const cur = [i];
        for (let j = 1; j <= b.length; j++) cur.push(Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] !== b[j - 1] ? 1 : 0)));
        prev = cur;
      }
      return prev[b.length];
    }
    function splitHost(host) {
      host = host.toLowerCase().replace(/^\.+|\.+$/g, "");
      const L = host.split(".");
      if (L.length < 2) return ["", host, ""];
      const last2 = L.slice(-2).join(".");
      if (D.multiSuffix.includes(last2) && L.length >= 3) return [L.slice(0, -3).join("."), L.slice(-3).join("."), last2];
      return [L.slice(0, -2).join("."), last2, L[L.length - 1]];
    }
    function parse(url) {
      const m = url.match(/^([a-z][a-z0-9+.-]*):\/\/([^/?#]*)([^?#]*)(?:\?([^#]*))?/i) || [];
      const netloc = m[2] || "";
      let hp = netloc.includes("@") ? netloc.slice(netloc.lastIndexOf("@") + 1) : netloc;
      let port = null;
      const pm = hp.match(/^(.*?):(\d+)$/);
      if (pm && !hp.startsWith("[")) { hp = pm[1]; port = parseInt(pm[2], 10); }
      return { scheme: (m[1] || "").toLowerCase(), netloc, host: hp.replace(/^\[|\]$/g, "").toLowerCase(), port, path: m[3] || "", query: m[4] || "" };
    }
    const flag = (id, weight, en, ar, evidence = [], category = "generic") => ({ id, category, weight, evidence, en, ar, source: "url" });
    const isIP = (h) => /^(\d{1,3}\.){3}\d{1,3}$/.test(h) || (h.includes(":") && /^[0-9a-f:]+$/.test(h));

    function analyzeUrl(raw) {
      let url = raw.trim(), schemeGiven = true;
      if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(url)) { url = "http://" + url; schemeGiven = false; }
      const p = parse(url), host = p.host;
      const flags = [], trust = [];
      const res = { url: raw, host, flags, trust, official: null, isMaps: false, reg: "" };
      if (!host) { flags.push(flag("bad_url", 0.3, "Malformed URL", "رابط غير سليم")); return res; }
      const ip = isIP(host);
      if (ip) flags.push(flag("ip_host", 0.45, "Uses a raw IP address instead of a domain name", "يستخدم عنوان IP مباشرة بدلاً من اسم نطاق", [host]));
      const [sub, reg, tld] = ip ? ["", host, ""] : splitHost(host);
      res.reg = reg;
      const label = reg.split(".")[0];
      if (!ip && D.official[reg]) {
        res.official = D.official[reg];
        trust.push({ id: "official_domain", weight: 0.45, evidence: [reg], en: `Official domain of ${D.official[reg]}`, ar: `النطاق الرسمي لجهة ${D.official[reg]}`, source: "url" });
      } else if (!ip && tld.endsWith("gov.ae")) {
        trust.push({ id: "gov_tld", weight: 0.35, evidence: [reg], en: "UAE government domain (.gov.ae)", ar: "نطاق حكومي إماراتي (.gov.ae)", source: "url" });
      }
      if ((D.mapsHosts.includes(host) && (host.includes("maps") || p.path.startsWith("/maps"))) || (reg === "google.com" && p.path.startsWith("/maps"))) res.isMaps = true;

      // open redirect
      const qs = new URLSearchParams(p.query);
      for (const key of ["q", "url", "u", "redirect", "redirect_uri", "next", "dest", "continue"]) {
        const vals = qs.getAll(key).filter((v) => /^https?:\/\//.test(v));
        if (vals.length) {
          const inner = analyzeUrl(vals[0]);
          if (!inner.official) {
            flags.push(flag("redirect", 0.35, "Redirects to another (untrusted) site hidden in the link", "يُعيد التوجيه إلى موقع آخر غير موثوق مخفي داخل الرابط", [inner.host]));
            flags.push(...inner.flags);
            trust.length = 0; res.official = null;
          }
          break;
        }
      }
      if (!res.official) {
        const hay = (host + p.path).replace(/[-.]/g, "");
        for (const [kw, off] of Object.entries(D.brands)) {
          if (kw.length <= 5) { if (!new RegExp("(^|[.\\-/_])" + kw + "($|[.\\-/_])").test(host + p.path)) continue; }
          else if (!hay.includes(kw)) continue;
          flags.push(flag("brand_impersonation", 0.65, `Uses the name '${kw}' but is NOT the official site (${off})`, `يستخدم اسم '${kw}' لكنه ليس الموقع الرسمي (${off})`, [host], "impersonation"));
          break;
        }
        const nl = label.split("").map((c) => HOMO[c] || c).join("").replace(/rn/g, "m").replace(/-/g, "");
        for (const off of Object.keys(D.official)) {
          const ol = off.split(".")[0];
          if (ol.length < 4 || ol === label) continue;
          const d = lev(nl, ol);
          if ((d === 0 && nl !== label) || (d > 0 && d <= (ol.length < 7 ? 1 : 2))) {
            flags.push(flag("typosquat", 0.55, `Domain looks like a misspelling of ${off} (${D.official[off]})`, `النطاق يشبه تهجئة خاطئة لـ ${off} (${D.official[off]})`, [reg, off], "impersonation"));
            break;
          }
        }
      }
      if (!res.official && !ip) {
        const dw = [...new Set((sub + "." + label).split(/[.\-]+/))].filter((w) => D.pathWords.includes(w)).sort();
        if (dw.length) flags.push(flag("domain_words", 0.15, "Domain name contains words like: " + dw.join(", "), "اسم النطاق يحتوي على كلمات مثل: " + dw.join("، "), dw));
      }
      if (host.startsWith("xn--") || host.includes(".xn--")) flags.push(flag("punycode", 0.35, "Internationalised (punycode) domain - may hide look-alike letters", "نطاق بترميز Punycode - قد يخفي حروفاً مشابهة", [host]));
      if (D.badTlds.includes(tld.split(".").pop())) flags.push(flag("cheap_tld", 0.20, `Low-cost domain extension often abused (.${tld})`, `امتداد نطاق رخيص يكثر استغلاله (.${tld})`, [tld]));
      if (res.isMaps) { trust.length = 0; res.official = null; }
      if (D.shorteners.includes(reg) || D.shorteners.includes(host)) flags.push(flag("shortener", 0.25, "Shortened link hides the real destination", "رابط مختصر يُخفي الوجهة الحقيقية", [host]));
      if (reg === "goo.gl" && !res.isMaps) flags.push(flag("shortener", 0.15, "Google short link - destination hidden", "رابط Google مختصر - الوجهة مخفية", [host]));
      if (!res.official) {
        if ((label.match(/-/g) || []).length >= 2) flags.push(flag("hyphens", 0.15, "Many hyphens in the domain name", "عدد كبير من الشرطات في اسم النطاق", [reg]));
        if ((label.match(/\d/g) || []).length >= 3) flags.push(flag("digits", 0.10, "Many digits in the domain name", "أرقام كثيرة في اسم النطاق", [reg]));
        if ((sub.match(/\./g) || []).length >= 2) flags.push(flag("deep_sub", 0.15, "Unusually deep sub-domains", "نطاقات فرعية متعددة بشكل غير معتاد", [host]));
        if (schemeGiven && p.scheme === "http") flags.push(flag("no_https", 0.15, "Not using a secure connection (HTTPS)", "لا يستخدم اتصالاً آمناً (HTTPS)"));
      }
      if (p.netloc.includes("@")) flags.push(flag("at_sign", 0.40, "Contains '@' - the real site is after the @", "يحتوي على '@' - الموقع الحقيقي بعد العلامة", [p.netloc]));
      if (p.port && p.port !== 80 && p.port !== 443) flags.push(flag("port", 0.15, `Non-standard port ${p.port}`, `منفذ غير معتاد ${p.port}`));
      if (url.length > 100) flags.push(flag("long_url", 0.08, "Very long URL", "رابط طويل جداً"));
      const pw = new Set((p.path + "?" + p.query).toLowerCase().split(/[/\-_.?=&]+/));
      const hits = [...pw].filter((w) => D.pathWords.includes(w)).sort();
      if (hits.length && !res.official) flags.push(flag("path_words", Math.min(0.08 * hits.length, 0.25), "Link contains phishing-style words: " + hits.slice(0, 4).join(", "), "الرابط يحتوي على كلمات تصيّد: " + hits.slice(0, 4).join("، "), hits.slice(0, 4)));
      if (D.dangerExt.some((e) => p.path.toLowerCase().endsWith(e))) flags.push(flag("download", 0.40, "Link downloads an app/file directly (e.g. APK)", "الرابط يقوم بتنزيل تطبيق أو ملف مباشرة (مثل APK)", [p.path.slice(-20)]));
      return res;
    }

    // ---------------- model.py ----------------
    const M = D.model, vocabIndex = new Map(M.vocab.map((t, i) => [t, i]));
    function predict(text) {
      const toks = (normalize(text).match(/[\p{L}\p{N}\p{M}_]+/gu) || []).filter((t) => t.length >= 2);
      const grams = toks.slice();
      for (let i = 0; i + 1 < toks.length; i++) grams.push(toks[i] + " " + toks[i + 1]);
      const tf = new Map();
      for (const g of grams) { const j = vocabIndex.get(g); if (j !== undefined) tf.set(j, (tf.get(j) || 0) + 1); }
      const x = new Map(); let norm = 0;
      for (const [j, c] of tf) { const v = (1 + Math.log(c)) * M.idf[j]; x.set(j, v); norm += v * v; }
      norm = Math.sqrt(norm) || 1;
      for (const [j, v] of x) x.set(j, v / norm);
      const z = M.classes.map((_, k) => { let s = M.intercept[k]; for (const [j, v] of x) s += v * M.coef[k][j]; return s; });
      const mx = Math.max(...z), ex = z.map((v) => Math.exp(v - mx)), se = ex.reduce((a, b) => a + b, 0);
      const p = {}; M.classes.forEach((c, k) => (p[c] = ex[k] / se));
      const fraud = 1 - (p.legit || 0);
      const fc = M.classes.filter((c) => c !== "legit");
      const cat = fc.reduce((a, b) => (p[b] > p[a] ? b : a));
      const ci = M.classes.indexOf(cat), li = M.classes.indexOf("legit");
      const contribs = [...x].map(([j, v]) => [M.vocab[j], v * (M.coef[ci][j] - M.coef[li][j])]).sort((a, b) => b[1] - a[1]);
      return {
        fraud_probability: fraud, likely_category: cat, known_vocabulary: x.size,
        top_fraud_terms: contribs.slice(0, 6).filter((c) => c[1] > 0.02).map((c) => ({ term: c[0], score: +c[1].toFixed(3) })),
      };
    }

    // ---------------- engine.py ----------------
    const noisyOr = (ws) => 1 - ws.reduce((p, w) => p * (1 - Math.max(0, Math.min(w, 0.95))), 1);
    const level = (s) => { for (const [lo, hi, k, lab] of D.levels) if (lo <= s && s < hi) return [k, lab]; const l = D.levels[D.levels.length - 1]; return [l[2], l[3]]; };

    function analyze({ text = "", url = "" } = {}) {
      text = text.trim(); url = url.trim();
      const found = extractUrls(text).filter((u) => u !== url);
      const urls = (url ? [url] : []).concat(found);
      const onlyUrl = text ? (urls.length > 0 && text.replace(urls[0], "").trim() === "") : !!url;
      const content = onlyUrl ? "" : text;
      let flags = [], trust = [], hasMaps = false, official = null, primaryDomain = "";
      const urlResults = [];
      for (const u of urls.slice(0, 5)) {
        const r = analyzeUrl(u);
        urlResults.push({ url: u, host: r.host, official: r.official });
        flags = flags.concat(r.flags); trust = trust.concat(r.trust);
        hasMaps = hasMaps || r.isMaps; official = official || r.official;
        primaryDomain = primaryDomain || r.reg || r.host;
      }
      if (hasMaps) flags.push({ id: "maps_link", category: "maps", weight: 0.10, evidence: [], source: "url",
        en: "Google Maps link - the map itself is safe, but listing phone numbers/websites can be hijacked",
        ar: "رابط Google Maps - الخريطة آمنة لكن أرقام ومواقع النتائج قد يتم التلاعب بها" });
      if (content) { const [f, t] = detectIndicators(content); flags = flags.concat(f); trust = trust.concat(t); }
      let ml = null;
      if (content && content.length >= 15) { ml = predict(content); ml.reliability = Math.min(1, ml.known_vocabulary / 6); }

      let urlScore = noisyOr(flags.filter((x) => x.source === "url").map((x) => x.weight));
      const ruleScore = noisyOr(flags.filter((x) => x.source === "text").map((x) => x.weight));
      const mlScore = ml ? ml.fraud_probability * ml.reliability : 0;
      const urlTrust = trust.filter((x) => x.source === "url").reduce((a, x) => a + x.weight, 0);
      const textTrust = trust.filter((x) => x.source === "text").reduce((a, x) => a + x.weight, 0);
      urlScore *= 1 - Math.min(urlTrust * 2, 1);
      let combined = noisyOr([urlScore, ruleScore * 0.9, mlScore * 0.75]);
      const trustTotal = Math.min(textTrust + 0.3 * urlTrust, 0.7);
      combined *= 1 - trustTotal;
      const score = Math.round(100 * combined);
      const [lvl, lvlLabel] = level(score);

      const votes = {};
      for (const x of flags) if (x.category !== "generic") votes[x.category] = (votes[x.category] || 0) + x.weight;
      if (ml && ml.fraud_probability > 0.4) votes[ml.likely_category] = (votes[ml.likely_category] || 0) + ml.fraud_probability * 0.6 * ml.reliability;
      let ranked = Object.entries(votes).sort((a, b) => b[1] - a[1]);
      let primary = score < 25 ? "legit" : ranked.length ? ranked[0][0] : ml ? ml.likely_category : "impersonation";
      if (primary !== "legit" && !ranked.length) ranked = [[primary, 1]];
      const tv = ranked.reduce((a, r) => a + r[1], 0) || 1;
      const domains = ranked.slice(0, 3).map(([k, v]) => ({ key: k, ...D.categories[k], share: +(v / tv).toFixed(2) }));
      const impact = { financial: 0, health: 0, identity: 0, social: 0 };
      for (const [k, v] of ranked) for (const d in impact) impact[d] = Math.max(impact[d], D.impact[k][d] * (0.5 + 0.5 * v / tv));
      if (flags.some((x) => x.id === "sensitive_data")) impact.identity = Math.max(impact.identity, 0.9);
      for (const d in impact) impact[d] = Math.round(100 * impact[d] * combined);
      const advKeys = score < 25 ? ["safe"] : domains.map((d) => d.key).filter((k) => D.advice[k]).slice(0, 2).concat(["generic"]);
      return {
        score, level: lvl, level_label: lvlLabel, category: { key: primary, ...D.categories[primary] }, domains, impact,
        reasons: flags.slice().sort((a, b) => b.weight - a.weight),
        trust_signals: trust,
        advice: { en: advKeys.flatMap((k) => D.advice[k].en), ar: advKeys.flatMap((k) => D.advice[k].ar) },
        report_channels: score >= 50 ? D.reporting : null,
        components: { url: Math.trunc(urlScore * 100), content_rules: Math.trunc(ruleScore * 100), ml: Math.trunc(mlScore * 100), trust_reduction: Math.trunc(trustTotal * 100) },
        ml, urls: urlResults, official_entity: official, primary_domain: primaryDomain,
      };
    }
    return { analyze, analyzeUrl, predict, normalize };
  }
  if (typeof module !== "undefined" && module.exports) module.exports = MirgabEngine;
  else root.MirgabEngine = MirgabEngine;
})(this);
