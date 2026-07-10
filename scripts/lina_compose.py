"""Lina's compose logic — relevance-ranked, COUPLED pain->solution block (option B).

The message uses ONE dynamic slot `{{2}}` that always carries a *coupled* pain + the
NAVAIA solution that addresses THAT pain. The rest of the template is fixed and whole
(greeting, impact + compliance, question close, signature).

Decision (per the boss + user rules):
  - The pain is NOT auto-preferred just because it's specific. RELEVANCE wins.
  - specific pain (lead's own reviews, `pain_line` from enrich_reviews.py) is scored by how
    well it maps to a KNOWN, solvable pain in the vertical's library (keyword match) plus a
    small "grounded in real reviews" bonus.
  - general pain has a constant baseline relevance (it's the vertical's dominant pain, always
    at least decently relevant, and keeps the message WHOLE when there's no specific signal).
  - whichever scores higher wins; its coupled solution rides along. If the specific pain maps
    to nothing we can solve (novel / noise), the GENERAL pair wins — the safe, whole default.

Deterministic by design (OPTIMIZATION.md: scripts, not model calls). An optional LLM step is
left as a stub for genuinely novel specific pains; off by default to control spend.

Usage:
    python scripts/lina_compose.py --self-test
    python scripts/lina_compose.py --in leads_enriched.csv --vertical clinics --limit 20
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Tunables (calibratable; exposed on purpose) ─────────────────────────────
GENERAL_RELEVANCE = 1.0     # baseline relevance of the vertical's general pain
GROUNDED_BONUS = 0.6        # bonus for a specific pain that is grounded in real reviews
PER_KEYWORD = 0.6           # relevance added per matched library keyword
# specific wins iff (matched_keywords*PER_KEYWORD + GROUNDED_BONUS) > GENERAL_RELEVANCE
# → one solid keyword match (0.6) + grounded (0.6) = 1.2 > 1.0 → specific wins
# → zero keyword match (novel/noise) = 0.6 < 1.0 → general wins (more relevant)

# ── Per-vertical pain -> solution library ───────────────────────────────────
# Each category coupled: a solvable pain and the EXACT NAVAIA solution for it.
# `general` is the whole/complete default. Specific categories supply the matched
# SOLUTION; the lead's own `pain_line` supplies the PAIN wording when it matches.
LIBRARY: dict[str, dict] = {
    "clinics": {
        "desc": "عيادة خاصة: ردّ على المراجعين، حجز مواعيد، تذكير وتأكيد، عدم حضور",
        "general": {
            "pain": "بين الاتصالات والرسائل وحجز المواعيد وتذكير المراجعين بها وتأكيدها، قد يفوت العيادة حجزٌ أو يتأخّر ردّ",
            "solution": "ونحن إلى جانب فرقكم نُؤتمت متابعة مراجعيكم ومواعيدهم دون أن تزيد أعباءهم",
        },
        "categories": {
            "no_show": {
                "triggers": ["حضور", "يحضر", "حضر", "تخلف", "غياب", "ما حضر"],
                "desc": "عدم حضور المراجعين لمواعيدهم دون إشعار",
                "pain": "بعض المواعيد لا يحضر أصحابها دون إشعار",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت تذكير مراجعيكم بمواعيدهم وتأكيدها قبلها، فيقلّ عدم الحضور",
            },
            "after_hours": {
                "triggers": ["الدوام", "دوام", "مغلق", "مساء", "الليل", "بالليل"],
                "desc": "لا ردّ على الطلبات بعد ساعات الدوام",
                "pain": "بعض مراجعيكم يطلبون مواعيد بعد الدوام دون ردّ",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت الردّ وحجز المواعيد بعد الدوام، فلا يفوتكم حجز",
            },
            "slow_reply": {
                "triggers": ["تاخر", "الرد", "يرد", "ردو", "انتظار", "بطء", "بدون رد"],
                "desc": "تأخّر أو انعدام الردّ على الاتصالات والرسائل",
                "pain": "تأخّر الردّ على اتصالات مراجعيكم ورسائلهم",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت الردّ الأول عبر قنواتكم فوراً، فلا ينتظر مراجعكم",
            },
            "booking_hard": {
                "triggers": ["الحجز", "احجز", "صعوب", "صعب", "تعقيد"],
                "desc": "صعوبة حجز المواعيد على المراجعين",
                "pain": "صعوبة حجز المواعيد على مراجعيكم",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت الحجز والتأكيد آلياً، فيسهل على مراجعكم تثبيت موعده",
            },
        },
    },
    "contracting": {
        "desc": "مقاولات وصيانة: عروض أسعار، مناقصات وعطاءات، متابعة طلبات العملاء",
        "general": {
            "pain": "بين طلبات عروض الأسعار والمناقصات ومتابعة العطاءات قبل موعد الترسية، قد يفوت الشركةَ عقدٌ لتأخّر ردٍّ أو عرضٍ معلّق",
            "solution": "ونحن إلى جانب فرقكم نُؤتمت متابعة عروضكم وطلبات عملائكم دون أن تزيد أعباءهم",
        },
        "categories": {
            "rfq_slow": {
                "triggers": ["عرض سعر", "تسعير", "سعر", "عروض", "العرض", "rfq"],
                "desc": "تأخّر الردّ على طلبات عروض الأسعار",
                "pain": "تأخّر الردّ على طلبات عروض الأسعار",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت استقبال الطلبات والردّ الأولي عليها فوراً، فلا يفوتكم طلب",
            },
            "tender_deadline": {
                "triggers": ["مناقص", "عطاء", "العطاء", "الترسيه", "ترسيه", "التسليم"],
                "desc": "تفويت مواعيد العطاءات والترسية",
                "pain": "متابعة العطاءات قبل موعد الترسية",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت تذكيركم بمواعيد العطاءات ومتابعتها، فلا يفوتكم موعد ترسية",
            },
            "followup_lost": {
                "triggers": ["متابع", "تابع", "معلق", "بدون متابعه", "ما تابع"],
                "desc": "بقاء العروض دون متابعة حتى تبرد",
                "pain": "بقاء عروضكم دون متابعة حتى تبرد",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت متابعة عروضكم المعلّقة في وقتها، فلا يبرد عرضٌ لكم",
            },
        },
    },
    "finance": {
        "desc": "تمويل وتحصيل ديون: متعثّرات، أعمار ديون، تذكير بالأقساط، ضغط على المحصّلين",
        "general": {
            "pain": "بين تقادم أعمار الديون وكثرة المتعثّرات وتذكير العملاء بأقساطهم، قد تتأخّر المتابعة فيتراجع التحصيل",
            "solution": "ونحن إلى جانب فرقكم نُؤتمت متابعة المتعثّرات والأقساط دون أن تزيد أعباءهم",
        },
        "categories": {
            "aging_debt": {
                "triggers": ["اعمار الديون", "تقادم", "ديون", "متعثر", "المتعثر"],
                "desc": "تقادم أعمار الديون دون متابعة منتظمة",
                "pain": "تقادم أعمار ديونكم دون متابعة منتظمة",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت المتابعة المنتظمة للمتعثّرات في وقتها، فيرتفع التحصيل",
            },
            "reminder": {
                "triggers": ["تذكير", "يذكر", "ينسون", "ينسى", "نسي", "القسط", "اقساط", "الاقساط", "استحقاق"],
                "desc": "عدم تذكير العملاء بمواعيد أقساطهم",
                "pain": "تذكير عملائكم بمواعيد أقساطهم",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت تذكير عملائكم بأقساطهم قبل استحقاقها، فيقلّ التعثّر",
            },
            "collector_load": {
                "triggers": ["ارهاق", "المحصل", "محصل", "كثره الحالات", "ضغط"],
                "desc": "إرهاق فرق التحصيل بكثرة الحالات",
                "pain": "كثرة الحالات على فرق التحصيل لديكم",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت المتابعة الروتينية، فيتفرّغ فريقكم للحالات التي تحتاج تفاوضاً",
            },
            "slow_reply": {
                "triggers": ["تاخر", "الرد", "يرد", "ردو", "بدون رد", "تجاهل", "ما رد", "ما يرد"],
                "desc": "تأخّر أو انعدام الردّ على اتصالات العملاء ورسائلهم",
                "pain": "تأخّر الردّ على اتصالات عملائكم ورسائلهم",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت الردّ الأول والمتابعة مع عملائكم فوراً، فلا يُهمل عميل",
            },
        },
    },
    "realestate": {
        "desc": "عقار وإدارة أملاك: استفسارات المهتمّين، تنسيق المعاينات، إشغال الوحدات",
        "general": {
            "pain": "بين كثرة استفسارات المهتمّين وتنسيق المعاينات ومتابعة العروض، قد يبرد مهتمٌّ قبل أن يصله ردّ أو تبقى وحدةٌ شاغرة",
            "solution": "ونحن إلى جانب فرقكم نُؤتمت متابعة المهتمّين وتنسيق المعاينات دون أن تزيد أعباءهم",
        },
        "categories": {
            "slow_reply_lead": {
                "triggers": ["تاخر", "يرد", "يردوا", "يردون", "ردو", "بدون رد", "استفسر", "الاستفسار"],
                "desc": "تأخّر الردّ على استفسارات المهتمّين حتى يبردوا",
                "pain": "تأخّر الردّ على استفسارات المهتمّين حتى يبردوا",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت الردّ الأول على المهتمّين فوراً، فلا يبرد مهتمٌّ لكم",
            },
            "viewing_coord": {
                "triggers": ["معاين", "المعاين", "زياره", "تنسيق"],
                "desc": "صعوبة تنسيق مواعيد المعاينات",
                "pain": "تنسيق مواعيد المعاينات مع المهتمّين",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت تنسيق المعاينات وتذكير المهتمّين بها، فتزيد الزيارات الفعلية",
            },
            "vacancy": {
                "triggers": ["شاغر", "فاضي", "اشغال", "تاجير"],
                "desc": "بقاء الوحدات شاغرة طويلاً",
                "pain": "بقاء وحداتكم شاغرة أطول من اللازم",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت متابعة المهتمّين حتى الإغلاق، فتقلّ مدة الشغور",
            },
        },
    },
    "training": {
        "desc": "معهد تدريب: موسم تسجيل، استفسارات المتدرّبين، متابعة من لم يُكمل التسجيل",
        "general": {
            "pain": "بين كثرة المستفسرين في موسم التسجيل وتأخّر الردّ عليهم ومتابعة من لم يُكمل تسجيله، قد يضيع مستفسرٌ قبل أن يُسجّل",
            "solution": "ونحن إلى جانب فرقكم نُؤتمت متابعة المستفسرين وتذكيرهم بمواعيد التسجيل دون أن تزيد أعباءهم",
        },
        "categories": {
            "season_overload": {
                "triggers": ["موسم التسجيل", "التسجيل", "زحمه", "زحام", "كثره الاستفسار", "ضغط"],
                "desc": "زحام المستفسرين في موسم التسجيل يفوق طاقة الفريق",
                "pain": "زحام المستفسرين في موسم التسجيل يفوق طاقة فريقكم",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت الردّ الأول على المستفسرين مهما كثروا، فلا يضيع مستفسر",
            },
            "incomplete_reg": {
                "triggers": ["لم يكمل", "ما كمل", "يكمل", "تسجيل ناقص", "توقف", "لم يسجل"],
                "desc": "عدم متابعة من بدأ التسجيل ولم يُكمله",
                "pain": "متابعة من بدأ التسجيل ولم يُكمله",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت متابعة من لم يُكمل تسجيله وتذكيره، فترتفع نسبة الإتمام",
            },
            "slow_reply_edu": {
                "triggers": ["تاخر", "يرد", "يردون", "ردو", "بدون رد", "استفسار"],
                "desc": "تأخّر الردّ على استفسارات المتدرّبين",
                "pain": "تأخّر الردّ على استفسارات المتدرّبين",
                "solution": "ونحن إلى جانب فرقكم نُؤتمت الردّ الفوري على استفساراتهم، فلا يتّجه المستفسر لغيركم",
            },
        },
    },
}

_TASHKEEL = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")


def _norm(s: str) -> str:
    """Normalize Arabic for matching: strip tashkeel, unify alef/ya/hamza, lowercase latin."""
    s = (s or "").lower()
    s = _TASHKEEL.sub("", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا")
    s = s.replace("ى", "ي").replace("ئ", "ي").replace("ؤ", "و").replace("ة", "ه")
    s = re.sub(r"[ـ\s]+", " ", s)  # tatweel + collapse whitespace
    return s.strip()


CHEAP_MODEL = "qwen/qwen3.6-plus"   # same cheap model the enrichment uses


def classify_llm(vertical: str, pain_line: str, key: str) -> str | None:
    """Semantic fallback: map a pain_line to a category id (or None) via a cheap model.

    Used only when the deterministic keyword pass finds nothing — Arabic morphology makes
    keyword matching miss inflected forms. Returns a category id, or None for 'off-topic /
    not solvable here' (-> general, honouring the relevance rule).
    """
    import json
    import urllib.request
    lib = LIBRARY[vertical]
    cats = "\n".join(f'- {cid}: {c["desc"]}' for cid, c in lib["categories"].items())
    prompt = (
        f"Vertical: {lib['desc']}\n"
        f"A lead's pain (from their own reviews): \"{pain_line}\"\n\n"
        f"Which ONE of these known, solvable pains does it best match?\n{cats}\n\n"
        'Return JSON {"category":"<id>"} for the best match, or {"category":"none"} if it does '
        "not clearly match any (e.g. it praises them, or is off-topic). Do not guess."
    )
    body = json.dumps({"model": CHEAP_MODEL, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0.0}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = json.load(r)["choices"][0]["message"]["content"]
        m = re.search(r"\{.*\}", txt, re.S)
        cid = str(json.loads(m.group(0)).get("category", "none")).strip() if m else "none"
        return cid if cid in lib["categories"] else None
    except Exception as e:
        print(f"    (classify_llm error: {e})")
        return None


def select(vertical: str, pain_line: str, *, use_llm: bool = False, key: str | None = None) -> dict:
    """Relevance-rank specific vs general and return the winning COUPLED pair + trace."""
    vk = (vertical or "").strip().lower()
    lib = LIBRARY.get(vk)
    if not lib:
        raise ValueError(f"unknown vertical {vertical!r}; known: {list(LIBRARY)}")
    general = lib["general"]
    p_norm = _norm(pain_line)

    def _general(reason: str) -> dict:
        return {"choice": "general", "category": None, "score_specific": 0.0,
                "score_general": GENERAL_RELEVANCE, "reason": reason,
                "pain": general["pain"], "solution": general["solution"]}

    def _specific(cat: str, score: float, reason: str) -> dict:
        # PAIN = lead's own words (grounded); SOLUTION = the matched, coupled remedy
        return {"choice": "specific", "category": cat, "score_specific": score,
                "score_general": GENERAL_RELEVANCE, "reason": reason,
                "pain": pain_line.strip(), "solution": lib["categories"][cat]["solution"]}

    if not p_norm:
        return _general("no specific pain_line -> general (whole)")

    # tier 1 — deterministic keyword fast-path (inflection-friendly cores)
    best_cat, best_hits = None, 0
    for cat, spec in lib["categories"].items():
        hits = sum(1 for kw in spec["triggers"] if _norm(kw) in p_norm)
        if hits > best_hits:
            best_cat, best_hits = cat, hits
    score_specific = best_hits * PER_KEYWORD + (GROUNDED_BONUS if best_hits else 0.0)
    if best_cat and score_specific > GENERAL_RELEVANCE:
        return _specific(best_cat, score_specific, f"keyword: maps to '{best_cat}' ({best_hits} kw) -> beats general")

    # tier 2 — cheap-LLM semantic fallback (morphology-robust; returns None -> general)
    if use_llm and key:
        cid = classify_llm(vk, pain_line, key)
        if cid:
            return _specific(cid, GENERAL_RELEVANCE + GROUNDED_BONUS, f"llm: semantic match -> '{cid}'")
        return _general("llm: no solvable match -> general more relevant")

    return _general("specific present but no keyword match -> general (enable --llm for semantic pass)")


def compose_block(vertical: str, pain_line: str, *, use_llm: bool = False,
                  key: str | None = None) -> tuple[str, dict]:
    """Return the `{{2}}` block (coupled pain->solution) + the decision trace."""
    d = select(vertical, pain_line, use_llm=use_llm, key=key)
    pain = d["pain"].rstrip("،.").strip()
    solution = d["solution"].strip()
    block = f"{pain}، {solution}."
    return block, d


# ── self-test ──────────────────────────────────────────────────────────────
_SELFTEST = [
    ("clinics", "", "empty -> general"),
    ("clinics", "لاحظت أن بعض مراجعيكم ذكروا تأخّر الردّ على اتصالاتهم", "slow_reply -> specific"),
    ("clinics", "مراجعون يشتكون أنهم لا يجدون رداً بعد الدوام", "after_hours -> specific"),
    ("clinics", "الموقع نظيف والطاقم لطيف جداً", "irrelevant/novel -> general wins"),
    ("finance", "عملاء ينسون مواعيد أقساطهم ولا أحد يذكّرهم", "reminder -> specific"),
    ("realestate", "استفسرت عن شقة ولم يردوا عليّ إطلاقاً", "slow_reply_lead -> specific"),
    ("training", "في موسم التسجيل الزحمة كبيرة ولا يردون", "season_overload -> specific"),
]


def _self_test(*, use_llm: bool = False, key: str | None = None) -> None:
    for vertical, pain, note in _SELFTEST:
        block, d = compose_block(vertical, pain, use_llm=use_llm, key=key)
        print(f"[{vertical}] {note}")
        print(f"  pain_line: {pain or '(empty)'}")
        print(f"  -> choice={d['choice']} cat={d['category']} "
              f"score(spec={d['score_specific']:.2f} vs gen={d['score_general']:.2f}) | {d['reason']}")
        print(f"  {{{{2}}}} = {block}\n")


def _env(key: str) -> str | None:
    import os
    v = os.environ.get(key)
    if v:
        return v
    try:
        import os as _os
        p = _os.path.join(_os.path.dirname(__file__), "..", ".env")
        m = re.search(rf"^{re.escape(key)}=(.+)$", open(p, encoding="utf-8").read(), re.M)
        return m.group(1).strip() if m else None
    except OSError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--in", dest="inp", help="leads CSV (needs pain_line + a vertical)")
    ap.add_argument("--vertical", help="force a vertical for all rows (else read row['vertical'])")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--llm", action="store_true", help="enable the cheap-LLM semantic fallback")
    args = ap.parse_args()

    key = (_env("MY_OPENROUTER_KEY") or _env("OPENROUTER_API_KEY")) if args.llm else None

    if args.self_test or not args.inp:
        _self_test(use_llm=args.llm, key=key)
        return

    # CSV uses `sector`; map it to a library vertical key.
    sector_map = {
        "private clinics": "clinics", "contracting & facilities": "contracting",
        "finance & debt collection": "finance", "real estate": "realestate",
        "training institutes": "training",
    }

    with open(args.inp, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    todo = rows[: args.limit] if args.limit else rows
    n_spec = 0
    for r in todo:
        vertical = (args.vertical or r.get("vertical")
                    or sector_map.get((r.get("sector", "") or "").strip().lower(), ""))
        name = r.get("company_name") or r.get("name", "")
        block, d = compose_block(vertical, r.get("pain_line", ""), use_llm=args.llm, key=key)
        n_spec += d["choice"] == "specific"
        print(f"{name} [{vertical}] -> {d['choice']}"
              + (f"/{d['category']}" if d["choice"] == "specific" else "") )
        print(f"  {{{{2}}}} = {block}")
    print(f"\n{n_spec}/{len(todo)} used a specific coupled pain; the rest used the general default.")


if __name__ == "__main__":
    main()
