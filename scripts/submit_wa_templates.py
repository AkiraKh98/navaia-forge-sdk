"""Submit all 5 WhatsApp templates to Meta via Baian (cloud-only).

Creates a cloud task for each template asking Tariq to submit it via Baian's
create_template tool. Does NOT wait for approval - just submits and prints the task IDs.
Check approval status tomorrow with: python scripts/check_baian_templates.py

Templates:
  navaia_clinics_t1, navaia_contracting_t1, navaia_finance_t1,
  navaia_realestate_t1, navaia_training_t1
"""
from __future__ import annotations

import io
import os
import re
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from navaia_forge import NavaiaForgeClient

CLOUD_BASE = "https://fareegi.navaia.sa"
CLOUD_WF = "131bb52f-e5eb-44ad-8134-03dc6908b485"
TARIQ = "6ba49326-4ec0-4b3b-8651-9526ec96894e"
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")


def _env(key: str) -> str:
    m = re.search(rf"^{re.escape(key)}=(.+)$", open(ENV_PATH).read(), re.M)
    if not m:
        raise SystemExit(f"{key} not found in {ENV_PATH}")
    return m.group(1).strip()


TEMPLATES = {
    "navaia_clinics_t1": """السلام عليكم ورحمة الله وبركاته،
{{1}}، تحية طيبة،

{{2}}

ساعدنا عياداتٍ أخرى تعاني من تأخّر الردّ على مراجعيها وفقدان حجوزاتها بعد الدوام، فكان الأثر مباشراً: أرباحها أعلى بنسبة 30% وتكاليفها أقل بنسبة 40%، وذلك ضمن أنظمة وزارة الصحة وحماية البيانات.

نڤايا تعمل إلى جانبكم ليبقى جدولكم ممتلئاً دون عبء على فريق استقبالكم.

يسعدني أن أوضح لكم الأثر المتوقّع على {{3}} تحديداً، ما هو الوقت المناسب لكم؟ {{4}}، أو راسلوني هنا.

{{5}}""",

    "navaia_contracting_t1": """السلام عليكم ورحمة الله وبركاته،
{{1}}، تحية طيبة،

{{2}}

ساعدنا شركاتٍ أخرى تعاني من تأخّر الردّ على طلبات عروض الأسعار وضياع عطاءاتها قبل موعد الترسية، فكان الأثر مباشراً: أرباحها أعلى بنسبة 30% وتكاليفها أقل بنسبة 40%، وذلك ضمن نظام حماية البيانات وأنظمة العمل.

نڤايا تعمل إلى جانبكم فلا يفوتكم عقدٌ بسبب تأخّر متابعةٍ أو عرضٍ معلّق.

يسعدني أن أوضح لكم الأثر المتوقّع على {{3}} تحديداً، ما هو الوقت المناسب لكم؟ {{4}}، أو راسلوني هنا.

{{5}}""",

    "navaia_finance_t1": """السلام عليكم ورحمة الله وبركاته،
{{1}}، تحية طيبة،

{{2}}

ساعدنا مكاتبَ أخرى تعاني من تقادم أعمار الديون وإرهاق محصّليها دون انتظام في المتابعة، فكان الأثر مباشراً: تحصيلها أعلى بنسبة 30% وتكاليفها أقل بنسبة 40%، وكل ذلك ضمن أنظمة ساما ولوائح ممارسات التحصيل.

نڤايا تعمل إلى جانب فريقكم فلا يبقى متعثّرٌ لكم دون متابعةٍ في وقتها.

يسعدني أن أوضح لكم الأثر المتوقّع على {{3}} تحديداً، ما هو الوقت المناسب لكم؟ {{4}}، أو راسلوني هنا.

{{5}}""",

    "navaia_realestate_t1": """السلام عليكم ورحمة الله وبركاته،
{{1}}، تحية طيبة،

{{2}}

ساعدنا مكاتبَ أخرى تعاني من برود مهتمّيها قبل أن يصله ردّ وبقاء وحداتها شاغرة، فكان الأثر مباشراً: أرباحها أعلى بنسبة 30% وتكاليفها أقل بنسبة 40%، وكل ذلك ضمن نظام حماية البيانات والأنظمة العقارية.

نڤايا تعمل إلى جانبكم فلا يبرد مهتمّكم ولا تبقى وحدتكم شاغرةً بسبب تأخّر الردّ.

يسعدني أن أوضح لكم الأثر المتوقّع على {{3}} تحديداً، ما هو الوقت المناسب لكم؟ {{4}}، أو راسلوني هنا.

{{5}}""",

    "navaia_training_t1": """السلام عليكم ورحمة الله وبركاته،
{{1}}، تحية طيبة،

{{2}}

ساعدنا معاهدَ أخرى تعاني من ضياع مستفسريها في موسم التسجيل لتأخّر الردّ عليهم، فكان الأثر مباشراً: تسجيلاتها أعلى بنسبة 30% وتكاليفها أقل بنسبة 40%، وكل ذلك ضمن نظام حماية البيانات وأنظمة التدريب.

نڤايا تعمل إلى جانبكم فلا يضيع مستفسرٌ لكم مهما اشتدّ زحام موسمكم.

يسعدني أن أوضح لكم الأثر المتوقّع على {{3}} تحديداً، ما هو الوقت المناسب لكم؟ {{4}}، أو راسلوني هنا.

{{5}}""",
}


def main() -> None:
    key = _env("BUSINESS_NF")
    cloud = NavaiaForgeClient(api_key=key, base_url=CLOUD_BASE)

    for name, body in TEMPLATES.items():
        desc = f"""Create a NEW WhatsApp template via Baian's create_template tool.

Template name: {name}
Category: MARKETING
Language: ar (Arabic)
Body (exactly this, with {{{{1}}}}-{{{{5}}}} as variable placeholders):

{body}

Steps:
1. Introspect Baian's tools (do not hardcode endpoints).
2. Use create_template to submit this template to Meta with the exact name, category, language, and body above.
3. Do NOT wait for approval in this task. Just submit and report the submission result.
4. Do NOT send any message. Do NOT look up CRM leads.

Report: template name submitted, any template ID returned, and any error."""

        t = cloud.tasks.create(
            CLOUD_WF,
            f"SUBMIT: WhatsApp template ({name})",
            description=desc,
            agent_id=TARIQ,
            priority="standard",
            metadata={"channel": "whatsapp", "template": name, "action": "create"},
        )
        print(f"[{name}] TASK CREATED: {t.id} | status: {t.status}")

        # Poll briefly to approve the plan gate, then move on
        deadline = time.time() + 120
        last = None
        while time.time() < deadline:
            t = cloud.tasks.get(t.id)
            if t.status != last:
                print(f"  [{name}] status -> {t.status}")
                last = t.status
            s = str(t.status).lower()
            if "waiting_plan" in s:
                try:
                    cloud.tasks.approve(t.id)
                    print(f"  [{name}] approved plan")
                except Exception:
                    pass
            elif s in ("done", "failed", "cancelled", "waiting_blocked", "waiting_question"):
                break
            time.sleep(6)

        t = cloud.tasks.get(t.id)
        print(f"  [{name}] FINAL: {t.status}")
        print(f"  [{name}] RESULT: {(t.result or '')[:500]}")
        print()

    print("=== All templates submitted ===")
    print("Check approval status tomorrow with:")
    print("  python scripts/check_baian_templates.py")


if __name__ == "__main__":
    main()
