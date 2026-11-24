"""
Mirgab AI - knowledge base.

Everything the rule engine "knows" about the UAE fraud landscape lives here,
so analysts can update it without touching the analysis code.
"""

# --------------------------------------------------------------------------
# Fraud domains covered by Mirgab
# --------------------------------------------------------------------------
CATEGORIES = {
    "legit": {"en": "No fraud pattern", "ar": "لا يوجد نمط احتيال"},
    "real_estate": {"en": "Real-estate fraud / fake listing", "ar": "احتيال عقاري / إعلان وهمي"},
    "pharma": {"en": "Unlicensed medicine sales", "ar": "بيع أدوية من جهات غير مرخصة"},
    "fake_store": {"en": "Fake online store", "ar": "متجر إلكتروني وهمي"},
    "investment": {"en": "Investment fraud / suspicious platform", "ar": "احتيال استثماري / منصة مشبوهة"},
    "impersonation": {"en": "Government / bank impersonation", "ar": "انتحال جهة حكومية أو بنك"},
    "maps": {"en": "Fraudulent Google Maps listing link", "ar": "رابط احتيالي مرتبط بنتائج Google Maps"},
}

# --------------------------------------------------------------------------
# Official domains (allow-list).  Registered domain -> display name.
# --------------------------------------------------------------------------
OFFICIAL_DOMAINS = {
    # Government
    "u.ae": "UAE Government Portal",
    "adpolice.gov.ae": "Abu Dhabi Police",
    "dubaipolice.gov.ae": "Dubai Police",
    "moi.gov.ae": "Ministry of Interior",
    "mohap.gov.ae": "Ministry of Health & Prevention",
    "doh.gov.ae": "Department of Health - Abu Dhabi",
    "dha.gov.ae": "Dubai Health Authority",
    "icp.gov.ae": "ICP",
    "tamm.abudhabi": "TAMM",
    "rta.ae": "RTA",
    "dewa.gov.ae": "DEWA",
    "cbuae.gov.ae": "Central Bank of the UAE",
    "sca.gov.ae": "Securities & Commodities Authority",
    "dubailand.gov.ae": "Dubai Land Department",
    "adrec.gov.ae": "Abu Dhabi Real Estate Centre",
    "ecrimehub.gov.ae": "Dubai Police eCrime Hub",
    "emiratespost.ae": "Emirates Post",
    "salik.ae": "Salik",
    # Banks
    "emiratesnbd.com": "Emirates NBD",
    "adcb.com": "ADCB",
    "bankfab.com": "First Abu Dhabi Bank",
    "mashreq.com": "Mashreq",
    "dib.ae": "Dubai Islamic Bank",
    "adib.ae": "Abu Dhabi Islamic Bank",
    "rakbank.ae": "RAKBANK",
    "cbd.ae": "Commercial Bank of Dubai",
    # Telecom / delivery / marketplaces
    "etisalat.ae": "e& (Etisalat)",
    "eand.com": "e&",
    "du.ae": "du",
    "aramex.com": "Aramex",
    "noon.com": "noon",
    "amazon.ae": "Amazon UAE",
    "propertyfinder.ae": "Property Finder",
    "bayut.com": "Bayut",
    "dubizzle.com": "dubizzle",
    # Big platforms
    "google.com": "Google",
    "goo.gl": "Google (short links)",
    "youtube.com": "YouTube",
    "whatsapp.com": "WhatsApp",
}

# Brand keyword -> official registered domain.  If a URL contains the keyword
# but is NOT hosted on the official domain, it is a likely impersonation.
BRAND_KEYWORDS = {
    "adpolice": "adpolice.gov.ae",
    "abudhabipolice": "adpolice.gov.ae",
    "dubaipolice": "dubaipolice.gov.ae",
    "moi": "moi.gov.ae",
    "mohap": "mohap.gov.ae",
    "icp": "icp.gov.ae",
    "tamm": "tamm.abudhabi",
    "rta": "rta.ae",
    "salik": "salik.ae",
    "dewa": "dewa.gov.ae",
    "emiratesnbd": "emiratesnbd.com",
    "enbd": "emiratesnbd.com",
    "adcb": "adcb.com",
    "bankfab": "bankfab.com",
    "mashreq": "mashreq.com",
    "adib": "adib.ae",
    "rakbank": "rakbank.ae",
    "etisalat": "etisalat.ae",
    "aramex": "aramex.com",
    "emiratespost": "emiratespost.ae",
    "noon": "noon.com",
    "amazon": "amazon.ae",
    "bayut": "bayut.com",
    "propertyfinder": "propertyfinder.ae",
    "dubizzle": "dubizzle.com",
    "uaepass": "u.ae",
}

# Multi-label public suffixes we need to understand without network access.
MULTI_PART_SUFFIXES = {
    "gov.ae", "ac.ae", "co.ae", "net.ae", "org.ae", "sch.ae", "mil.ae",
    "co.uk", "org.uk", "com.sa", "gov.sa", "com.eg", "com.au", "co.in",
    "com.pk", "com.tr", "com.br",
}

SUSPICIOUS_TLDS = {
    "xyz", "top", "club", "online", "site", "icu", "buzz", "live", "vip",
    "cc", "tk", "ml", "ga", "cf", "gq", "work", "click", "link", "rest",
    "monster", "cyou", "sbs", "cfd", "lol", "quest", "bond", "pw", "win",
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy", "ow.ly",
    "shorturl.at", "tiny.cc", "s.id", "t.ly", "shorturl.asia", "v.gd",
}

GOOGLE_MAPS_HOSTS = {"maps.app.goo.gl", "maps.google.com", "goo.gl"}

SUSPICIOUS_PATH_WORDS = {
    "login", "signin", "verify", "verification", "update", "secure",
    "account", "banking", "payment", "pay", "otp", "kyc", "refund",
    "fine", "fines", "violation", "parcel", "customs", "unlock",
    "suspend", "confirm", "wallet", "claim", "reward", "gift",
}

DANGEROUS_EXTENSIONS = (".apk", ".exe", ".scr", ".bat", ".msi", ".zip", ".rar", ".js")

# --------------------------------------------------------------------------
# Text indicators.  Each rule: (id, category, weight 0-1, [patterns], en, ar)
# Patterns are lowercase; Arabic is matched after normalisation (see text.py).
# category "generic" applies to all domains.
# --------------------------------------------------------------------------
TEXT_RULES = [
    # ---------------- Generic manipulation ----------------
    ("urgency", "generic", 0.18,
     ["urgent", "immediately", "within 24 hours", "last chance", "act now", "today only",
      "expires today", "عاجل", "ادفع الحين", "بسرعه قبل", "فورا", "خلال 24 ساعه", "فرصه اخيره", "اليوم فقط", "لا تفوت"],
     "Creates pressure / urgency to act fast",
     "يستخدم أسلوب الاستعجال والضغط لاتخاذ قرار سريع"),
    ("sensitive_data", "generic", 0.35,
     ["otp", "cvv", "card number", "pin code", "password", "verification code",
      "emirates id number", "رمز التحقق", "رقم البطاقه", "الرقم السري", "كلمه المرور",
      "رمز otp", "بيانات البطاقه", "رقم الهويه"],
     "Asks for sensitive data (OTP, card, password, ID)",
     "يطلب بيانات حساسة مثل رمز التحقق أو رقم البطاقة أو كلمة المرور"),
    ("odd_payment", "generic", 0.30,
     ["gift card", "itunes card", "western union", "usdt", "bitcoin only",
      "crypto wallet", "personal account", "transfer to this account", "بطاقات هدايا",
      "بطاقه هدايا", "حساب شخصي", "محفظه كريبتو", "حول على الحساب", "تحويل على حساب"],
     "Requests payment through untraceable or personal channels",
     "يطلب الدفع بوسائل يصعب تتبعها أو إلى حساب شخصي"),
    ("click_link", "generic", 0.12,
     ["click the link", "via the link", "click here", "عبر الرابط", "اضغط على الرابط", "من الرابط",
      "ادخل على الرابط"],
     "Pushes you to click a link",
     "يدفعك للضغط على رابط"),
    ("off_platform", "generic", 0.15,
     ["whatsapp only", "contact on telegram", "telegram only", "dm only", "واتساب فقط",
      "تواصل واتساب فقط", "تيليجرام فقط", "راسلني خاص"],
     "Pushes communication to private chat apps only",
     "يحصر التواصل في تطبيقات المحادثة الخاصة فقط"),
    ("too_good", "generic", 0.20,
     ["100% guaranteed", "guaranteed", "risk free", "no risk", "free gift", "you have won",
      "congratulations you won", "مضمون 100", "مضمون", "بدون مخاطره", "مبروك فزت", "هديه مجانيه"],
     "Promises that are too good to be true",
     "يقدم وعوداً مبالغاً فيها يصعب تصديقها"),

    # ---------------- Real estate ----------------
    ("re_deposit", "real_estate", 0.35,
     ["deposit before viewing", "pay deposit to reserve", "booking fee before viewing",
      "transfer deposit", "عربون قبل المعاينه", "حول العربون", "دفع عربون", "عربون لحجز",
      "تحويل قبل المعاينه", "مبلغ الحجز", "ارسل مبلغ", "send money to hold",
      "to hold it", "عربون الحجز"],
     "Asks for a deposit before viewing the property",
     "يطلب دفع عربون قبل معاينة العقار"),
    ("re_owner_abroad", "real_estate", 0.30,
     ["owner is abroad", "owner outside the country", "keys will be sent", "keys by courier",
      "المالك خارج الدوله", "المالك مسافر", "نرسل لك المفاتيح", "انا مسافر",
      "مع المندوب", "can't show it", "mail you the keys", "ارسلك المفتاح"],
     "Owner 'abroad' and viewing not possible - classic rental scam",
     "المالك خارج الدولة ولا يمكن المعاينة - أسلوب شائع في الاحتيال العقاري"),
    ("re_cheap", "real_estate", 0.20,
     ["below market price", "urgent sale", "cheapest villa", "أقل من سعر السوق", "بيع مستعجل",
      "ارخص فيلا", "سعر لا يصدق"],
     "Price far below market value",
     "سعر أقل بكثير من سعر السوق"),
    ("re_no_contract", "real_estate", 0.25,
     ["no ejari", "no contract needed", "without contract", "بدون عقد", "بدون ايجاري",
      "بدون توثيق"],
     "Avoids an official contract / Ejari / Tawtheeq",
     "يتجنب العقد الرسمي أو التوثيق (إيجاري / توثيق)"),

    # ---------------- Pharma ----------------
    ("ph_no_rx", "pharma", 0.40,
     ["without prescription", "no prescription", "no rx", "بدون وصفه", "بدون وصفه طبيه",
      "بدون روشته"],
     "Sells prescription medicine without a prescription",
     "يبيع أدوية تحتاج وصفة طبية بدون وصفة"),
    ("ph_controlled", "pharma", 0.35,
     ["tramadol", "xanax", "alprazolam", "oxycodone", "pregabalin", "lyrica", "captagon",
      "ترامادول", "زاناكس", "ليريكا", "كبتاجون"],
     "Mentions controlled / high-risk medicines",
     "يذكر أدوية خاضعة للرقابة أو عالية الخطورة"),
    ("ph_miracle", "pharma", 0.30,
     ["miracle cure", "cures diabetes", "cure cancer", "lose 10kg in a week", "permanent cure",
      "علاج نهائي", "يعالج السكري", "يعالج السرطان", "تخسيس سريع", "خسارة 10 كيلو"],
     "Miracle-cure or unrealistic medical claims",
     "ادعاءات علاجية خارقة أو غير واقعية"),
    ("ph_weightloss", "pharma", 0.20,
     ["ozempic", "mounjaro", "slimming injection", "fat burner", "اوزمبيك", "مونجارو",
      "ابر التنحيف", "حرق الدهون"],
     "Weight-loss injections / slimming products sold online",
     "بيع إبر تنحيف أو منتجات تخسيس عبر الإنترنت"),
    ("ph_discreet", "pharma", 0.15,
     ["discreet delivery", "discreet packaging", "توصيل سري", "تغليف سري"],
     "'Discreet delivery' - typical of illegal medicine sellers",
     "\"توصيل سري\" - سمة شائعة لدى بائعي الأدوية غير المرخصين"),

    # ---------------- Fake store ----------------
    ("st_discount", "fake_store", 0.25,
     ["90% off", "80% off", "95% off", "clearance sale all items", "خصم 90", "خصم 80",
      "خصم 95", "تخفيضات تصل الى 90"],
     "Extreme, unrealistic discounts",
     "خصومات مبالغ فيها وغير واقعية"),
    ("st_transfer_only", "fake_store", 0.25,
     ["bank transfer only", "no cash on delivery", "prepayment only", "تحويل بنكي فقط",
      "لا يوجد دفع عند الاستلام", "الدفع مقدما فقط"],
     "Only accepts prepayment / bank transfer (no buyer protection)",
     "يقبل الدفع المسبق أو التحويل البنكي فقط دون حماية للمشتري"),
    ("st_no_returns", "fake_store", 0.15,
     ["no refunds", "no returns", "لا يوجد استرجاع", "لا استرداد"],
     "No refunds / returns",
     "لا يوجد استرجاع أو استرداد"),
    ("st_replica", "fake_store", 0.20,
     ["original at half price", "first copy", "master copy", "replica", "كوبي ون",
      "ماستر كوبي", "تقليد درجه اولى"],
     "Branded goods at impossible prices / replicas",
     "منتجات ماركات بأسعار مستحيلة أو مقلدة"),

    # ---------------- Investment ----------------
    ("in_returns", "investment", 0.40,
     ["guaranteed returns", "guaranteed profit", "daily profit", "double your money",
      "weekly returns", "ارباح مضمونه", "يوميا مضمونه", "اربح يوميا", "ارباح يوميه", "ربح يومي", "ضاعف اموالك", "عوائد اسبوعيه",
      "ربح مضمون"],
     "Guaranteed or unrealistic investment returns",
     "عوائد استثمارية مضمونة أو غير واقعية"),
    ("in_crypto", "investment", 0.15,
     ["crypto", "forex", "bitcoin", "trading signals", "binary options", "كريبتو",
      "فوركس", "بيتكوين", "تداول", "عملات رقميه"],
     "High-risk asset (crypto / forex) promoted to the public",
     "ترويج أصول عالية المخاطر (عملات رقمية / فوركس) للعامة"),
    ("in_referral", "investment", 0.25,
     ["invite friends", "referral bonus", "recruit", "join our vip group", "ادع اصدقائك",
      "مكافاه احاله", "انضم لقروب vip", "انضم للمجموعه", "اللي تسجلهم",
      "كل ما زاد عدد", "join his group", "dm me to join"],
     "Referral / recruitment model (possible Ponzi or pyramid)",
     "نموذج إحالة وتجنيد (احتمال مخطط بونزي أو هرمي)"),
    ("in_min_deposit", "investment", 0.15,
     ["minimum deposit", "start with only", "ابدا بـ", "الحد الادنى للايداع", "ابدا بمبلغ"],
     "Low entry deposit to hook victims",
     "إيداع أولي منخفض لاستدراج الضحايا"),

    # ---------------- Impersonation ----------------
    ("im_suspend", "impersonation", 0.35,
     ["account will be suspended", "account has been blocked", "card has been blocked",
      "سيتم ايقاف حسابك", "تم ايقاف حسابك", "تم حظر بطاقتك", "سيتم تجميد"],
     "Threatens account suspension",
     "يهدد بإيقاف الحساب أو البطاقة"),
    ("im_update_id", "impersonation", 0.30,
     ["update your emirates id", "update your details", "update your information",
      "تحديث الهويه", "تحديث بياناتك", "تحديث البيانات"],
     "Asks to 'update' personal details via a link",
     "يطلب \"تحديث البيانات\" عبر رابط"),
    ("im_fine", "impersonation", 0.30,
     ["traffic fine", "unpaid fine", "pay your fine", "violation", "مخالفه مروريه",
      "مخالفات غير مدفوعه", "سدد المخالفه", "عليك غرامه", "ادفعها الحين",
      "قبل ما تتضاعف", "غرامه مستحقه"],
     "Fake traffic fine / violation notice",
     "إشعار مخالفة مرورية وهمي"),
    ("im_parcel", "impersonation", 0.30,
     ["parcel is on hold", "shipment on hold", "customs fee", "delivery failed",
      "شحنتك معلقه", "رسوم جمركيه", "تعذر توصيل", "الشحنه محتجزه"],
     "Fake parcel / customs fee message",
     "رسالة شحنة أو رسوم جمركية وهمية"),
    ("im_gov_claim", "impersonation", 0.10,
     ["abu dhabi police", "dubai police", "ministry of interior", "central bank",
      "شرطه ابوظبي", "شرطه دبي", "وزاره الداخليه", "المصرف المركزي"],
     "Claims to come from a government authority",
     "يدّعي أنه صادر عن جهة حكومية"),

    # ---------------- Maps listing fraud ----------------
    ("mp_listing", "maps", 0.20,
     ["google maps", "found you on maps", "maps listing", "خرائط جوجل", "قوقل ماب",
      "جوجل ماب"],
     "Business contact obtained from a Maps / search listing",
     "بيانات التواصل مأخوذة من نتائج الخرائط أو محرك البحث"),
    ("mp_customer_service", "maps", 0.20,
     ["customer service number", "call center number", "hotline", "رقم خدمه العملاء",
      "رقم مركز الاتصال", "الخط الساخن"],
     "'Customer service' number from a listing - common hijack target",
     "رقم \"خدمة عملاء\" من نتائج البحث - هدف شائع للتلاعب"),
]

# Trust signals reduce risk slightly (they can be faked, so the effect is small)
TRUST_RULES = [
    ("permit", 0.10,
     ["rera", "trakheesi", "permit number", "adrec", "رقم التصريح", "ترخيص رقم", "ريرا"],
     "Mentions a regulatory permit / licence number",
     "يذكر رقم تصريح أو ترخيص رسمي"),
    ("rx_required", 0.12,
     ["prescription required", "valid prescription", "يتطلب وصفه", "بوصفه طبيه"],
     "Requires a valid prescription",
     "يشترط وصفة طبية سارية"),
    ("never_ask", 0.15,
     ["we will never ask", "never share your otp", "لن نطلب منك", "لا تشارك رمز"],
     "Contains standard anti-fraud warning",
     "يحتوي على تحذير معتاد ضد الاحتيال"),
    ("regulated", 0.10,
     ["licensed by sca", "regulated by", "dfsa", "fsra", "مرخص من هيئه الاوراق الماليه"],
     "Claims regulation by a named authority (verify it!)",
     "يدّعي ترخيصاً من جهة رقابية مسماة (تحقق منه)"),
]

# Which harm dimensions each category touches (0-1)
IMPACT_MATRIX = {
    "real_estate":   {"financial": 0.95, "health": 0.05, "identity": 0.40, "social": 0.60},
    "pharma":        {"financial": 0.50, "health": 1.00, "identity": 0.30, "social": 0.50},
    "fake_store":    {"financial": 0.80, "health": 0.10, "identity": 0.55, "social": 0.25},
    "investment":    {"financial": 1.00, "health": 0.15, "identity": 0.45, "social": 0.70},
    "impersonation": {"financial": 0.90, "health": 0.05, "identity": 1.00, "social": 0.60},
    "maps":          {"financial": 0.75, "health": 0.10, "identity": 0.80, "social": 0.40},
    "legit":         {"financial": 0.0, "health": 0.0, "identity": 0.0, "social": 0.0},
}

RISK_LEVELS = [
    (0, 25, "safe", {"en": "Low risk", "ar": "خطورة منخفضة"}),
    (25, 50, "caution", {"en": "Be cautious", "ar": "توخَّ الحذر"}),
    (50, 75, "suspicious", {"en": "Suspicious", "ar": "مشبوه"}),
    (75, 101, "critical", {"en": "Critical - likely fraud", "ar": "خطير - احتيال مرجّح"}),
]

REPORTING = {
    "en": [
        "Abu Dhabi Police Aman service: call 8002626 or SMS 2828",
        "Email: aman@adpolice.gov.ae or the Abu Dhabi Police smart app",
        "Ministry of Interior eCrimes platform (MOI UAE app)",
        "If you already paid: call your bank immediately to stop the transfer",
    ],
    "ar": [
        "خدمة أمان - شرطة أبوظبي: اتصل على 8002626 أو أرسل رسالة نصية إلى 2828",
        "البريد: aman@adpolice.gov.ae أو تطبيق شرطة أبوظبي الذكي",
        "منصة الجرائم الإلكترونية - وزارة الداخلية (تطبيق MOI UAE)",
        "إذا دفعت بالفعل: اتصل ببنكك فوراً لإيقاف التحويل",
    ],
}
