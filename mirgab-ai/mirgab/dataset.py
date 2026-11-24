"""
Synthetic bilingual seed dataset (Arabic + English).

IMPORTANT: this is a *seed* dataset generated from templates so the prototype
can be trained offline.  For production, replace / extend it with real,
anonymised and labelled cases (e.g. reports received through Abu Dhabi
Police's Aman service).  Put extra rows in data/extra_samples.csv with
columns: text,label  - they are picked up automatically by train.py.
"""
import random

AREAS_EN = ["Al Reem Island", "Khalifa City", "Yas Island", "Al Raha Beach", "Saadiyat", "Mussafah",
            "Dubai Marina", "JLT", "Al Khalidiyah", "Mohammed Bin Zayed City"]
AREAS_AR = ["جزيرة الريم", "مدينة خليفة", "جزيرة ياس", "شاطئ الراحة", "السعديات", "مصفح",
            "دبي مارينا", "الخالدية", "مدينة محمد بن زايد", "الشامخة"]
BANKS_EN = ["ADCB", "FAB", "Emirates NBD", "ADIB", "Mashreq", "your bank"]
BANKS_AR = ["بنك أبوظبي التجاري", "بنك أبوظبي الأول", "الإمارات دبي الوطني", "مصرف أبوظبي الإسلامي", "المشرق", "البنك"]
DRUGS = ["Tramadol", "Xanax", "Lyrica", "Ozempic", "Mounjaro", "slimming capsules", "fat burner"]
DRUGS_AR = ["ترامادول", "زاناكس", "ليريكا", "أوزمبيك", "مونجارو", "كبسولات تخسيس", "حبوب حرق الدهون"]
PRODUCTS = ["iPhone 17 Pro", "PlayStation 5", "Rolex watch", "Dyson hair dryer", "Gucci bag", "Samsung TV 75 inch"]
PRODUCTS_AR = ["ايفون 17 برو", "بلايستيشن 5", "ساعة رولكس", "مجفف دايسون", "شنطة قوتشي", "تلفزيون سامسونج 75 بوصة"]
LINKS = ["bit.ly/3xYz", "adcb-secure-update.com", "uae-fines-pay.xyz", "emiratespost-track.top",
         "tamm-services.online", "invest-gold-uae.vip", "cheap-meds-uae.shop"]


def _r(seq):
    return random.choice(seq)


FRAUD_TEMPLATES = {
    "real_estate": [
        lambda: f"Luxury 3BR villa in {_r(AREAS_EN)} for only {random.randint(800, 1400)} AED monthly. Owner is abroad, pay deposit to reserve and keys will be sent by courier. WhatsApp only.",
        lambda: f"Urgent sale! Apartment in {_r(AREAS_EN)} below market price. Transfer deposit today to secure it, viewing after payment.",
        lambda: f"Studio for rent {_r(AREAS_EN)}, no Ejari needed, no contract needed, pay booking fee before viewing.",
        lambda: f"Owner outside the country, renting my apartment in {_r(AREAS_EN)} cheap. Send deposit to my personal account and I will courier the keys.",
        lambda: f"فيلا فاخرة في {_r(AREAS_AR)} بإيجار {random.randint(900, 1400)} درهم شهري فقط. المالك خارج الدولة، حول العربون ونرسل لك المفاتيح.",
        lambda: f"شقة للإيجار في {_r(AREAS_AR)} بأقل من سعر السوق، بدون عقد وبدون إيجاري. دفع عربون قبل المعاينة. تواصل واتساب فقط.",
        lambda: f"بيع مستعجل! أرخص فيلا في {_r(AREAS_AR)}، المالك مسافر، تحويل قبل المعاينة لحجز العقار.",
        lambda: f"الشقة في {_r(AREAS_AR)} للحين متوفرة بس انا برا الدولة، حول مبلغ الحجز وبطرش لك المفتاح مع المندوب",
        lambda: f"فيلا {_r(AREAS_AR)} لقطة، المالك مب موجود بالبلاد، اذا تبيها لازم تحجز اليوم وتحول العربون",
        lambda: f"استوديو في {_r(AREAS_AR)} سعر لا يصدق، حول العربون اليوم فقط والمفاتيح توصلك بالبريد.",
    ],
    "pharma": [
        lambda: f"Buy {_r(DRUGS)} without prescription, discreet delivery anywhere in UAE. Order on WhatsApp.",
        lambda: f"{_r(DRUGS)} available no prescription needed, 100% original, discreet packaging, cash or transfer.",
        lambda: "Miracle cure! Our herbal capsules cure diabetes permanently in 30 days. Guaranteed results.",
        lambda: "Lose 10kg in a week with our slimming injection, no doctor needed, fast delivery.",
        lambda: f"متوفر {_r(DRUGS_AR)} بدون وصفة طبية، توصيل سري لجميع الإمارات. اطلب الآن واتساب.",
        lambda: "علاج نهائي للسكري بالأعشاب، نتائج مضمونة 100% خلال شهر. اطلب الآن.",
        lambda: f"ابر التنحيف {_r(['أوزمبيك', 'مونجارو'])} بدون وصفة، خسارة 10 كيلو بأسبوع، تغليف سري.",
        lambda: f"حبوب {_r(DRUGS_AR)} أصلية بدون روشتة، توصيل سري وسريع.",
    ],
    "fake_store": [
        lambda: f"{_r(PRODUCTS)} 90% off! Only {random.randint(199, 599)} AED. Bank transfer only, no cash on delivery, limited stock.",
        lambda: f"Clearance sale all items 80% off, original {_r(PRODUCTS)} at half price. Prepayment only, no refunds.",
        lambda: f"Master copy {_r(PRODUCTS)} first copy best quality, pay in advance, no returns. Today only!",
        lambda: f"Brand new {_r(PRODUCTS)} for {random.randint(150, 400)} AED, shop closing. Transfer to this account to confirm order.",
        lambda: f"{_r(PRODUCTS_AR)} بخصم 90% فقط {random.randint(199, 599)} درهم! تحويل بنكي فقط ولا يوجد دفع عند الاستلام.",
        lambda: f"تخفيضات تصل إلى 90% على {_r(PRODUCTS_AR)}، الدفع مقدما فقط، لا يوجد استرجاع. العرض اليوم فقط.",
        lambda: f"{_r(PRODUCTS_AR)} ماستر كوبي تقليد درجة أولى، حول المبلغ على الحساب لتأكيد الطلب.",
        lambda: f"متجر يغلق! {_r(PRODUCTS_AR)} جديد بسعر لا يصدق، الدفع مقدما فقط. لا تفوت الفرصة.",
    ],
    "investment": [
        lambda: f"Guaranteed returns of {random.randint(20, 60)}% weekly! Invest in our crypto trading platform. Minimum deposit {random.choice([250, 500, 1000])} AED.",
        lambda: "Double your money in 7 days with AI forex trading. No risk, daily profit paid in USDT. Join our VIP group.",
        lambda: "Earn daily profit from home, invite friends and get referral bonus. Start with only 100 dollars, guaranteed profit.",
        lambda: "Bitcoin investment opportunity, risk free, guaranteed returns, our experts trade for you. Contact on Telegram.",
        lambda: f"أرباح مضمونة {random.randint(20, 60)}% أسبوعياً! استثمر في منصة تداول العملات الرقمية. الحد الأدنى للإيداع {random.choice([500, 1000])} درهم.",
        lambda: "ضاعف أموالك خلال أسبوع مع تداول الفوركس بالذكاء الاصطناعي، بدون مخاطرة وربح يومي. انضم لقروب VIP.",
        lambda: "ربح يومي من البيت! ادع أصدقائك واحصل على مكافأة إحالة. ابدأ بمبلغ 100 دولار فقط، ربح مضمون.",
        lambda: "سجل في المنصة واربح يوميا ارباح مضمونة، وكل ما جبت ناس اكثر زاد ربحك",
        lambda: "خويي حول 2000 وصارت 20 الف خلال اسبوعين، كلمني ادخلك القروب",
        lambda: "فرصة استثمار في بيتكوين بدون مخاطرة وعوائد أسبوعية مضمونة. تيليجرام فقط.",
    ],
    "impersonation": [
        lambda: f"Dear customer, your {_r(BANKS_EN)} account will be suspended. Update your Emirates ID immediately: {_r(LINKS)}",
        lambda: f"Abu Dhabi Police: you have an unpaid traffic fine of {random.randint(400, 3000)} AED. Pay your fine within 24 hours to avoid penalty: {_r(LINKS)}",
        lambda: f"Emirates Post: your parcel is on hold due to unpaid customs fee of {random.randint(5, 30)} AED. Pay now {_r(LINKS)}",
        lambda: f"{_r(BANKS_EN)}: your card has been blocked. Share the OTP sent to you to reactivate.",
        lambda: f"Ministry of Interior: update your information to avoid suspension of your services {_r(LINKS)}",
        lambda: f"عميلنا العزيز، سيتم إيقاف حسابك في {_r(BANKS_AR)}. يرجى تحديث الهوية فوراً عبر الرابط {_r(LINKS)}",
        lambda: f"شرطة أبوظبي: لديك مخالفة مرورية غير مدفوعة بقيمة {random.randint(400, 3000)} درهم، سدد المخالفة خلال 24 ساعة {_r(LINKS)}",
        lambda: f"بريد الإمارات: شحنتك معلقة بسبب رسوم جمركية {random.randint(5, 30)} درهم، ادفع الآن {_r(LINKS)}",
        lambda: f"{_r(BANKS_AR)}: تم حظر بطاقتك، أرسل رمز التحقق لإعادة التفعيل.",
        lambda: f"تنبيه: عليك غرامة مستحقة، ادفعها الحين عبر الرابط {_r(LINKS)} قبل ما تزيد",
        lambda: f"عزيزي العميل حسابك بينقفل اليوم، ادخل على الرابط وحدث بياناتك {_r(LINKS)}",
        lambda: "وزارة الداخلية: يرجى تحديث بياناتك لتجنب تجميد الخدمات. أدخل رقم البطاقة والرقم السري.",
    ],
}

LEGIT_TEMPLATES = [
    # real estate - legit
    lambda: f"2BR apartment for rent in {_r(AREAS_EN)}, {random.randint(70, 140)},000 AED per year, 4 cheques. RERA permit number {random.randint(10000, 99999)}. Viewing available any day, contract registered via Tawtheeq.",
    lambda: f"شقة غرفتين للإيجار في {_r(AREAS_AR)} بسعر {random.randint(70, 140)} ألف درهم سنوياً، رقم التصريح {random.randint(10000, 99999)}. المعاينة متاحة والعقد موثق عبر توثيق.",
    lambda: f"Villa for sale in {_r(AREAS_EN)}, listed through licensed agency, ADREC registered. Book a viewing with our broker.",
    # pharma - legit
    lambda: "Pharmacy delivery: prescription required for prescription medicines. Upload a valid prescription through our licensed app.",
    lambda: "صيدلية مرخصة من دائرة الصحة: الأدوية الموصوفة تتطلب وصفة طبية سارية. التوصيل خلال ساعتين.",
    lambda: "Flu season reminder: get your vaccine at the nearest health centre. Consult your doctor before taking any medication.",
    lambda: "تذكير: احجز موعد التطعيم ضد الإنفلونزا في أقرب مركز صحي، واستشر طبيبك قبل تناول أي دواء.",
    # store - legit
    lambda: f"White Friday deals: up to 30% off on {_r(PRODUCTS)}. Cash on delivery and 15-day free returns.",
    lambda: f"عروض الجمعة البيضاء: خصم حتى 30% على {_r(PRODUCTS_AR)}، الدفع عند الاستلام وإرجاع مجاني خلال 15 يوماً.",
    lambda: "Your order has been shipped and will arrive tomorrow. Track it from the app.",
    lambda: "تم شحن طلبك وسيصلك غداً، يمكنك تتبع الطلب من التطبيق.",
    # investment - legit
    lambda: "Our fund is licensed by SCA. Past performance does not guarantee future returns. Please read the prospectus before investing.",
    lambda: "الصندوق مرخص من هيئة الأوراق المالية والسلع، الأداء السابق لا يضمن العوائد المستقبلية. يرجى قراءة نشرة الاكتتاب.",
    lambda: "Monthly statement for your savings account is now available in online banking.",
    lambda: "كشف الحساب الشهري لحساب التوفير متاح الآن في الخدمات المصرفية عبر الإنترنت.",
    # bank / government - legit
    lambda: f"{_r(BANKS_EN)}: we will never ask for your OTP, PIN or password. Never share your OTP with anyone.",
    lambda: f"{_r(BANKS_AR)}: لن نطلب منك أبداً رمز التحقق أو الرقم السري. لا تشارك رمز التحقق مع أي شخص.",
    lambda: "Abu Dhabi Police reminds the public to report fraud attempts via Aman service 8002626.",
    lambda: "شرطة أبوظبي تذكر الجمهور بالإبلاغ عن محاولات الاحتيال عبر خدمة أمان 8002626.",
    lambda: "Your Emirates ID renewal request has been received. Track status through the official ICP app.",
    lambda: "تم استلام طلب تجديد الهوية، يمكنك متابعة الطلب عبر تطبيق الهيئة الاتحادية الرسمي.",
    lambda: f"Your salary of AED {random.randint(5, 40)},{random.randint(100, 999)} has been credited to your account.",
    lambda: "Meeting tomorrow at 10am to review the project plan. Please bring the latest numbers.",
    lambda: "اجتماع بكرة الساعة 10 لمراجعة خطة المشروع، يرجى إحضار آخر الأرقام.",
    lambda: f"Family weekend at {_r(AREAS_EN)}: beach, dinner and shopping. Who is joining?",
    lambda: "وين بنتلاقى اليوم؟ خلنا نروح المول بعد الدوام",
    lambda: "تم دفع فاتورة الكهرباء بنجاح عبر التطبيق الرسمي، شكراً لك",
    lambda: "مطعم جديد افتتح في الخالدية، الأسعار معقولة والخدمة ممتازة.",
]


def build_dataset(n_per_class: int = 120, seed: int = 42):
    random.seed(seed)
    rows = []
    for label, templates in FRAUD_TEMPLATES.items():
        for i in range(n_per_class):
            rows.append((templates[i % len(templates)](), label))
    for i in range(n_per_class * 2):
        rows.append((LEGIT_TEMPLATES[i % len(LEGIT_TEMPLATES)](), "legit"))
    random.shuffle(rows)
    return rows
