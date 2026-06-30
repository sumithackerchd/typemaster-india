"""Paragraph Database seeder for TypeMaster India.

Generates and stores typing content:
    * 100 English paragraphs
    * 100 Hindi (Mangal) paragraphs
    * 100 English random-word sets
    * 100 Hindi random-word sets

The database is the primary source of truth. A JSON mirror is written to
``static/data/`` so the typing engine keeps working even if the database is
unavailable (JSON fallback).
"""

import json
import os
import random

from models import db
from models.paragraph import Paragraph
from utils.mock_constants import CATEGORY_KIND


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "static", "data")

SEED_JSON = os.path.join(DATA_DIR, "seed_paragraphs.json")
ENGLISH_JSON = os.path.join(DATA_DIR, "paragraphs.json")
HINDI_JSON = os.path.join(DATA_DIR, "hindi_mangal.json")

PARAGRAPH_CATEGORIES = [
    "random_paragraph",
    "ssc",
    "railway",
    "up_police",
    "cpct",
    "government",
    "programming",
    "general_knowledge",
    "typing_practice",
]

DIFFICULTIES = ["easy", "medium", "hard"]

# Sentences per difficulty bucket
SENTENCES_PER_DIFFICULTY = {"easy": (1, 2), "medium": (3, 4), "hard": (5, 6)}

# Word count per difficulty for random-word sets
WORDS_PER_DIFFICULTY = {"easy": 20, "medium": 35, "hard": 50}


# ---------------------------------------------------------------------------
# English sentence banks
# ---------------------------------------------------------------------------

EN_SENTENCES = {
    "random_paragraph": [
        "The quick brown fox jumps over the lazy dog every single morning.",
        "Reading good books expands the mind and improves our vocabulary.",
        "A calm river flows gently through the green and peaceful valley.",
        "Hard work and patience always lead to lasting success in life.",
        "The sun rises in the east and paints the sky with warm colours.",
        "Friendship is a treasure that grows stronger with honest care.",
        "Travelling to new places teaches us about different cultures.",
        "Music has the power to heal the heart and lift the spirit.",
        "A healthy mind lives best inside a healthy and active body.",
        "Small daily habits build the foundation of a great future.",
        "Kindness costs nothing yet it is worth more than gold.",
        "The garden was full of bright flowers and busy honey bees.",
    ],
    "ssc": [
        "The Staff Selection Commission conducts exams for various government posts.",
        "Candidates must prepare general awareness, reasoning and quantitative aptitude.",
        "Time management is the key to clearing the SSC tier examinations.",
        "Regular revision of static general knowledge improves the final score.",
        "The combined graduate level exam attracts lakhs of aspirants each year.",
        "Accuracy in the data interpretation section can boost the overall rank.",
        "A balanced study plan covers English comprehension and grammar daily.",
        "Mock tests help aspirants understand the real exam pattern clearly.",
        "Current affairs of the last six months are very important for the test.",
        "Speed and precision in typing matter for the skill test stage.",
    ],
    "railway": [
        "The Indian Railways is one of the largest rail networks in the world.",
        "Railway recruitment boards conduct exams for technical and clerical posts.",
        "Punctuality and discipline are essential values for railway employees.",
        "The general science section tests basic physics, chemistry and biology.",
        "Aspirants should practise reasoning puzzles to improve their speed.",
        "Safety of passengers is the highest priority of every railway worker.",
        "The exam includes mathematics, general intelligence and awareness.",
        "Trains connect distant cities and carry millions of people each day.",
        "A station master coordinates the safe arrival and departure of trains.",
        "Consistent practice of arithmetic builds confidence for the exam.",
    ],
    "up_police": [
        "The state police force maintains law and order across the region.",
        "Physical fitness and mental alertness are vital for police duty.",
        "Constable recruitment includes a written test and a physical exam.",
        "Reasoning ability helps an officer make quick and fair decisions.",
        "Respect for citizens and the rule of law guides honest policing.",
        "The written exam covers general knowledge, reasoning and numerical ability.",
        "Discipline and courage define the character of a true police officer.",
        "Aspirants must stay updated with current legal and social affairs.",
        "Patrolling the streets keeps neighbourhoods safe during the night.",
        "Integrity is the most important quality expected from every recruit.",
    ],
    "cpct": [
        "The computer proficiency certification test checks basic typing speed.",
        "Candidates must type accurately in both English and Hindi languages.",
        "Knowledge of operating systems and office tools is tested in the exam.",
        "A good typing rhythm reduces errors and increases the net speed.",
        "The objective section covers computer fundamentals and the internet.",
        "Daily typing drills build muscle memory for faster keyboard control.",
        "Understanding email, spreadsheets and word processors is essential.",
        "The certificate is valid for many state government job applications.",
        "Maintaining posture and finger placement improves long typing sessions.",
        "Practising on the standard layout prepares you for the real test.",
    ],
    "government": [
        "Government examinations open the door to stable and respected careers.",
        "A disciplined routine and steady focus are the secrets of toppers.",
        "Public service demands honesty, dedication and a spirit of duty.",
        "Aspirants should read the newspaper daily to track current affairs.",
        "Clearing the preliminary stage requires strong conceptual clarity.",
        "Writing practice improves the quality of descriptive answer papers.",
        "Civil servants work to deliver welfare schemes to ordinary citizens.",
        "Patience and persistence carry candidates through years of preparation.",
        "A clear understanding of the constitution helps in the polity section.",
        "Setting weekly targets keeps the long preparation journey on track.",
    ],
    "programming": [
        "A function should do one thing and do that one thing very well.",
        "Clean code reads like well written prose for the next developer.",
        "Variables must have clear names that describe their real purpose.",
        "Testing early and often prevents small bugs from becoming disasters.",
        "Loops and conditions form the backbone of everyday programming logic.",
        "Version control lets a team collaborate without overwriting work.",
        "An algorithm is simply a clear sequence of well defined steps.",
        "Comments should explain why the code exists, not what it does.",
        "Breaking a big problem into small functions makes it easier to solve.",
        "Reading other people's code is one of the fastest ways to learn.",
    ],
    "general_knowledge": [
        "Mount Everest is the highest mountain above sea level on the earth.",
        "The human body has two hundred and six bones in adulthood.",
        "Water covers nearly seventy percent of the surface of our planet.",
        "The Great Wall of China stretches across thousands of kilometres.",
        "Photosynthesis allows green plants to make their own food from light.",
        "The currency of Japan is the yen and its capital is Tokyo.",
        "Sound travels faster through water than it does through the air.",
        "The Sahara is the largest hot desert found anywhere in the world.",
        "Diamond is the hardest naturally occurring material known to science.",
        "The heart pumps blood through a vast network of veins and arteries.",
    ],
    "typing_practice": [
        "Place your fingers on the home row and keep your wrists relaxed.",
        "Look at the screen and trust your fingers to find the right keys.",
        "Slow and steady practice builds accuracy before raw typing speed.",
        "Take a short break every twenty minutes to rest your tired eyes.",
        "Aim for smooth and even keystrokes instead of sudden quick bursts.",
        "Correct posture protects your back during long typing sessions.",
        "Practising the same drill daily turns effort into easy habit.",
        "Focus on the words ahead and let a steady rhythm guide you.",
        "Accuracy first and speed will follow naturally with patience.",
        "Warm up your hands gently before starting a long typing test.",
    ],
}

EN_WORDS = (
    "time year people way day man thing woman life child world school state "
    "family student group country problem hand part place case week company "
    "system program question work government number night point home water "
    "room mother area money story fact month lot right study book eye job "
    "word business issue side kind head house service friend father power hour "
    "game line end member law car city community name president team minute "
    "idea body information back parent face others level office door health "
    "person art war history party result change morning reason research girl "
    "guy moment air teacher force education value paper light table music road "
    "river garden market window letter ground future season nature future "
    "honest brave bright simple strong gentle quiet happy clever modern global"
).split()


# ---------------------------------------------------------------------------
# Hindi (Mangal) sentence banks
# ---------------------------------------------------------------------------

HI_SENTENCES = {
    "random_paragraph": [
        "सूरज पूर्व दिशा में उगता है और आकाश को सुनहरा बना देता है।",
        "अच्छी पुस्तकें पढ़ने से ज्ञान और शब्दावली दोनों बढ़ती है।",
        "कड़ी मेहनत और धैर्य से जीवन में सफलता अवश्य मिलती है।",
        "मित्रता एक अनमोल खजाना है जो सच्ची देखभाल से मजबूत होता है।",
        "स्वस्थ शरीर में ही स्वस्थ मन निवास करता है यह सत्य है।",
        "नदी का शांत जल हरी भरी घाटी से धीरे धीरे बहता है।",
        "छोटी छोटी अच्छी आदतें उज्ज्वल भविष्य की नींव रखती हैं।",
        "संगीत में मन को शांत करने और आत्मा को ऊपर उठाने की शक्ति है।",
        "नई जगहों की यात्रा हमें विभिन्न संस्कृतियों का परिचय देती है।",
        "दया करने में कुछ खर्च नहीं होता पर यह सोने से भी मूल्यवान है।",
        "बगीचा रंग बिरंगे फूलों और मेहनती मधुमक्खियों से भरा हुआ था।",
        "प्रतिदिन का अभ्यास परिश्रम को सहज आदत में बदल देता है।",
    ],
    "ssc": [
        "कर्मचारी चयन आयोग विभिन्न सरकारी पदों के लिए परीक्षा आयोजित करता है।",
        "उम्मीदवारों को सामान्य ज्ञान तर्कशक्ति और गणित की तैयारी करनी चाहिए।",
        "समय प्रबंधन परीक्षा को सफलतापूर्वक पास करने की कुंजी है।",
        "स्थैतिक सामान्य ज्ञान का नियमित दोहराव अंतिम अंक सुधारता है।",
        "मॉक टेस्ट से अभ्यर्थी को वास्तविक परीक्षा का स्वरूप समझ आता है।",
        "पिछले छह महीनों की समसामयिकी परीक्षा के लिए बहुत महत्वपूर्ण है।",
        "संतुलित अध्ययन योजना प्रतिदिन अंग्रेजी और व्याकरण को शामिल करती है।",
        "आंकड़ों के विश्लेषण में शुद्धता समग्र रैंक को ऊपर ले जाती है।",
        "गति और सटीकता कौशल परीक्षा चरण के लिए अत्यंत आवश्यक हैं।",
        "लाखों अभ्यर्थी हर वर्ष इस परीक्षा में बैठते हैं।",
    ],
    "railway": [
        "भारतीय रेल विश्व के सबसे बड़े रेल नेटवर्क में से एक है।",
        "रेलवे भर्ती बोर्ड तकनीकी और लिपिक पदों के लिए परीक्षा लेता है।",
        "समय की पाबंदी और अनुशासन रेलवे कर्मचारी के मुख्य गुण हैं।",
        "सामान्य विज्ञान खंड भौतिकी रसायन और जीव विज्ञान का परीक्षण करता है।",
        "यात्रियों की सुरक्षा हर रेल कर्मचारी की सर्वोच्च प्राथमिकता है।",
        "तर्क संबंधी पहेलियों का अभ्यास गति बढ़ाने में सहायक होता है।",
        "रेलगाड़ियाँ दूर के शहरों को जोड़ती और लाखों लोगों को ले जाती हैं।",
        "अंकगणित का निरंतर अभ्यास परीक्षा के लिए आत्मविश्वास बढ़ाता है।",
        "स्टेशन मास्टर गाड़ियों के सुरक्षित आगमन और प्रस्थान का संचालन करता है।",
        "परीक्षा में गणित सामान्य बुद्धि और जागरूकता शामिल होती है।",
    ],
    "up_police": [
        "पुलिस बल क्षेत्र में कानून और व्यवस्था बनाए रखता है।",
        "शारीरिक फिटनेस और मानसिक सतर्कता पुलिस ड्यूटी के लिए आवश्यक है।",
        "आरक्षी भर्ती में लिखित परीक्षा और शारीरिक परीक्षण शामिल होता है।",
        "तर्क शक्ति अधिकारी को त्वरित और निष्पक्ष निर्णय लेने में मदद करती है।",
        "नागरिकों का सम्मान और कानून का पालन ईमानदार पुलिसिंग का आधार है।",
        "अनुशासन और साहस सच्चे पुलिस अधिकारी के चरित्र को परिभाषित करते हैं।",
        "लिखित परीक्षा सामान्य ज्ञान तर्क और संख्यात्मक योग्यता पर आधारित है।",
        "अभ्यर्थियों को वर्तमान कानूनी और सामाजिक घटनाओं से अवगत रहना चाहिए।",
        "रात में गश्त लगाना मोहल्लों को सुरक्षित बनाए रखता है।",
        "ईमानदारी हर भर्ती से अपेक्षित सबसे महत्वपूर्ण गुण है।",
    ],
    "cpct": [
        "कंप्यूटर दक्षता प्रमाणन परीक्षा बुनियादी टाइपिंग गति की जाँच करती है।",
        "उम्मीदवारों को अंग्रेजी और हिंदी दोनों में सटीक टाइप करना आवश्यक है।",
        "ऑपरेटिंग सिस्टम और कार्यालय उपकरणों का ज्ञान परीक्षा में आता है।",
        "अच्छी टाइपिंग लय त्रुटियों को घटाती और शुद्ध गति को बढ़ाती है।",
        "वस्तुनिष्ठ खंड कंप्यूटर की मूल बातें और इंटरनेट को शामिल करता है।",
        "प्रतिदिन का टाइपिंग अभ्यास कीबोर्ड नियंत्रण के लिए स्मृति बनाता है।",
        "ईमेल स्प्रेडशीट और वर्ड प्रोसेसर की समझ बहुत आवश्यक है।",
        "यह प्रमाणपत्र कई राज्य सरकारी नौकरियों के लिए मान्य होता है।",
        "सही मुद्रा और अंगुलियों की स्थिति लंबे सत्र को सरल बनाती है।",
        "मानक लेआउट पर अभ्यास आपको वास्तविक परीक्षा के लिए तैयार करता है।",
    ],
    "government": [
        "सरकारी परीक्षाएँ स्थिर और सम्मानित करियर का द्वार खोलती हैं।",
        "अनुशासित दिनचर्या और निरंतर ध्यान ही श्रेष्ठ अभ्यर्थी का रहस्य है।",
        "लोक सेवा ईमानदारी समर्पण और कर्तव्य की भावना की माँग करती है।",
        "अभ्यर्थियों को समसामयिकी जानने के लिए प्रतिदिन समाचार पढ़ना चाहिए।",
        "प्रारंभिक चरण को पास करने के लिए मजबूत वैचारिक स्पष्टता आवश्यक है।",
        "लेखन अभ्यास वर्णनात्मक उत्तर पत्रों की गुणवत्ता को सुधारता है।",
        "लोक सेवक आम नागरिकों तक कल्याणकारी योजनाएँ पहुँचाते हैं।",
        "धैर्य और दृढ़ता अभ्यर्थियों को वर्षों की तैयारी से पार ले जाती है।",
        "संविधान की स्पष्ट समझ राजव्यवस्था खंड में सहायता करती है।",
        "साप्ताहिक लक्ष्य निर्धारित करना लंबी तैयारी को सही दिशा में रखता है।",
    ],
    "programming": [
        "एक फलन को केवल एक ही कार्य करना चाहिए और वह भी बहुत अच्छे से।",
        "स्वच्छ कोड अगले डेवलपर के लिए सुंदर गद्य की तरह पढ़ा जाता है।",
        "चरों के नाम स्पष्ट होने चाहिए जो उनके उद्देश्य को बताएँ।",
        "जल्दी और बार बार परीक्षण छोटी त्रुटियों को बड़ी समस्या बनने से रोकता है।",
        "लूप और शर्तें रोजमर्रा के प्रोग्रामिंग तर्क की रीढ़ हैं।",
        "वर्जन कंट्रोल एक टीम को बिना काम मिटाए मिलकर काम करने देता है।",
        "एल्गोरिद्म केवल सुस्पष्ट चरणों का एक क्रम मात्र होता है।",
        "टिप्पणियाँ बताती हैं कि कोड क्यों है न कि वह क्या करता है।",
        "बड़ी समस्या को छोटे भागों में बाँटना उसे हल करना आसान बनाता है।",
        "दूसरों का कोड पढ़ना सीखने का सबसे तेज तरीका है।",
    ],
    "general_knowledge": [
        "माउंट एवरेस्ट पृथ्वी पर समुद्र तल से सबसे ऊँचा पर्वत है।",
        "मानव शरीर में वयस्क अवस्था में दो सौ छह हड्डियाँ होती हैं।",
        "हमारे ग्रह की सतह का लगभग सत्तर प्रतिशत भाग जल से ढका है।",
        "प्रकाश संश्लेषण से हरे पौधे प्रकाश से अपना भोजन बनाते हैं।",
        "ध्वनि वायु की तुलना में जल में अधिक तेज गति से चलती है।",
        "सहारा संसार का सबसे बड़ा गर्म रेगिस्तान माना जाता है।",
        "हीरा विज्ञान को ज्ञात सबसे कठोर प्राकृतिक पदार्थ है।",
        "हृदय शिराओं और धमनियों के विशाल जाल से रक्त को पंप करता है।",
        "भारत का राष्ट्रीय पक्षी मोर अपनी सुंदरता के लिए प्रसिद्ध है।",
        "गंगा भारत की सबसे पवित्र और लंबी नदियों में से एक है।",
    ],
    "typing_practice": [
        "अपनी अंगुलियों को होम रो पर रखें और कलाई को शिथिल रखें।",
        "स्क्रीन को देखें और अंगुलियों पर भरोसा करें कि वे सही कुंजी ढूँढ लेंगी।",
        "धीमा और स्थिर अभ्यास गति से पहले शुद्धता का निर्माण करता है।",
        "हर बीस मिनट में थोड़ा विराम लें ताकि आँखों को आराम मिले।",
        "अचानक तेज झटकों के बजाय एक समान कीस्ट्रोक का लक्ष्य रखें।",
        "सही मुद्रा लंबे टाइपिंग सत्र के दौरान पीठ की रक्षा करती है।",
        "प्रतिदिन एक ही अभ्यास करने से प्रयास आसान आदत बन जाता है।",
        "आगे के शब्दों पर ध्यान दें और एक स्थिर लय को मार्गदर्शक बनने दें।",
        "पहले शुद्धता और गति धैर्य के साथ स्वयं ही आ जाएगी।",
        "लंबी टाइपिंग परीक्षा शुरू करने से पहले हाथों को धीरे से गर्म करें।",
    ],
}

HI_WORDS = (
    "समय वर्ष लोग दिन आदमी वस्तु महिला जीवन बच्चा संसार विद्यालय राज्य परिवार "
    "छात्र समूह देश समस्या हाथ भाग स्थान सप्ताह कंपनी प्रणाली प्रश्न कार्य सरकार "
    "संख्या रात बिंदु घर पानी कमरा माता क्षेत्र धन कहानी तथ्य महीना अधिकार अध्ययन "
    "पुस्तक नौकरी शब्द व्यापार पक्ष सिर सेवा मित्र पिता शक्ति घंटा खेल रेखा सदस्य "
    "कानून नगर समुदाय नाम टीम मिनट विचार शरीर सूचना माता पिता चेहरा स्तर कार्यालय "
    "द्वार स्वास्थ्य व्यक्ति कला इतिहास परिणाम परिवर्तन सुबह कारण शोध लड़की पल वायु "
    "शिक्षक बल शिक्षा मूल्य कागज प्रकाश मेज संगीत सड़क नदी बगीचा बाजार खिड़की पत्र "
    "भूमि भविष्य ऋतु प्रकृति ईमानदार बहादुर उज्ज्वल सरल मजबूत शांत प्रसन्न आधुनिक"
).split()


# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------

def _compose_paragraph(rng, sentences, difficulty):
    low, high = SENTENCES_PER_DIFFICULTY[difficulty]
    count = rng.randint(low, high)
    pool = sentences[:]
    rng.shuffle(pool)
    chosen = pool[:count]
    return " ".join(chosen)


def _compose_words(rng, word_bank, difficulty):
    count = WORDS_PER_DIFFICULTY[difficulty]
    return " ".join(rng.choice(word_bank) for _ in range(count))


def _word_count(text):
    return len(text.split())


def build_entries():
    """Return a deterministic list of paragraph dicts (400 total)."""
    rng = random.Random(20240601)
    entries = []
    seen = set()

    def add(language, category, difficulty, kind, content):
        key = (language, content)
        if key in seen:
            return False
        seen.add(key)
        entries.append({
            "language": language,
            "category": category,
            "difficulty": difficulty,
            "kind": kind,
            "content": content,
            "word_count": _word_count(content),
            "source": "seed",
        })
        return True

    # ---- Paragraphs: 100 English + 100 Hindi ----
    for language, banks in (("english", EN_SENTENCES), ("hindi", HI_SENTENCES)):
        produced = 0
        guard = 0
        di = 0
        ci = 0
        while produced < 100 and guard < 5000:
            guard += 1
            category = PARAGRAPH_CATEGORIES[ci % len(PARAGRAPH_CATEGORIES)]
            difficulty = DIFFICULTIES[di % len(DIFFICULTIES)]
            content = _compose_paragraph(rng, banks[category], difficulty)
            if add(language, category, difficulty, "paragraph", content):
                produced += 1
                ci += 1
                di += 1

    # ---- Random words: 100 English + 100 Hindi ----
    for language, bank in (("english", EN_WORDS), ("hindi", HI_WORDS)):
        produced = 0
        guard = 0
        di = 0
        while produced < 100 and guard < 5000:
            guard += 1
            difficulty = DIFFICULTIES[di % len(DIFFICULTIES)]
            content = _compose_words(rng, bank, difficulty)
            if add(language, "random_words", difficulty, "words", content):
                produced += 1
                di += 1

    return entries


# ---------------------------------------------------------------------------
# JSON mirror writers (fallback)
# ---------------------------------------------------------------------------

def _empty_lang_tree():
    tree = {}
    for cat in CATEGORY_KIND:
        tree[cat] = {"easy": [], "medium": [], "hard": []}
    return tree


def write_json_mirror(entries):
    os.makedirs(DATA_DIR, exist_ok=True)

    full = {"english": _empty_lang_tree(), "hindi": _empty_lang_tree()}

    # Simple per-language difficulty buckets used by the default typing pages
    simple_en = {"english": {"easy": [], "medium": [], "hard": []}}
    simple_hi = {"hindi": {"easy": [], "medium": [], "hard": []}}

    for e in entries:
        lang = e["language"]
        cat = e["category"]
        diff = e["difficulty"]
        full[lang].setdefault(cat, {"easy": [], "medium": [], "hard": []})
        full[lang][cat][diff].append(e["content"])

        if e["kind"] == "paragraph":
            if lang == "english":
                simple_en["english"][diff].append(e["content"])
            else:
                simple_hi["hindi"][diff].append(e["content"])

    with open(SEED_JSON, "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=2)

    with open(ENGLISH_JSON, "w", encoding="utf-8") as f:
        json.dump(simple_en, f, ensure_ascii=False, indent=2)

    with open(HINDI_JSON, "w", encoding="utf-8") as f:
        json.dump(simple_hi, f, ensure_ascii=False, indent=2)


def load_json_mirror():
    if not os.path.exists(SEED_JSON):
        return None
    try:
        with open(SEED_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Public seed entrypoint
# ---------------------------------------------------------------------------

def seed_paragraphs(force=False):
    """Seed the paragraphs table and write the JSON mirror.

    Safe to call on every startup: it only inserts when the table is empty
    (unless ``force`` is True).
    """
    entries = build_entries()

    # Always keep the JSON mirror fresh as a fallback.
    try:
        write_json_mirror(entries)
    except OSError:
        pass

    existing = Paragraph.query.count()
    if existing and not force:
        return existing

    if force and existing:
        Paragraph.query.delete()
        db.session.commit()

    db.session.bulk_save_objects([Paragraph(**e) for e in entries])
    db.session.commit()

    return Paragraph.query.count()
