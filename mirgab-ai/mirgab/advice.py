"""Protective advice per fraud domain (Arabic + English)."""

ADVICE = {
    "real_estate": {
        "en": ["Never pay a deposit before viewing the property in person.",
               "Check the broker / listing permit on the official real-estate authority (ADREC / Dubai Land Department).",
               "Only sign contracts registered through Tawtheeq or Ejari and pay to company accounts, not personal ones."],
        "ar": ["لا تدفع أي عربون قبل معاينة العقار بنفسك.",
               "تحقق من تصريح الوسيط أو الإعلان عبر الجهة العقارية الرسمية (مركز أبوظبي العقاري / دائرة الأراضي والأملاك).",
               "وقّع فقط عقوداً موثقة عبر توثيق أو إيجاري، وادفع لحسابات شركات وليس حسابات شخصية."],
    },
    "pharma": {
        "en": ["Buy medicines only from licensed pharmacies (DoH / MOHAP / DHA licensed).",
               "Prescription medicines sold without a prescription may be fake, expired or dangerous.",
               "Consult a doctor before using any weight-loss injection or 'miracle' product."],
        "ar": ["اشترِ الأدوية فقط من صيدليات مرخصة (دائرة الصحة / وزارة الصحة / هيئة الصحة بدبي).",
               "الأدوية التي تباع بدون وصفة قد تكون مغشوشة أو منتهية أو خطيرة على صحتك.",
               "استشر طبيبك قبل استخدام أي إبر تنحيف أو منتج \"علاج سحري\"."],
    },
    "fake_store": {
        "en": ["Prefer cash-on-delivery or payment methods with buyer protection.",
               "Search the store name + 'scam' and check its trade licence and physical address.",
               "Discounts of 80-90% on branded products are almost always fake."],
        "ar": ["فضّل الدفع عند الاستلام أو وسائل دفع توفر حماية للمشتري.",
               "ابحث عن اسم المتجر مع كلمة \"احتيال\" وتحقق من الرخصة التجارية والعنوان الفعلي.",
               "خصومات 80-90% على منتجات الماركات غالباً ما تكون وهمية."],
    },
    "investment": {
        "en": ["No legitimate investment guarantees returns - 'guaranteed profit' is a red flag.",
               "Verify the company is licensed by SCA, DFSA (DIFC) or FSRA (ADGM) on their official registers.",
               "Never send money to individuals or crypto wallets you met on social media."],
        "ar": ["لا يوجد استثمار حقيقي يضمن الأرباح - \"ربح مضمون\" علامة تحذير.",
               "تحقق من ترخيص الشركة لدى هيئة الأوراق المالية والسلع أو DFSA أو FSRA من سجلاتها الرسمية.",
               "لا ترسل أموالاً لأشخاص أو محافظ عملات رقمية تعرفت عليها عبر وسائل التواصل."],
    },
    "impersonation": {
        "en": ["Government entities and banks never ask for your OTP, PIN or password by message or call.",
               "Type the official website yourself or use the official app - never click links in SMS.",
               "Pay fines only through official channels (TAMM, Abu Dhabi Police app, MOI app)."],
        "ar": ["الجهات الحكومية والبنوك لا تطلب أبداً رمز التحقق أو الرقم السري عبر رسالة أو اتصال.",
               "اكتب عنوان الموقع الرسمي بنفسك أو استخدم التطبيق الرسمي - لا تضغط على روابط الرسائل.",
               "ادفع المخالفات فقط عبر القنوات الرسمية (تم، تطبيق شرطة أبوظبي، تطبيق وزارة الداخلية)."],
    },
    "maps": {
        "en": ["Maps and search listings can be edited by anyone - fraudsters replace phone numbers and websites.",
               "Get customer-service numbers from the back of your card or the official website/app.",
               "Check that the website in the listing matches the company's official domain exactly."],
        "ar": ["نتائج الخرائط ومحركات البحث يمكن لأي شخص تعديلها - المحتالون يستبدلون الأرقام والمواقع.",
               "خذ أرقام خدمة العملاء من خلف بطاقتك أو من الموقع أو التطبيق الرسمي.",
               "تأكد أن الموقع المذكور في النتيجة يطابق النطاق الرسمي للشركة تماماً."],
    },
    "generic": {
        "en": ["Stop and verify before you click, pay or share any data.",
               "When in doubt, contact the organisation through its official number."],
        "ar": ["توقف وتحقق قبل أن تضغط أو تدفع أو تشارك أي بيانات.",
               "عند الشك، تواصل مع الجهة عبر رقمها الرسمي."],
    },
    "safe": {
        "en": ["No strong fraud indicators found - but stay alert: never share OTPs or passwords."],
        "ar": ["لم يتم العثور على مؤشرات احتيال قوية - لكن ابقَ يقظاً ولا تشارك رمز التحقق أو كلمة المرور."],
    },
}
