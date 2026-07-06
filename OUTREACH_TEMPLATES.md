# NAVAIA — Outreach Templates

> Planning/content deliverable. Sending, personalization-fill, and scheduling are
> handed to the scripting model. See `WORKFLOW_SPEC.md` §11 for the strategy,
> decisions, and research behind these.

## Conventions

- **Language:** formal فصحى, but **conversational** — talk to the lead about their
  situation, don't list what we sell. Warmth ~6/10. Keep it short; not long.
- **No AI tells:** no em-dashes in body, **no middot/bullet dots between or before
  words** (`·` / `•`), no calqued English marketing-speak, no government-letter
  clichés, consistent register.
- **Sender:** عبدالمجيد الوردي / Abdulmajeed Alwardi — نڤايا / NAVAIA
- **cal.com:** https://cal.com/abdulmajeed-alwardi — included **from touch 1**.
  Deliverability offset: sending model must use a warmed domain + plain-text link.
- **Cadence:** day 0 / +3 / +7. Send Sun–Thu, ~10am–12pm AST. Never Fri–Sat.
- **Channel:** email first; move to WhatsApp on engagement.
- **Field vocabulary:** each vertical weaves 2–3 **well-known field terms** into the
  copy (RFQ/عطاءات, محفظة التحصيل/أعمار الديون, عدم الحضور/قائمة الانتظار, الوحدات
  الشاغرة/سندات القبض, المتدربين/منصة اعتماد) to signal domain familiarity. See the
  **Field lexicon** line under each vertical. Keep terms recognizable to anyone in
  the field — never obscure jargon, never more than a light touch.

### Email flow (fixed order)

1. **Subject = the pain point**, drawn from real info about the lead. Catchy, short.
2. **Open on the pain** that concerns *this* company.
3. **What we do** — the actions taken, **not the how**. Frame as **حلول
   (solutions), never منصّة (platform)** — "platform" implies work/onboarding for
   the reader. Add a "works on your behalf, no extra load on your team" clause
   (تعمل إلى جانبكم دون عبء) to kill the effort fear, and a "we start from…"
   (نبدأ من…) phrasing so the single named pain implies broader scope without
   listing services. Keep حلول concrete — never "حلول مبتكرة/متكاملة" buzzword drift.
4. **Impact with prior clients** — stated as plain fact, no "trust me", no hype.
5. **Regulatory assurance** — stated clearly, not overstated (see below).
6. **CTA** — cal.com link + WhatsApp option.
7. **Signature** (4 lines, below).

### Benefit bank — pick TWO of three per lead (match to the lead's situation)

All three are real, already-achieved results with prior clients. State as fact.

> **Numbers are confirmed for CLINICS only.** The +30% / 40–60% figures are used
> verbatim in the clinic sequence. For every other vertical the rate is a
> **placeholder** (`{نسبة الأثر}`, `{نسبة التحصيل}`, `{نسبة خفض التكاليف}`) — user
> to supply the real per-vertical figure before sending.

| # | Benefit | Arabic phrasing (clinic numbers; placeholder elsewhere) |
|---|---------|-----------------|
| 1 | Cost minimization | خفض في التكاليف التشغيلية يتراوح بين 40% و60% (clinic) / بنسبة {نسبة خفض التكاليف} (other) |
| 2 | Profit increase | ارتفاع في الأرباح تجاوز 30% (clinic) / بنسبة {نسبة الأثر} (other) |
| 3 | Employee productivity | ارتفاع في إنتاجية الفريق ووقت أكبر للتركيز على العميل الحاضر |

### Regulatory assurance line (clear, not overstated)

Clinics get Ministry of Health + PDPL; other verticals get PDPL + relevant work
regulations. Example (clinics):
> وكل ذلك ملتزم بأنظمة وزارة الصحة ونظام حماية البيانات الشخصية وما يتّصل بها من
> أنظمة، فبيانات عيادتكم ومرضاكم في مأمن.

### Signature (4 lines, all emails)

```
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا
```

### Tokens

| Token | Per | Meaning |
|-------|-----|---------|
| `{اسم العيادة}` / `{اسم الشركة}` / `{اسم المعهد}` | lead | Business name — noun adapts per vertical (عيادة / شركة / مكتب / معهد) |
| `{honorific+name}` | lead | e.g. حضرة الدكتور فلان / الأستاذ فلان |
| `{القناة}` | lead | Their booking/inquiry channel (phone / WhatsApp / IG DM / form) |
| `{pain_line}` | lead | One concrete observation about that business |
| `{benefit_pair}` | lead | Two of the three benefits above, chosen to fit the lead |
| `{نسبة الأثر}` / `{نسبة التحصيل}` / `{نسبة خفض التكاليف}` | vertical | **Needed from user** — impact rate for non-clinic verticals (clinics use the confirmed +30% / 40–60%) |
| `{{CONTACT_PHONE}}` | fixed | Sender's phone in the signature — **resolved** |

Only `{honorific+name}`, `{اسم العيادة}`, `{pain_line}`, and `{benefit_pair}` are
per-lead.

---

## Vertical 3 (Tier 1) — العيادات الخاصة الطبية (Private Specialty Clinics) — REFERENCE SEQUENCE

Specialty only: dental, dermatology, cosmetic, physiotherapy. **NOT** general
hospitals. Pain: bookings lost after hours, cancelled appointments with no
follow-up, reception staff quit yearly. Decision fast (high margins). Benefit
pair used: profit +30% and cost −40–60%. Compliance: MoH + PDPL.

**Value prop:** نڤايا تردّ على استفسارات المرضى وتؤكّد المواعيد وتتابع المتأخّرين،
فيبقى الجدول ممتلئاً دون عبء على فريقكم.

**Field lexicon (woven in):** المراجعين، نسبة إشغال الجدول، قائمة الانتظار، عدم
الحضور (no-show)، إعادة الجدولة، تأكيد المواعيد والتذكير بها.

### Subject-line options (pick one, keep it short)
- `مواعيد فائتة في {اسم العيادة}؟`
- `الردّ الآلي على استفسارات عيادتكم`
- `كم تكلّفكم المواعيد الضائعة؟`

### Touch 1 — Day 0 (pain → actions → impact → compliance → link)

**الموضوع:** مواعيد فائتة في {اسم العيادة}؟

السلام عليكم ورحمة الله وبركاته،
{honorific+name}، أطيب التحية،

أعلم أن يوم العيادة لا يترك متّسعاً للردّ على كل اتصال أو استفسار يصل بعد الدوام، ومع
ذلك فكل مكالمة تفوت قد تكون مراجعاً ذهب إلى غيركم، وكل حالة عدم حضور موعدٌ شاغر كان
يمكن ملؤه من قائمة الانتظار.

نڤايا تقدّم حلولاً لأتمتة تواصل العيادة مع مرضاها، تعمل إلى جانبكم دون أي عبء إضافي
على فريقكم. نبدأ من أكثر نقطة تكلّفكم: الردّ على استفسارات المراجعين، وتأكيد المواعيد
والتذكير بها لتقليل عدم الحضور، وإعادة ملء المواعيد الملغاة من قائمة الانتظار.

وهذه ليست وعوداً بل نتائج لمسها عملاؤنا فعلاً: ارتفاع في الأرباح تجاوز 30%، وخفض في
التكاليف التشغيلية يتراوح بين 40% و60%.

وكل ذلك ملتزم بأنظمة وزارة الصحة ونظام حماية البيانات الشخصية وما يتّصل بها من أنظمة،
فبيانات عيادتكم ومرضاكم في مأمن.

يسعدني أن أوضّح لكم الأثر على عيادتكم في مكالمة قصيرة. اختاروا الوقت الأنسب لكم هنا:
https://cal.com/abdulmajeed-alwardi أو راسلوني على واتساب إن كان أيسر.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 2 — Day +3 (new angle: the reception team)

**الموضوع:** زاوية أخرى تخصّ استقبال {اسم العيادة}

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

عوداً على رسالتي، خطرت لي زاوية أخرى ربما تهمّكم أكثر، وهي فريق الاستقبال لديكم.

بين الردّ على الهاتف وتنظيم المواعيد ومتابعة المتأخّرين، يضيع وقتٌ طويل كان يمكن أن
يُصرف على المريض الحاضر أمامهم. حين تولّت نڤايا هذا الجانب لدى عملائنا، ارتفعت إنتاجية
الفريق وتفرّغوا لما هو أهم.

إن رأيتم أن الأمر يستحق النقاش، يسعدني ترتيب مكالمة قصيرة في وقتٍ يناسبكم:
https://cal.com/abdulmajeed-alwardi

مع التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 3 — Day +7 (warm door-open breakup)

**الموضوع:** أترك الأمر بين يديكم

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

لن أثقل عليكم أكثر، فأنا أقدّر انشغالكم.

أردت فقط أن أترك الباب مفتوحاً: إن شعرتم يوماً أن مواعيد تضيع أو استفسارات تتأخّر،
فنڤايا جاهزة حين تحتاجونها. رابط الحجز هنا متى ما ناسبكم:
https://cal.com/abdulmajeed-alwardi أو رسالة على واتساب تكفي.

أشكر لكم وقتكم، وأتمنّى لعيادتكم دوام التوفيق.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

---

## Vertical 1 (Tier 1) — المقاولات والصيانة وإدارة المرافق (Contracting, Maintenance & Facilities)

Pain: lose contracts every week for lack of a proposals team. Decision maker: owner
directly. Value = a won contract. Benefit pair: profit +30% and staff productivity.
Compliance: PDPL + أنظمة العمل.

**Value prop:** نڤايا تلتقط طلبات العروض والاستفسارات وتردّ عليها فوراً وتتابع العروض
حتى الترسية، فلا يضيع عقد بسبب تأخّر الردّ.

**Field lexicon (woven in):** طلبات عروض الأسعار (RFQ)، المناقصات والعطاءات، كراسة
الشروط والمواصفات، مواعيد تسليم العطاءات، الترسية، عقود الصيانة الوقائية، اتفاقيات
مستوى الخدمة (SLA)، أوامر العمل.

**Subject options:** `عقود تضيع في {اسم الشركة}؟` / `عرضٌ متأخر = عقدٌ ضائع` / `من يتابع عروضكم؟`

### Touch 1 — Day 0

**الموضوع:** عقود تضيع في {اسم الشركة}؟

السلام عليكم ورحمة الله وبركاته،
{honorific+name}، أطيب التحية،

أعلم أن طلبات عروض الأسعار (RFQ) والمناقصات تصل في أوقاتٍ لا يتّسع لها اليوم، ومع ذلك
فكل طلبٍ يتأخّر الردّ عليه أو عطاءٍ يفوت موعد تسليمه قد يكون عقداً ذهب إلى منافس أسرع.

نڤايا تقدّم حلولاً لأتمتة تواصلكم مع عملائكم، تعمل إلى جانبكم دون أي عبء إضافي على
فريقكم. نبدأ من أكثر نقطة تكلّفكم: الردّ على طلبات عروض الأسعار والاستفسارات فور
وصولها، ومتابعة العطاءات حتى الترسية، مع التنبيه لمواعيد تسليمها قبل فواتها.

وهذه ليست وعوداً بل نتائج لمسها عملاؤنا فعلاً: ارتفاع في الأرباح بنسبة {نسبة الأثر} مع فريقٍ
أكثر تفرّغاً لإنجاز العمل بدل مطاردة المتابعات.

وكل ذلك ملتزم بنظام حماية البيانات الشخصية وأنظمة العمل ذات الصلة.

يسعدني أن أوضّح لكم الأثر على شركتكم في مكالمة قصيرة. اختاروا الوقت الأنسب لكم هنا:
https://cal.com/abdulmajeed-alwardi أو راسلوني على واتساب إن كان أيسر.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 2 — Day +3 (angle: the follow-up that closes)

**الموضوع:** ليست المشكلة في العرض، بل في المتابعة

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

عوداً على رسالتي، أغلب العقود لا تُفقد لأن العرض ضعيف، بل لأن لا أحد تابعه في وقته،
سواء أكان عرض سعرٍ جديداً أو تجديد عقد صيانة.

نڤايا تتكفّل بهذه المتابعة إلى جانبكم، فلا يبقى عرضٌ معلّقاً ولا عميلٌ دون ردّ، وقد
لمس عملاؤنا أثر ذلك في عدد العقود المكتملة.

إن رأيتم الأمر يستحق النقاش، يسعدني ترتيب مكالمة قصيرة في وقتٍ يناسبكم:
https://cal.com/abdulmajeed-alwardi

مع التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 3 — Day +7 (warm door-open breakup)

**الموضوع:** أترك الأمر بين يديكم

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

لن أثقل عليكم أكثر، فأنا أقدّر انشغالكم.

أردت فقط أن أترك الباب مفتوحاً: متى ما شعرتم أن طلباً يضيع أو عرضاً يتأخّر، فنڤايا
جاهزة حين تحتاجونها. رابط الحجز هنا متى ما ناسبكم: https://cal.com/abdulmajeed-alwardi
أو رسالة على واتساب تكفي.

أشكر لكم وقتكم، وأتمنّى لشركتكم دوام التوفيق.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

---

## Vertical 2 (Tier 1) — التمويل والتقسيط ومكاتب التحصيل (Finance, Installment & Debt Collection)

Pain: stuck debts = dead revenue, human collectors burn out and quit, SAMA
compliance is a genuine advantage. Pricing = % of collected. Benefit pair: profit
+30% (more collected) and cost −40–60% (collector overhead). Compliance: **SAMA** +
PDPL — lead with SAMA, it's a differentiator here.

**Value prop:** نڤايا تتابع المتعثّرين بانتظام ووفق أنظمة ساما وحماية البيانات، فيرتفع
التحصيل دون إرهاق فريقكم.

**Field lexicon (woven in):** المتعثّرات، أعمار الديون (aging)، محفظة التحصيل، نسبة
التحصيل، الأقساط المتأخّرة، جدولة الديون وإعادة الهيكلة، لوائح ممارسات التحصيل من ساما.

**Subject options:** `تحصيلٌ أعلى دون إرهاق الفريق` / `متابعةٌ منتظمة ومتوافقة مع ساما` / `ديونٌ متعثّرة في {اسم الشركة}؟`

### Touch 1 — Day 0

**الموضوع:** تحصيلٌ أعلى دون إرهاق الفريق

السلام عليكم ورحمة الله وبركاته،
{honorific+name}، أطيب التحية،

أعلم أن متابعة محفظة التحصيل يوماً بيوم عملٌ مرهق، وأن المحصّلين يحترقون ويتركون
العمل، وأن كل حسابٍ تتقادم مديونيته دون متابعة هو إيرادٌ معلّق.

نڤايا تقدّم حلولاً لأتمتة متابعة التحصيل، تعمل إلى جانب فريقكم دون أن تزيد عبئه. نبدأ
من أكثر نقطة تكلّفكم: متابعة منتظمة ومنضبطة للأقساط المتأخّرة وكل متعثّر وفق أعمار الديون، في وقتها وبالنبرة المناسبة.

وهذه ليست وعوداً بل نتائج لمسها عملاؤنا فعلاً: ارتفاع في التحصيل بنسبة {نسبة التحصيل} وخفض في
تكاليف التشغيل بنسبة {نسبة خفض التكاليف}.

وكل ذلك ملتزم بأنظمة ساما ولوائح ممارسات التحصيل ونظام حماية البيانات الشخصية،
فالمتابعة تتم ضمن الإطار النظامي دون أي مخالفة.

يسعدني أن أوضّح لكم الأثر على مكتبكم في مكالمة قصيرة. اختاروا الوقت الأنسب لكم هنا:
https://cal.com/abdulmajeed-alwardi أو راسلوني على واتساب إن كان أيسر.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 2 — Day +3 (angle: consistency the human team can't sustain)

**الموضوع:** المتابعة التي لا يتعب منها أحد

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

عوداً على رسالتي، الفرق ليس في مهارة المحصّل، بل في انتظام المتابعة. الإنسان يتعب
وينسى ويترك العمل، والحساب يبقى معلّقاً.

نڤايا تحافظ على هذا الانتظام إلى جانبكم ووفق أنظمة ساما، فيبقى كل متعثّر تحت المتابعة
حتى السداد، وقد لمس عملاؤنا أثر ذلك في نسبة التحصيل.

إن رأيتم الأمر يستحق النقاش، يسعدني ترتيب مكالمة قصيرة في وقتٍ يناسبكم:
https://cal.com/abdulmajeed-alwardi

مع التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 3 — Day +7 (warm door-open breakup)

**الموضوع:** أترك الأمر بين يديكم

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

لن أثقل عليكم أكثر، فأنا أقدّر انشغالكم.

أردت فقط أن أترك الباب مفتوحاً: متى ما رغبتم في رفع التحصيل دون إرهاق الفريق، فنڤايا
جاهزة حين تحتاجونها. رابط الحجز هنا متى ما ناسبكم: https://cal.com/abdulmajeed-alwardi
أو رسالة على واتساب تكفي.

أشكر لكم وقتكم، وأتمنّى لمكتبكم دوام التوفيق.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

---

## Vertical 4 (Tier 2) — العقار وإدارة الأملاك (Real Estate & Property Management)

Pain: an interested client goes cold within minutes without a reply; late rent
collection ties this sector to the debt-collection agent (buys two agents). Benefit
pair: profit +30% (closed deals) and staff productivity. Compliance: PDPL +
الأنظمة العقارية (REGA).

**Value prop:** نڤايا تردّ على المهتمّين خلال ثوانٍ قبل أن يبردوا، وتتابع تحصيل
الإيجارات في وقتها، فلا تضيع صفقة ولا دفعة.

**Field lexicon (woven in):** المهتمّ (lead)، المعاينة، الوحدات الشاغرة، نسبة
الإشغال، عقود الإيجار ودفعاتها، سندات القبض، إدارة الأملاك.

**Subject options:** `المهتمّ يبرد خلال دقائق` / `ردٌّ فوري = صفقةٌ لا تضيع` / `من يردّ على مهتمّي {اسم الشركة}؟`

### Touch 1 — Day 0

**الموضوع:** المهتمّ يبرد خلال دقائق

السلام عليكم ورحمة الله وبركاته،
{honorific+name}، أطيب التحية،

أعلم أن المهتمّ بالعقار لا ينتظر؛ إن لم يجد رداً خلال دقائق انتقل إلى إعلانٍ آخر،
فتبقى الوحدة شاغرة وتضيع صفقة كانت في متناول اليد.

نڤايا تقدّم حلولاً لأتمتة تواصلكم مع العملاء، تعمل إلى جانبكم دون أي عبء إضافي على
فريقكم. نبدأ من أكثر نقطة تكلّفكم: الردّ الفوري على كل مهتمّ، وحجز المعاينة ومتابعته
حتى إتمامها، مع متابعة تحصيل دفعات الإيجار وسنداتها في مواعيدها.

وهذه ليست وعوداً بل نتائج لمسها عملاؤنا فعلاً: ارتفاع في الصفقات المكتملة بنسبة {نسبة الأثر}
مع فريقٍ أكثر تفرّغاً لإتمام البيع بدل مطاردة الردود.

وكل ذلك ملتزم بنظام حماية البيانات الشخصية والأنظمة العقارية ذات الصلة.

يسعدني أن أوضّح لكم الأثر على مكتبكم في مكالمة قصيرة. اختاروا الوقت الأنسب لكم هنا:
https://cal.com/abdulmajeed-alwardi أو راسلوني على واتساب إن كان أيسر.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 2 — Day +3 (angle: rent collection, the second need)

**الموضوع:** وماذا عن تحصيل الإيجارات؟

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

عوداً على رسالتي، ثمّة جانبٌ آخر يرهق مكاتب العقار قدر ضياع المهتمّين، وهو تأخّر
تحصيل دفعات الإيجار المستحقة ومتابعة المستأجرين وسندات القبض.

نڤايا تتكفّل بالمتابعتين معاً إلى جانبكم: المهتمّ الجديد حتى المعاينة، والمستأجر حتى
السداد في وقته، وقد لمس عملاؤنا أثر ذلك في انتظام الدخل.

إن رأيتم الأمر يستحق النقاش، يسعدني ترتيب مكالمة قصيرة في وقتٍ يناسبكم:
https://cal.com/abdulmajeed-alwardi

مع التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 3 — Day +7 (warm door-open breakup)

**الموضوع:** أترك الأمر بين يديكم

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

لن أثقل عليكم أكثر، فأنا أقدّر انشغالكم.

أردت فقط أن أترك الباب مفتوحاً: متى ما شعرتم أن مهتمّاً يبرد أو دفعةً تتأخّر، فنڤايا
جاهزة حين تحتاجونها. رابط الحجز هنا متى ما ناسبكم: https://cal.com/abdulmajeed-alwardi
أو رسالة على واتساب تكفي.

أشكر لكم وقتكم، وأتمنّى لمكتبكم دوام التوفيق.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

---

## Vertical 5 (Tier 2) — معاهد التدريب (Training Institutes)

Pain: registration season drowns them; they also bid on government training tenders
(dual buyer). Benefit pair: staff productivity (absorb the surge) and profit +30%
(more enrolments). Compliance: PDPL + أنظمة التدريب (TVTC).

**Value prop:** نڤايا تستوعب زحام موسم التسجيل وتردّ على كل مستفسر في حينه وتتابع
الفرص حتى التسجيل، فلا يضيع طالب ولا فرصة.

**Field lexicon (woven in):** المتدربين، القبول والتسجيل، الدفعات والأفواج، البرامج
والحقائب التدريبية، المنافسات الحكومية، منصة اعتماد (Etimad)، اعتماد المنشأة.

**Subject options:** `موسم التسجيل لا يجب أن يُغرقكم` / `كل مستفسر يُردّ عليه في حينه` / `مستفسرون يضيعون في {اسم المعهد}؟`

### Touch 1 — Day 0

**الموضوع:** موسم التسجيل لا يجب أن يُغرقكم

السلام عليكم ورحمة الله وبركاته،
{honorific+name}، أطيب التحية،

أعلم أن موسم التسجيل يأتي بزحامٍ من استفسارات المتدربين المحتملين يفوق طاقة الفريق،
فيضيع مستفسرون جادّون لمجرّد أن الردّ تأخّر عليهم.

نڤايا تقدّم حلولاً لأتمتة تواصلكم مع المستفسرين، تعمل إلى جانبكم دون أي عبء إضافي على
فريقكم. نبدأ من أكثر نقطة تكلّفكم: الردّ على كل مستفسر في حينه، ومتابعته حتى إتمام
القبول والالتحاق بالدفعة، مهما اشتدّ الزحام.

وهذه ليست وعوداً بل نتائج لمسها عملاؤنا فعلاً: ارتفاع في التسجيلات بنسبة {نسبة الأثر} مع فريقٍ
يستوعب الموسم دون إرهاق.

وكل ذلك ملتزم بنظام حماية البيانات الشخصية وأنظمة التدريب ذات الصلة.

يسعدني أن أوضّح لكم الأثر على معهدكم في مكالمة قصيرة. اختاروا الوقت الأنسب لكم هنا:
https://cal.com/abdulmajeed-alwardi أو راسلوني على واتساب إن كان أيسر.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 2 — Day +3 (angle: the leads lost between seasons)

**الموضوع:** المستفسر الذي لم يُكمل التسجيل

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

عوداً على رسالتي، ليس كل من استفسر التحق؛ كثيرون توقّفوا في منتصف إجراءات القبول لأن
لا أحد تابعهم.

نڤايا تتكفّل بمتابعة هؤلاء إلى جانبكم حتى إتمام التسجيل والالتحاق بالدفعة، وقد لمس
عملاؤنا أثر ذلك في عدد المتدربين الذين أكملوا فعلاً.

إن رأيتم الأمر يستحق النقاش، يسعدني ترتيب مكالمة قصيرة في وقتٍ يناسبكم:
https://cal.com/abdulmajeed-alwardi

مع التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

### Touch 3 — Day +7 (warm door-open breakup)

**الموضوع:** أترك الأمر بين يديكم

السلام عليكم ورحمة الله وبركاته،
{honorific+name}،

لن أثقل عليكم أكثر، فأنا أقدّر انشغالكم.

أردت فقط أن أترك الباب مفتوحاً: متى ما أثقلكم موسم التسجيل أو ضاع مستفسر، فنڤايا جاهزة
حين تحتاجونها. رابط الحجز هنا متى ما ناسبكم: https://cal.com/abdulmajeed-alwardi
أو رسالة على واتساب تكفي.

أشكر لكم وقتكم، وأتمنّى لمعهدكم دوام التوفيق.

مع خالص التقدير،
عبدالمجيد الوردي
تطوير الأعمال - Business Development
{{CONTACT_PHONE}}
NAVAIA نڤايا

---

## On positive reply (any touch, all verticals)

Check cal.com first — they may have already booked from the link in the email.
Pick the matching reply:

**A) Replied, but no booking yet:**

يسعدني ذلك. تفضّلوا باختيار الوقت الأنسب لكم هنا:
https://cal.com/abdulmajeed-alwardi أو أرسلوا لي وقتاً مناسباً على واتساب لأتّصل بكم.

**B) They already booked via the link:**

شكراً لكم، وصلني حجزكم وسأتّصل بكم في الموعد الذي اخترتموه. وإن رغبتم في تقديمه أو
تأجيله فأنا رهن إشارتكم.

## Ramadan variant (applies to all verticals)

- Add opener under the greeting: `رمضان مبارك، أعاده الله عليكم بالخير.`
- Soften the CTA verb; no urgency.
- Send early morning or post-iftar; avoid mid-afternoon.
