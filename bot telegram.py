from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes, CallbackQueryHandler
import random
import asyncio

TOKEN = "PUT_YOUR_TOKEN_HERE"

# ─────────────────────────────────────────
# 🧠 الذاكرة
# ─────────────────────────────────────────
memory = {}
games_xo = {}
guess_games = {}
higher_lower_games = {}
capitals_games = {}
trivia_waiting = {}  # ← جديد

DICE_FACES = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣"]
SLOT_SYMBOLS = ["🍒","🍋","🍊","⭐","💎","🔔"]

# ─────────────────────────────────────────
# 🌍 عواصم الدول
# ─────────────────────────────────────────
CAPITALS = [
    ("فرنسا","باريس"), ("ألمانيا","برلين"), ("اليابان","طوكيو"),
    ("البرازيل","برازيليا"), ("كندا","أوتاوا"), ("أستراليا","كانبيرا"),
    ("مصر","القاهرة"), ("السعودية","الرياض"), ("الإمارات","أبوظبي"),
    ("الكويت","الكويت"), ("قطر","الدوحة"), ("الأردن","عمان"),
    ("المغرب","الرباط"), ("تونس","تونس"), ("الجزائر","الجزائر"),
    ("العراق","بغداد"), ("سوريا","دمشق"), ("لبنان","بيروت"),
    ("تركيا","أنقرة"), ("إيران","طهران"), ("باكستان","إسلام آباد"),
    ("الهند","نيودلهي"), ("الصين","بكين"), ("روسيا","موسكو"),
    ("إيطاليا","روما"), ("إسبانيا","مدريد"), ("البرتغال","لشبونة"),
    ("هولندا","أمستردام"), ("بلجيكا","بروكسل"), ("السويد","ستوكهولم"),
    ("النرويج","أوسلو"), ("الدنمارك","كوبنهاغن"), ("سويسرا","برن"),
    ("النمسا","فيينا"), ("بولندا","وارسو"), ("اليونان","أثينا"),
    ("المكسيك","مكسيكو سيتي"), ("الأرجنتين","بوينس آيرس"), ("كولومبيا","بوغوتا"),
    ("نيجيريا","أبوجا"), ("كينيا","نيروبي"), ("إثيوبيا","أديس أبابا"),
    ("جنوب أفريقيا","بريتوريا"), ("غانا","أكرا"), ("المملكة المتحدة","لندن"),
    ("أمريكا","واشنطن"), ("كوريا الجنوبية","سيول"), ("إندونيسيا","جاكرتا"),
    ("ماليزيا","كوالالمبور"), ("تايلاند","بانكوك"),
]

# ─────────────────────────────────────────
# ❓ تريفيا - 120 سؤال بدون خيارات
# ─────────────────────────────────────────
TRIVIA = [
    # 🌍 جغرافيا
    {"q":"ما هي عاصمة فرنسا؟","a":"باريس"},
    {"q":"ما هي أكبر قارة في العالم؟","a":"آسيا"},
    {"q":"ما هو أطول نهر في العالم؟","a":"النيل"},
    {"q":"ما هي أكبر دولة في العالم مساحة؟","a":"روسيا"},
    {"q":"ما هي عاصمة اليابان؟","a":"طوكيو"},
    {"q":"ما هي عاصمة البرازيل؟","a":"برازيليا"},
    {"q":"ما هو أعمق بحيرة في العالم؟","a":"بايكال"},
    {"q":"ما هي أصغر قارة في العالم؟","a":"أستراليا"},
    {"q":"ما هو أعلى جبل في العالم؟","a":"إيفرست"},
    {"q":"في أي قارة توجد مصر؟","a":"أفريقيا"},
    {"q":"ما هي عاصمة كندا؟","a":"أوتاوا"},
    {"q":"ما هي عاصمة أستراليا؟","a":"كانبيرا"},
    {"q":"ما هو أكبر محيط في العالم؟","a":"الهادئ"},
    {"q":"كم عدد قارات العالم؟","a":"7"},
    {"q":"ما هي عاصمة ألمانيا؟","a":"برلين"},
    {"q":"ما هي عاصمة إيطاليا؟","a":"روما"},
    {"q":"ما هي عاصمة إسبانيا؟","a":"مدريد"},
    {"q":"ما هي عاصمة الصين؟","a":"بكين"},
    {"q":"ما هي عاصمة روسيا؟","a":"موسكو"},
    {"q":"ما هي عاصمة المملكة العربية السعودية؟","a":"الرياض"},
    # 🔬 علوم
    {"q":"ما هو أكبر كوكب في المجموعة الشمسية؟","a":"المشتري"},
    {"q":"كم عدد أيام السنة الكبيسة؟","a":"366"},
    {"q":"ما هو الغاز الأكثر وفرة في الهواء؟","a":"النيتروجين"},
    {"q":"ما هو رمز الذهب في الجدول الدوري؟","a":"Au"},
    {"q":"كم عدد عظام جسم الإنسان البالغ؟","a":"206"},
    {"q":"ما هو أصغر كوكب في المجموعة الشمسية؟","a":"عطارد"},
    {"q":"كم عدد أسنان الإنسان البالغ؟","a":"32"},
    {"q":"ما هو رمز الماء الكيميائي؟","a":"H2O"},
    {"q":"ما هو أسرع حيوان في العالم؟","a":"الفهد"},
    {"q":"كم عدد ألوان قوس قزح؟","a":"7"},
    {"q":"ما هو العنصر الأخف في الجدول الدوري؟","a":"الهيدروجين"},
    {"q":"كم عدد كروموسومات الإنسان؟","a":"46"},
    {"q":"ما هو رمز الحديد في الجدول الدوري؟","a":"Fe"},
    {"q":"ما هو أكبر عضو في جسم الإنسان؟","a":"الجلد"},
    {"q":"كم عدد غرف القلب؟","a":"4"},
    # 📚 تاريخ
    {"q":"من بنى الأهرامات؟","a":"المصريون"},
    {"q":"في أي سنة اكتشف كولومبوس أمريكا؟","a":"1492"},
    {"q":"من هو أول إنسان وصل للقمر؟","a":"نيل أرمسترونج"},
    {"q":"في أي سنة قامت الحرب العالمية الأولى؟","a":"1914"},
    {"q":"من اخترع الهاتف؟","a":"بيل"},
    {"q":"من اخترع المصباح الكهربائي؟","a":"إديسون"},
    {"q":"في أي سنة سقط جدار برلين؟","a":"1989"},
    {"q":"من كتب روميو وجولييت؟","a":"شكسبير"},
    {"q":"في أي سنة انتهت الحرب العالمية الثانية؟","a":"1945"},
    {"q":"من اخترع الطائرة؟","a":"رايت"},
    {"q":"من هو أول رئيس للولايات المتحدة؟","a":"واشنطن"},
    {"q":"في أي سنة قامت الثورة الفرنسية؟","a":"1789"},
    {"q":"في أي سنة هبط الإنسان على القمر؟","a":"1969"},
    {"q":"من اخترع الطباعة؟","a":"غوتنبرغ"},
    {"q":"في أي مدينة ولد النبي محمد صلى الله عليه وسلم؟","a":"مكة"},
    # ⚽ رياضة
    {"q":"كم عدد لاعبي كرة القدم في الفريق الواحد؟","a":"11"},
    {"q":"كم مدة مباراة كرة القدم بالدقيقة؟","a":"90"},
    {"q":"في أي دولة اخترعت كرة القدم؟","a":"إنجلترا"},
    {"q":"كم عدد حلقات شعار الأولمبياد؟","a":"5"},
    {"q":"كم عدد لاعبي كرة السلة في الفريق الواحد؟","a":"5"},
    {"q":"في أي مدينة أقيمت أول ألعاب أولمبية حديثة؟","a":"أثينا"},
    {"q":"كم عدد لاعبي الكرة الطائرة في الفريق؟","a":"6"},
    {"q":"من فاز بأكثر كؤوس العالم في كرة القدم؟","a":"البرازيل"},
    {"q":"كم عدد لاعبي كرة اليد في الفريق؟","a":"7"},
    {"q":"كم طول ملعب كرة القدم الرسمي بالمتر؟","a":"105"},
    # 🎬 فن وثقافة
    {"q":"من رسم الموناليزا؟","a":"ليوناردو دافنشي"},
    {"q":"في أي دولة تقع هوليوود؟","a":"أمريكا"},
    {"q":"من كتب روايات هاري بوتر؟","a":"رولينج"},
    {"q":"من ألّف سيمفونية القدر؟","a":"بيتهوفن"},
    {"q":"من كتب رواية البؤساء؟","a":"فيكتور هوغو"},
    {"q":"ما هي أشهر لوحة في العالم؟","a":"الموناليزا"},
    {"q":"من كتب قصيدة الإلياذة؟","a":"هوميروس"},
    {"q":"في أي دولة ولد موزارت؟","a":"النمسا"},
    {"q":"في أي دولة تأسست شركة ديزني؟","a":"أمريكا"},
    {"q":"من كتب رواية الجريمة والعقاب؟","a":"دوستويفسكي"},
    # 💻 تقنية
    {"q":"من أسس شركة آبل؟","a":"جوبز"},
    {"q":"في أي سنة تأسست شركة مايكروسوفت؟","a":"1975"},
    {"q":"من أسس شركة فيسبوك؟","a":"زوكربيرغ"},
    {"q":"ما هو أكثر نظام تشغيل استخداماً في العالم؟","a":"ويندوز"},
    {"q":"في أي سنة أُطلق أول آيفون؟","a":"2007"},
    {"q":"من أسس شركة تسلا؟","a":"ماسك"},
    {"q":"من أسس شركة أمازون؟","a":"بيزوس"},
    {"q":"في أي سنة أُطلق موقع يوتيوب؟","a":"2005"},
    {"q":"من أسس شركة تويتر؟","a":"جاك دورسي"},
    {"q":"في أي سنة تأسست شركة غوغل؟","a":"1998"},
    # 🌿 طبيعة وحيوانات
    {"q":"ما هو أكبر حيوان في العالم؟","a":"الحوت الأزرق"},
    {"q":"كم عدد أرجل العنكبوت؟","a":"8"},
    {"q":"ما هو أطول حيوان في العالم؟","a":"الزرافة"},
    {"q":"كم عدد أرجل الحشرات؟","a":"6"},
    {"q":"ما هو أثقل حيوان بري؟","a":"الفيل"},
    {"q":"كم عدد قلوب الأخطبوط؟","a":"3"},
    {"q":"ما هو أذكى حيوان بري؟","a":"الشمبانزي"},
    {"q":"ما هو الحيوان الذي ينام واقفاً؟","a":"الحصان"},
    {"q":"ما هو أسرع طائر في العالم؟","a":"الصقر"},
    {"q":"كم عدد أسنان الفيل؟","a":"4"},
    # 🔢 رياضيات
    {"q":"كم يساوي جذر 144؟","a":"12"},
    {"q":"كم يساوي 15 × 15؟","a":"225"},
    {"q":"ما هو أول عدد أولي؟","a":"2"},
    {"q":"كم يساوي 1000 ÷ 8؟","a":"125"},
    {"q":"كم عدد درجات المثلث؟","a":"180"},
    {"q":"ما هي قيمة باي π تقريباً؟","a":"3.14"},
    {"q":"كم يساوي 99 × 99؟","a":"9801"},
    {"q":"كم عدد درجات الدائرة الكاملة؟","a":"360"},
    {"q":"كم يساوي 7 × 8؟","a":"56"},
    {"q":"كم يساوي 2 أس 10؟","a":"1024"},
    # 🌙 دين وحضارة إسلامية
    {"q":"كم عدد سور القرآن الكريم؟","a":"114"},
    {"q":"ما هي أطول سورة في القرآن؟","a":"البقرة"},
    {"q":"كم عدد أركان الإسلام؟","a":"5"},
    {"q":"كم عدد أنبياء الإسلام المذكورين في القرآن؟","a":"25"},
    {"q":"ما هي أقصر سورة في القرآن؟","a":"الكوثر"},
    {"q":"ما هي أول كلمة نزلت في القرآن؟","a":"اقرأ"},
    {"q":"كم عدد آيات سورة الفاتحة؟","a":"7"},
    {"q":"كم عدد أيام شهر رمضان؟","a":"30"},
    {"q":"ما هي القبلة التي يتجه إليها المسلمون؟","a":"الكعبة"},
    {"q":"كم عدد الصلوات المفروضة في اليوم؟","a":"5"},
    # 🍎 طعام وصحة
    {"q":"ما هو الفيتامين الموجود في البرتقال؟","a":"C"},
    {"q":"كم لتر ماء يحتاج الإنسان يومياً؟","a":"2"},
    {"q":"ما هو المعدن الموجود في الحليب؟","a":"الكالسيوم"},
    {"q":"كم نبضة يضرب القلب في الدقيقة تقريباً؟","a":"72"},
    {"q":"كم درجة حرارة جسم الإنسان الطبيعية؟","a":"37"},
    {"q":"ما هو العضو الذي يضخ الدم؟","a":"القلب"},
    {"q":"كم عدد الرئتين في جسم الإنسان؟","a":"2"},
    {"q":"ما هو أغنى طعام بالحديد؟","a":"السبانخ"},
    {"q":"ما هو الجهاز المسؤول عن الهضم؟","a":"المعدة"},
    {"q":"كم عدد العظام في اليد الواحدة؟","a":"27"},
]

trivia_games = {}
trivia_waiting = {}

# ─────────────────────────────────────────
# 🗣️ شجرة الحوار
# ─────────────────────────────────────────
CONVERSATION_TREE = {
    "greet": {
        "triggers": ["سلام","مرحبا","هلا","أهلاً","هلو","صباح","مساء","هاي"],
        "responses": ["أهلاً {name}! 👋 كيف حالك اليوم؟","وعليكم السلام يا {name}! 😊 كيف يومك؟","هلا والله يا {name}! 🤝 كيف الأحوال؟"],
        "next": "waiting_how_are_you"
    },
    "how_are_you_q": {
        "triggers": ["كيف حالك","كيفك","شلونك","كيف الحال","عامل"],
        "responses": ["أنا بخير الحمد لله! 😄 وأنت يا {name}، كيف حالك؟","ممتاز والحمد لله! وأنت؟ 🙂"],
        "next": "waiting_how_are_you"
    },
    "reply_good": {
        "triggers": ["بخير","تمام","زين","ممتاز","منيح","كويس","الحمد لله","مرتاح","سعيد","فرحان","مبسوط","نشيط"],
        "context_required": "waiting_how_are_you",
        "responses": ["الحمد لله! يسعد يومك يا {name} 😊 شو أقدر أساعدك؟","هذا يسعدني! 🌟 شو في جديد؟","ماشاء الله! الله يديم عليك الصحة 💙"],
        "next": "idle"
    },
    "reply_bad": {
        "triggers": ["تعبان","مو بخير","زعلان","حزين","مرهق","متعب","ما زين","مو كويس","ضايق"],
        "context_required": "waiting_how_are_you",
        "responses": ["الله يشفيك ويعافيك يا {name} 💙 شو صاير؟ حكيلي...","آسف أسمع هذا 😔 أنا هنا، بتحكيلي إيش في؟"],
        "next": "waiting_problem"
    },
    "reply_so_so": {
        "triggers": ["عادي","نص نص","ماشي","أوكي","oki","okay","لا بأس"],
        "context_required": "waiting_how_are_you",
        "responses": ["عادي أحسن من لا شي! 😄 شو في؟","إن شاء الله يتحسن يومك يا {name} 🌟"],
        "next": "idle"
    },
    "share_problem": {
        "triggers": ["شغل","دراسة","تعب","ضغط","أهل","صديق","علاقة","فلوس","مال"],
        "context_required": "waiting_problem",
        "responses": ["فهمت عليك يا {name}... هذا الشي صعب فعلاً 😔 بتعدي إن شاء الله 💙","الله يصبّرك ويعينك 🤍 أنا هنا أسمعك..."],
        "next": "idle"
    },
    "thanks": {
        "triggers": ["شكراً","شكرا","مشكور","يسلمو","تسلم","يعطيك"],
        "responses": ["العفو يا {name}! 😊 في شي ثاني أقدر أساعدك؟","لا شكر على واجب! 🤝 أنا دايم هنا."],
        "next": "idle"
    },
    "bye": {
        "triggers": ["باي","مع السلامة","وداعاً","الله معك","أشوفك","لاحقاً"],
        "responses": ["مع السلامة يا {name}! 👋 أشوفك قريب إن شاء الله 😊","الله يسلمك! 🤝 أي وقت تحتاجني أنا هنا."],
        "next": "idle"
    },
    "joke": {
        "triggers": ["نكتة","ضحكني","اضحك","شي مضحك"],
        "responses": [
            "تفضل 😄:\nليش الكتاب حزين؟ لأن له ورق بس ما له فلوس 😂",
            "حاضر 😅:\nسألوا الكسول: ليش ما نجحت؟ قال: ما لاحقت 😂",
            "هذي حلوة 🤣:\nدكتور قال للمريض: اسمع نبضك\nالمريض: وأنت اسمع كلامي!",
        ],
        "next": "after_joke"
    },
    "after_joke_react": {
        "triggers": ["هههه","😂","هاها","حلوة","مضحك","جيدة"],
        "context_required": "after_joke",
        "responses": ["يسعدني إنك ضحكت! 😄 تبي نكتة ثانية؟","الحمد لله! 😂 عندي المزيد لو تبي!"],
        "next": "idle"
    },
    "bot_name": {
        "triggers": ["اسمك","مين أنت","من أنت","شو اسمك"],
        "responses": ["أنا بوتك الذكي 🤖 صديقك الرقمي! وأنت يا {name}، كيف حالك؟"],
        "next": "waiting_how_are_you"
    },
    "compliment": {
        "triggers": ["ذكي","رائع","ممتاز","أحسن بوت","تحفة","حلو"],
        "responses": ["شكراً يا {name}! كلامك يسعدني 😄🌟","هذا من ذوقك! أنا بخدمتك دايماً 🤖💙"],
        "next": "idle"
    },
    "bored": {
        "triggers": ["زهقت","ملل","بوريد","فاضي","وين أروح"],
        "responses": ["إذا زهقت العب معي! 🎮 اكتب /games تشوف كل الألعاب 😄"],
        "next": "idle"
    },
}

# ─────────────────────────────────────────
# 👤 المستخدمون
# ─────────────────────────────────────────
def get_user(uid):
    if uid not in memory:
        memory[uid] = {
            "name": "صديقي", "messages": 0, "context": "idle",
            "xo_wins": 0, "xo_losses": 0, "xo_draws": 0,
            "rolls": [],
            "guess_points": 0, "guess_total": 0, "guess_correct": 0,
            "trivia_points": 0, "trivia_total": 0, "trivia_correct": 0,
            "capitals_points": 0, "capitals_total": 0, "capitals_correct": 0,
            "slot_points": 0, "slot_spins": 0,
            "hl_best": None,
        }
    return memory[uid]

# ─────────────────────────────────────────
# 🧠 محرك الحوار
# ─────────────────────────────────────────
def find_intent(text, user_context):
    tl = text.lower()
    for name, intent in CONVERSATION_TREE.items():
        req = intent.get("context_required")
        if req and req == user_context:
            if any(t in tl for t in intent["triggers"]):
                return name, intent
    for name, intent in CONVERSATION_TREE.items():
        if "context_required" not in intent:
            if any(t in tl for t in intent["triggers"]):
                return name, intent
    return None, None

def fmt(response, user):
    return response.replace("{name}", user["name"])

# ─────────────────────────────────────────
# 🎮 XO
# ─────────────────────────────────────────
WINS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def check_win(board, p):
    return any(board[a]==board[b]==board[c]==p for a,b,c in WINS)

def check_draw(board):
    return " " not in board

def minimax(board, is_bot, depth=0):
    if check_win(board,"⭕"): return 10-depth
    if check_win(board,"❌"): return depth-10
    if check_draw(board): return 0
    moves = [i for i in range(9) if board[i]==" "]
    if is_bot:
        best=-100
        for m in moves:
            board[m]="⭕"; best=max(best,minimax(board,False,depth+1)); board[m]=" "
        return best
    else:
        best=100
        for m in moves:
            board[m]="❌"; best=min(best,minimax(board,True,depth+1)); board[m]=" "
        return best

def best_bot_move(board):
    moves=[i for i in range(9) if board[i]==" "]
    if not moves: return None
    if random.random()<0.8:
        scores=[]
        for m in moves:
            board[m]="⭕"; scores.append(minimax(board,False)); board[m]=" "
        return moves[scores.index(max(scores))]
    return random.choice(moves)

def draw_board(uid):
    b=games_xo[uid]["board"]
    rows=[]
    for r in range(3):
        row=[]
        for c in range(3):
            i=r*3+c
            cell=b[i] if b[i]!=" " else "·"
            row.append(InlineKeyboardButton(cell,callback_data=f"x{i}"))
        rows.append(row)
    rows.append([
        InlineKeyboardButton("🔄 جولة جديدة",callback_data="xreset"),
        InlineKeyboardButton("📊 نتائجي",callback_data="xstats"),
    ])
    return InlineKeyboardMarkup(rows)

def xo_header(uid):
    u=get_user(uid)
    return (f"🎮 *XO — دورك يا {u['name']}*\n"
            f"انت ❌  |  البوت ⭕\n"
            f"🏆 {u['xo_wins']} فوز  |  💔 {u['xo_losses']} خسارة  |  🤝 {u['xo_draws']} تعادل")

# ─────────────────────────────────────────
# 🎲 النرد
# ─────────────────────────────────────────
def dice_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 ارمي!",callback_data="roll"),
         InlineKeyboardButton("🎲🎲 مزدوج",callback_data="roll2")],
        [InlineKeyboardButton("📊 إحصائياتي",callback_data="rollstats")]
    ])

# ─────────────────────────────────────────
# 🎯 Guess Dice
# ─────────────────────────────────────────
def guess_markup():
    r1=[InlineKeyboardButton(DICE_FACES[i],callback_data=f"guess{i+1}") for i in range(3)]
    r2=[InlineKeyboardButton(DICE_FACES[i],callback_data=f"guess{i+1}") for i in range(3,6)]
    return InlineKeyboardMarkup([r1,r2])

def leaderboard_guess():
    players=[(uid,d) for uid,d in memory.items() if d.get("guess_total",0)>0]
    if not players: return "🏆 *ما أحد لعب Guess Dice بعد!*"
    players.sort(key=lambda x:x[1]["guess_points"],reverse=True)
    medals=["🥇","🥈","🥉"]
    lines=["🏆 *Leaderboard — Guess Dice*\n"]
    for rank,(uid,d) in enumerate(players[:10]):
        medal=medals[rank] if rank<3 else f"{rank+1}."
        acc=round(d['guess_correct']/d['guess_total']*100) if d['guess_total'] else 0
        lines.append(f"{medal} *{d['name']}*\n   ⭐ {d['guess_points']} نقطة  |  🎯 {acc}%  |  🎲 {d['guess_total']} محاولة")
    return "\n".join(lines)

# ─────────────────────────────────────────
# 🔢 Higher or Lower
# ─────────────────────────────────────────
def hl_markup(attempts):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬆️ أعلى",callback_data="hl_high"),
         InlineKeyboardButton("⬇️ أقل",callback_data="hl_low")],
        [InlineKeyboardButton(f"🔄 محاولة جديدة (محاولات: {attempts})",callback_data="hl_reset")]
    ])

# ─────────────────────────────────────────
# 🌍 عواصم الدول
# ─────────────────────────────────────────
def start_capitals(uid):
    question = random.choice(CAPITALS)
    capitals_games[uid] = {"country": question[0], "answer": question[1], "active": True}

def capitals_markup(uid):
    correct = capitals_games[uid]["answer"]
    wrong_pool = [c[1] for c in CAPITALS if c[1] != correct]
    choices = random.sample(wrong_pool, 3) + [correct]
    random.shuffle(choices)
    capitals_games[uid]["choices"] = choices
    rows = []
    for i, c in enumerate(choices):
        rows.append([InlineKeyboardButton(c, callback_data=f"cap{i}")])
    return InlineKeyboardMarkup(rows)

def leaderboard_capitals():
    players=[(uid,d) for uid,d in memory.items() if d.get("capitals_total",0)>0]
    if not players: return "🏆 *ما أحد لعب عواصم الدول بعد!*"
    players.sort(key=lambda x:x[1]["capitals_points"],reverse=True)
    medals=["🥇","🥈","🥉"]
    lines=["🏆 *Leaderboard — عواصم الدول*\n"]
    for rank,(uid,d) in enumerate(players[:10]):
        medal=medals[rank] if rank<3 else f"{rank+1}."
        acc=round(d['capitals_correct']/d['capitals_total']*100) if d['capitals_total'] else 0
        lines.append(f"{medal} *{d['name']}*\n   ⭐ {d['capitals_points']} نقطة  |  🎯 {acc}%  |  🌍 {d['capitals_total']} سؤال")
    return "\n".join(lines)

# ─────────────────────────────────────────
# ❓ تريفيا
# ─────────────────────────────────────────
def start_trivia(uid):
    q = random.choice(TRIVIA)
    trivia_games[uid] = {"question": q, "active": True}

def check_answer(user_ans, correct_ans):
    u = user_ans.strip().lower().replace("ال", "", 1)
    c = correct_ans.strip().lower().replace("ال", "", 1)
    return u == c or u in c or c in u

def trivia_next_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ سؤال جديد", callback_data="triv_next"),
         InlineKeyboardButton("🏆 Leaderboard", callback_data="triv_board")]
    ])

def leaderboard_trivia():
    players=[(uid,d) for uid,d in memory.items() if d.get("trivia_total",0)>0]
    if not players: return "🏆 *ما أحد لعب تريفيا بعد!*"
    players.sort(key=lambda x:x[1]["trivia_points"],reverse=True)
    medals=["🥇","🥈","🥉"]
    lines=["🏆 *Leaderboard — تريفيا*\n"]
    for rank,(uid,d) in enumerate(players[:10]):
        medal=medals[rank] if rank<3 else f"{rank+1}."
        acc=round(d['trivia_correct']/d['trivia_total']*100) if d['trivia_total'] else 0
        lines.append(f"{medal} *{d['name']}*  —  ⭐ {d['trivia_points']} نقطة  |  🎯 {acc}%  |  ✅ {d['trivia_total']} سؤال")
    return "\n".join(lines)

# ─────────────────────────────────────────
# 🎰 سلوت مشين
# ─────────────────────────────────────────
def slot_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 ادور!", callback_data="slot_spin")],
        [InlineKeyboardButton("📊 نقاطي", callback_data="slot_stats")]
    ])

def spin_slot():
    return [random.choice(SLOT_SYMBOLS) for _ in range(3)]

def calc_slot_points(reels):
    if reels[0]==reels[1]==reels[2]:
        if reels[0]=="💎": return 50, "💎 جاكبوت! +50 نقطة 🎊"
        if reels[0]=="⭐": return 20, "⭐ ممتاز! +20 نقطة 🎉"
        return 10, f"3 متطابقين! +10 نقاط 🎉"
    if reels[0]==reels[1] or reels[1]==reels[2] or reels[0]==reels[2]:
        return 3, "زوج! +3 نقاط 👍"
    return 0, "حظاً أوفر المرة القادمة 😅"

# ─────────────────────────────────────────
# 📋 /start و /games
# ─────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_chat.id
    u = get_user(uid)
    await update.message.reply_text(
        f"أهلاً {u['name']}! 👋\n\nأحسنت الاختيار، لنبدأ الدردشة! 😄\n\n"
        f"كلمني بشكل طبيعي أو اكتب /games لتشوف الألعاب 🎮"
    )

async def games_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_chat.id
    u = get_user(uid)
    text = (
        f"🎮 *قائمة الألعاب — أهلاً {u['name']}!*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❌⭕ *XO*\nالعب ضد البوت الذكي\n📝 اكتب: `xo`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎲 *النرد*\nارمي نرد عادي أو مزدوج\n📝 اكتب: `نرد`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 *Guess Dice*\nخمّن رقم النرد واجمع النقاط\n📝 اكتب: `guess`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔢 *Higher or Lower*\nخمّن رقم من 1-100\n📝 اكتب: `higher`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌍 *عواصم الدول*\nاختر عاصمة الدولة الصحيحة\n📝 اكتب: `عواصم`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❓ *تريفيا*\nأسئلة ثقافية واكتب الجواب\n📝 اكتب: `تريفيا`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎰 *سلوت مشين*\nدوّر 3 رموز وحاول تطابقها\n📝 اكتب: `سلوت`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏆 *Leaderboards:*\n"
        "`leaderboard guess` — Guess Dice\n"
        "`leaderboard عواصم` — عواصم الدول\n"
        "`leaderboard تريفيا` — تريفيا\n"
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌⭕ XO", callback_data="menu_xo"),
         InlineKeyboardButton("🎲 نرد", callback_data="menu_dice")],
        [InlineKeyboardButton("🎯 Guess Dice", callback_data="menu_guess"),
         InlineKeyboardButton("🔢 Higher/Lower", callback_data="menu_hl")],
        [InlineKeyboardButton("🌍 عواصم", callback_data="menu_cap"),
         InlineKeyboardButton("❓ تريفيا", callback_data="menu_trivia")],
        [InlineKeyboardButton("🎰 سلوت", callback_data="menu_slot")],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.message.chat_id
    u = get_user(uid)
    if q.data == "menu_xo":
        games_xo[uid] = {"board":[" "]*9,"active":True}
        await q.message.reply_text(xo_header(uid), parse_mode="Markdown", reply_markup=draw_board(uid))
    elif q.data == "menu_dice":
        await q.message.reply_text(f"🎲 *لعبة النرد*\nاضغط الزر يا {u['name']}!", parse_mode="Markdown", reply_markup=dice_markup())
    elif q.data == "menu_guess":
        secret=random.randint(1,6); guess_games[uid]=secret
        await q.message.reply_text(f"🎯 *Guess Dice!*\nخمّن رقم النرد!\n⭐ نقاطك: *{u['guess_points']}*", parse_mode="Markdown", reply_markup=guess_markup())
    elif q.data == "menu_hl":
        n=random.randint(1,100); higher_lower_games[uid]={"number":n,"attempts":0,"active":True,"last_guess":None}
        await q.message.reply_text(f"🔢 *Higher or Lower!*\nفكّرت برقم من 1 إلى 100...\nشو تخمّن؟", parse_mode="Markdown", reply_markup=hl_markup(0))
    elif q.data == "menu_cap":
        start_capitals(uid)
        country=capitals_games[uid]["country"]; mk=capitals_markup(uid)
        await q.message.reply_text(f"🌍 *عواصم الدول*\n\nما هي عاصمة *{country}*؟", parse_mode="Markdown", reply_markup=mk)
    elif q.data == "menu_trivia":
        start_trivia(uid)
        q_data=trivia_games[uid]["question"]
        trivia_waiting[uid] = q_data
        await q.message.reply_text(f"❓ *تريفيا*\n\n{q_data['q']}\n\n✏️ اكتب جوابك!", parse_mode="Markdown")
    elif q.data == "menu_slot":
        await q.message.reply_text(f"🎰 *سلوت مشين*\nنقاطك: *{u['slot_points']}* ⭐\nادور وحاول تطابق الرموز!", parse_mode="Markdown", reply_markup=slot_markup())

# ─────────────────────────────────────────
# 📩 معالجة الرسائل
# ─────────────────────────────────────────
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.message.chat_id
    u = get_user(uid)
    u["messages"] += 1
    tl = text.lower()

    if "اسمي" in tl:
        name=text.replace("اسمي","").strip()
        if name:
            u["name"]=name
            await update.message.reply_text(f"تشرفت يا {name}! 🤝 كيف حالك؟")
            u["context"]="waiting_how_are_you"
            return

    # ✏️ إجابة تريفيا مكتوبة
    if uid in trivia_waiting:
        game = trivia_waiting[uid]
        if check_answer(text, game["a"]):
            trivia_waiting.pop(uid)
            u["trivia_total"] += 1
            u["trivia_correct"] += 1
            u["trivia_points"] += 5
            await update.message.reply_text(
                f"✅ *إجابة صحيحة! ذكي! 🧠*\n\n⭐ +5 نقاط | مجموعك: *{u['trivia_points']} نقطة*",
                parse_mode="Markdown", reply_markup=trivia_next_markup()
            )
        else:
            msg = await update.message.reply_text("❌ غلط! حاول مرة ثانية 😅")
            await asyncio.sleep(2)
            await msg.delete()
            await update.message.delete()
        return

    if any(w in tl for w in ["xo","إكس أو","اكس او"]):
        games_xo[uid]={"board":[" "]*9,"active":True}
        await update.message.reply_text(xo_header(uid),parse_mode="Markdown",reply_markup=draw_board(uid))
        return

    if any(w in tl for w in ["نرد","dice","زهر"]) and "guess" not in tl:
        await update.message.reply_text(f"🎲 *لعبة النرد*\nاضغط الزر يا {u['name']}!",parse_mode="Markdown",reply_markup=dice_markup())
        return

    if any(w in tl for w in ["guess","خمن","تخمين"]):
        secret=random.randint(1,6); guess_games[uid]=secret
        await update.message.reply_text(f"🎯 *Guess Dice!*\nخمّن رقم النرد! 🎲\n⭐ نقاطك: *{u['guess_points']}*",parse_mode="Markdown",reply_markup=guess_markup())
        return

    if any(w in tl for w in ["higher","هاير","أعلى أو أقل"]):
        n=random.randint(1,100)
        higher_lower_games[uid]={"number":n,"attempts":0,"active":True,"last_guess":None}
        await update.message.reply_text(f"🔢 *Higher or Lower!*\nفكّرت برقم من 1 إلى 100\nشو تخمّن؟",parse_mode="Markdown",reply_markup=hl_markup(0))
        return

    if any(w in tl for w in ["عواصم","عاصمة","capitals"]):
        start_capitals(uid)
        country=capitals_games[uid]["country"]; mk=capitals_markup(uid)
        await update.message.reply_text(f"🌍 *عواصم الدول*\n\nما هي عاصمة *{country}*؟",parse_mode="Markdown",reply_markup=mk)
        return

    if any(w in tl for w in ["تريفيا","trivia","سؤال ثقافي"]):
        start_trivia(uid)
        q_data=trivia_games[uid]["question"]
        trivia_waiting[uid] = q_data
        await update.message.reply_text(f"❓ *تريفيا*\n\n{q_data['q']}\n\n✏️ اكتب جوابك!",parse_mode="Markdown")
        return

    if any(w in tl for w in ["سلوت","slot","سلوت مشين"]):
        await update.message.reply_text(f"🎰 *سلوت مشين*\nنقاطك: *{u['slot_points']}* ⭐\nادور وحاول تطابق الرموز!",parse_mode="Markdown",reply_markup=slot_markup())
        return

    if "leaderboard" in tl or "ليدربورد" in tl or "ترتيب" in tl:
        if "عواصم" in tl: await update.message.reply_text(leaderboard_capitals(),parse_mode="Markdown")
        elif "تريفيا" in tl: await update.message.reply_text(leaderboard_trivia(),parse_mode="Markdown")
        else: await update.message.reply_text(leaderboard_guess(),parse_mode="Markdown")
        return

    if any(w in tl for w in ["مساعدة","help","قائمة","أوامر"]):
        await update.message.reply_text("📋 اكتب /games لتشوف كل الألعاب! 🎮",parse_mode="Markdown")
        return

    intent_name, intent = find_intent(text, u["context"])
    if intent:
        response=random.choice(intent["responses"])
        u["context"]=intent.get("next","idle")
        await asyncio.sleep(random.uniform(0.6,1.3))
        await update.message.reply_text(fmt(response,u))
    else:
        ctx=u["context"]
        if ctx=="waiting_how_are_you":
            await update.message.reply_text(f"ما فهمت يا {u['name']} 😅 قلي كيف حالك؟")
        elif ctx=="waiting_problem":
            await update.message.reply_text(f"أنا أسمعك يا {u['name']}... كمّل كلامك 🤍")
        elif ctx=="after_joke":
            await update.message.reply_text("عجبتك؟ 😄 قلي تبي نكتة ثانية؟")
        else:
            u["context"]="idle"
            fallback=[f"ما فهمت كثير يا {u['name']} 😅 وضّح أكثر؟",f"كمّل كلامك، أنا أسمعك 👀",f"هممم... 🤔 قصدك إيش بالضبط؟"]
            await asyncio.sleep(random.uniform(0.5,1.0))
            await update.message.reply_text(random.choice(fallback))

# ─────────────────────────────────────────
# 🎮 XO Callback
# ─────────────────────────────────────────
async def xo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; uid=q.message.chat_id; u=get_user(uid)
    if q.data=="xstats":
        total=u["xo_wins"]+u["xo_losses"]+u["xo_draws"]
        rate=round(u["xo_wins"]/total*100) if total else 0
        await q.answer(f"🏆 فوز: {u['xo_wins']}\n💔 خسارة: {u['xo_losses']}\n🤝 تعادل: {u['xo_draws']}\n🎯 نسبة الفوز: {rate}%",show_alert=True)
        return
    await q.answer()
    if q.data=="xreset":
        games_xo[uid]={"board":[" "]*9,"active":True}
        await q.message.edit_text(xo_header(uid),parse_mode="Markdown",reply_markup=draw_board(uid)); return
    if uid not in games_xo: games_xo[uid]={"board":[" "]*9,"active":True}
    game=games_xo[uid]; b=game["board"]
    if not game["active"]: return
    i=int(q.data[1:])
    if b[i]!=" ": return
    b[i]="❌"
    if check_win(b,"❌"):
        u["xo_wins"]+=1; game["active"]=False
        await q.message.edit_text(f"🎉 *فزت! مبروك يا {u['name']}!* 🏆\n{xo_header(uid)}",parse_mode="Markdown",reply_markup=draw_board(uid)); return
    if check_draw(b):
        u["xo_draws"]+=1; game["active"]=False
        await q.message.edit_text(f"🤝 *تعادل!*\n{xo_header(uid)}",parse_mode="Markdown",reply_markup=draw_board(uid)); return
    await q.message.edit_text("🤖 *أفكر...*",parse_mode="Markdown",reply_markup=draw_board(uid))
    await asyncio.sleep(1.0)
    move=best_bot_move(b)
    if move is not None: b[move]="⭕"
    if check_win(b,"⭕"):
        u["xo_losses"]+=1; game["active"]=False
        await q.message.edit_text(f"😄 *أنا فزت هذه المرة!*\n{xo_header(uid)}",parse_mode="Markdown",reply_markup=draw_board(uid)); return
    if check_draw(b):
        u["xo_draws"]+=1; game["active"]=False
        await q.message.edit_text(f"🤝 *تعادل!*\n{xo_header(uid)}",parse_mode="Markdown",reply_markup=draw_board(uid)); return
    await q.message.edit_text(xo_header(uid),parse_mode="Markdown",reply_markup=draw_board(uid))

# ─────────────────────────────────────────
# 🎲 Dice Callback
# ─────────────────────────────────────────
async def dice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; uid=q.message.chat_id; u=get_user(uid)
    if q.data=="rollstats":
        rolls=u.get("rolls",[])
        if not rolls: await q.answer("ما رميت النرد بعد! 🎲",show_alert=True); return
        await q.answer(f"📊 عدد الرميات: {len(rolls)}\n🎯 المعدل: {round(sum(rolls)/len(rolls),2)}\n⬆️ أعلى: {max(rolls)}  |  ⬇️ أدنى: {min(rolls)}",show_alert=True); return
    await q.answer("🎲 جاري الرمي...")
    await asyncio.sleep(0.5)
    if q.data=="roll":
        r=random.randint(1,6); u.setdefault("rolls",[]).append(r)
        comments=["حظ مقبول!","مو بطال!","ممتاز! 🎉","يا سلام!","عادي...","🔥 رائع!"]
        await q.message.edit_text(f"🎲 *رميت النرد!*\n\n{DICE_FACES[r-1]}  —  الرقم: *{r}*\n_{random.choice(comments)}_",parse_mode="Markdown",reply_markup=dice_markup())
    elif q.data=="roll2":
        r1,r2=random.randint(1,6),random.randint(1,6); u.setdefault("rolls",[]).extend([r1,r2])
        total=r1+r2; comment="🎊 جوهرة!" if total==12 else ("💥 مزدوج!" if r1==r2 else "جرب حظك!")
        await q.message.edit_text(f"🎲🎲 *نرد مزدوج!*\n\n{DICE_FACES[r1-1]} + {DICE_FACES[r2-1]} = *{total}*\n_{comment}_",parse_mode="Markdown",reply_markup=dice_markup())

# ─────────────────────────────────────────
# 🎯 Guess Dice Callback
# ─────────────────────────────────────────
async def guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=q.message.chat_id; u=get_user(uid)
    if uid not in guess_games: await q.answer("اكتب guess لتبدأ!",show_alert=True); return
    secret=guess_games.pop(uid); guess=int(q.data.replace("guess","")); u["guess_total"]+=1
    mk=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 جولة جديدة",callback_data="guessnew"),InlineKeyboardButton("🏆 Leaderboard",callback_data="guessboard")]])
    if guess==secret:
        u["guess_correct"]+=1; u["guess_points"]+=3
        await q.message.edit_text(f"🎉 *صح! يا ذكي!*\n\nالنرد كان {DICE_FACES[secret-1]} = *{secret}*\n\n⭐ +3 نقاط | مجموعك: *{u['guess_points']} نقطة*",parse_mode="Markdown",reply_markup=mk)
    else:
        u["guess_points"]=max(0,u["guess_points"]-1)
        await q.message.edit_text(f"❌ *غلط!*\n\nاخترت {DICE_FACES[guess-1]} بس النرد كان {DICE_FACES[secret-1]} = *{secret}*\n\n💔 -1 نقطة | مجموعك: *{u['guess_points']} نقطة*",parse_mode="Markdown",reply_markup=mk)

async def guess_nav_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=q.message.chat_id; u=get_user(uid)
    if q.data=="guessnew":
        secret=random.randint(1,6); guess_games[uid]=secret
        await q.message.edit_text(f"🎯 *Guess Dice!*\nخمّن رقم النرد! 🎲\n⭐ نقاطك: *{u['guess_points']}*",parse_mode="Markdown",reply_markup=guess_markup())
    elif q.data=="guessboard":
        await q.message.edit_text(leaderboard_guess(),parse_mode="Markdown",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 العب مجدداً",callback_data="guessnew")]]))

# ─────────────────────────────────────────
# 🔢 Higher or Lower Callback
# ─────────────────────────────────────────
async def hl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=q.message.chat_id; u=get_user(uid)
    if q.data=="hl_reset":
        n=random.randint(1,100); higher_lower_games[uid]={"number":n,"attempts":0,"active":True,"last_guess":50}
        await q.message.edit_text(f"🔢 *Higher or Lower!*\nفكّرت برقم جديد من 1 إلى 100\nشو تخمّن؟",parse_mode="Markdown",reply_markup=hl_markup(0)); return
    if uid not in higher_lower_games: return
    game=higher_lower_games[uid]
    if not game["active"]: return
    game["attempts"]+=1
    last=game.get("last_guess",50)
    if q.data=="hl_high":
        new_guess=min(100,last+max(1,random.randint(3,15))); direction="أعلى ⬆️"
    else:
        new_guess=max(1,last-max(1,random.randint(3,15))); direction="أقل ⬇️"
    game["last_guess"]=new_guess
    number=game["number"]
    if new_guess==number:
        game["active"]=False
        best=u.get("hl_best")
        if best is None or game["attempts"]<best: u["hl_best"]=game["attempts"]
        await q.message.edit_text(f"🎉 *صح! الرقم كان {number}!*\n\nوصلتله في *{game['attempts']} محاولة*\n🏆 أفضل سجل: *{u['hl_best']} محاولة*",parse_mode="Markdown",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 جولة جديدة",callback_data="hl_reset")]]))
    elif new_guess<number:
        await q.message.edit_text(f"🔢 *Higher or Lower*\nخمّنت {direction} وصلت لـ *{new_guess}*\nالرقم أعلى من هذا! ⬆️\nمحاولات: *{game['attempts']}*",parse_mode="Markdown",reply_markup=hl_markup(game["attempts"]))
    else:
        await q.message.edit_text(f"🔢 *Higher or Lower*\nخمّنت {direction} وصلت لـ *{new_guess}*\nالرقم أقل من هذا! ⬇️\nمحاولات: *{game['attempts']}*",parse_mode="Markdown",reply_markup=hl_markup(game["attempts"]))

# ─────────────────────────────────────────
# 🌍 عواصم Callback
# ─────────────────────────────────────────
async def capitals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=q.message.chat_id; u=get_user(uid)
    if uid not in capitals_games: return
    game=capitals_games[uid]
    if not game.get("active"): return
    chosen_idx=int(q.data.replace("cap",""))
    chosen=game["choices"][chosen_idx]; correct=game["answer"]
    game["active"]=False; u["capitals_total"]+=1
    next_mk=InlineKeyboardMarkup([[InlineKeyboardButton("🌍 سؤال جديد",callback_data="cap_next"),InlineKeyboardButton("🏆 Leaderboard",callback_data="cap_board")]])
    if chosen==correct:
        u["capitals_correct"]+=1; u["capitals_points"]+=3
        await q.message.edit_text(f"✅ *صح! مبروك!*\nعاصمة *{game['country']}* هي *{correct}* 🌍\n\n⭐ +3 نقاط | مجموعك: *{u['capitals_points']} نقطة*",parse_mode="Markdown",reply_markup=next_mk)
    else:
        u["capitals_points"]=max(0,u["capitals_points"]-1)
        await q.message.edit_text(f"❌ *غلط!*\nاخترت *{chosen}* بس عاصمة *{game['country']}* هي *{correct}* 🌍\n\n💔 -1 نقطة | مجموعك: *{u['capitals_points']} نقطة*",parse_mode="Markdown",reply_markup=next_mk)

async def capitals_nav_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=q.message.chat_id; u=get_user(uid)
    if q.data=="cap_next":
        start_capitals(uid); country=capitals_games[uid]["country"]; mk=capitals_markup(uid)
        await q.message.edit_text(f"🌍 *عواصم الدول*\n\nما هي عاصمة *{country}*؟",parse_mode="Markdown",reply_markup=mk)
    elif q.data=="cap_board":
        await q.message.edit_text(leaderboard_capitals(),parse_mode="Markdown",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌍 سؤال جديد",callback_data="cap_next")]]))

# ─────────────────────────────────────────
# ❓ تريفيا Callback
# ─────────────────────────────────────────
async def trivia_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # هذي الدالة ما تُستخدم لأن التريفيا الجديدة بالكتابة
    # بس نتركها لتجنب الأخطاء
    q=update.callback_query; await q.answer()

async def trivia_nav_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=q.message.chat_id; u=get_user(uid)
    if q.data=="triv_next":
        start_trivia(uid)
        q_data=trivia_games[uid]["question"]
        trivia_waiting[uid] = q_data
        await q.message.edit_text(f"❓ *تريفيا*\n\n{q_data['q']}\n\n✏️ اكتب جوابك!",parse_mode="Markdown")
    elif q.data=="triv_board":
        await q.message.edit_text(leaderboard_trivia(),parse_mode="Markdown",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❓ سؤال جديد",callback_data="triv_next")]]))

# ─────────────────────────────────────────
# 🎰 سلوت Callback
# ─────────────────────────────────────────
async def slot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; uid=q.message.chat_id; u=get_user(uid)
    if q.data=="slot_stats":
        await q.answer(f"🎰 عدد الدورات: {u['slot_spins']}\n⭐ نقاطك: {u['slot_points']}",show_alert=True); return
    await q.answer("🎰 جاري الدوران...")
    await asyncio.sleep(0.8)
    reels=spin_slot(); u["slot_spins"]+=1
    pts,comment=calc_slot_points(reels); u["slot_points"]+=pts
    display=" | ".join(reels)
    await q.message.edit_text(f"🎰 *سلوت مشين*\n\n{display}\n\n_{comment}_\n\n⭐ نقاطك: *{u['slot_points']}*",parse_mode="Markdown",reply_markup=slot_markup())

# ─────────────────────────────────────────
# 🚀 تشغيل البوت
# ─────────────────────────────────────────
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("games", games_command))
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
app.add_handler(CallbackQueryHandler(menu_handler,        pattern="^menu_"))
app.add_handler(CallbackQueryHandler(xo_handler,          pattern="^x"))
app.add_handler(CallbackQueryHandler(dice_handler,        pattern="^roll"))
app.add_handler(CallbackQueryHandler(guess_handler,       pattern="^guess[1-6]$"))
app.add_handler(CallbackQueryHandler(guess_nav_handler,   pattern="^guess(new|board)$"))
app.add_handler(CallbackQueryHandler(hl_handler,          pattern="^hl_"))
app.add_handler(CallbackQueryHandler(capitals_handler,    pattern="^cap[0-9]$"))
app.add_handler(CallbackQueryHandler(capitals_nav_handler,pattern="^cap_"))
app.add_handler(CallbackQueryHandler(trivia_handler,      pattern="^triv[0-9]$"))
app.add_handler(CallbackQueryHandler(trivia_nav_handler,  pattern="^triv_"))
app.add_handler(CallbackQueryHandler(slot_handler,        pattern="^slot_"))

print("Bot is running 🤖")

try:
    app.run_polling()
except Exception as e:
    print("❌ في خطأ:", e)
    input("اضغط Enter للخروج...")