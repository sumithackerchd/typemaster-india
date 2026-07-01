"""Paragraph Database seeder for TypeMaster India.

Generates and stores typing content:
    * 500 English paragraphs
    * 500 Hindi (Mangal) paragraphs
    * 500 English random-word sets
    * 500 Hindi random-word sets

Content spans every paragraph category and all three difficulties, and each
difficulty produces enough text for the 60 / 120 / 300 / 600 second tests.
No two stored paragraphs share the same content (per language).

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
    "court",
    "computer_operator",
    "typing_exam",
    "bank",
    "office",
    "government",
    "programming",
    "general_knowledge",
    "current_affairs",
    "typing_practice",
]

DIFFICULTIES = ["easy", "medium", "hard"]

# How many paragraphs / word-sets to generate per language.
PARAGRAPHS_PER_LANGUAGE = 500
WORDSETS_PER_LANGUAGE = 500

# Sentences per difficulty bucket. Higher difficulty = longer text so that
# even the 600 second (10 minute) test never runs out of content.
SENTENCES_PER_DIFFICULTY = {"easy": (3, 5), "medium": (7, 11), "hard": (16, 26)}

# Word count per difficulty for random-word sets.
WORDS_PER_DIFFICULTY = {"easy": 40, "medium": 90, "hard": 220}


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
        "Every sunset promises a brand new sunrise waiting for us.",
        "Curiosity is the spark that lights the lamp of true learning.",
        "A gentle word can turn a difficult day into a pleasant one.",
        "The mountains stood silent under a blanket of soft white snow.",
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
        "Solving previous year papers reveals the weight of every topic.",
        "A disciplined timetable keeps preparation steady and stress free.",
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
        "The signalling system keeps every train moving in perfect order.",
        "Freight corridors carry goods across the country day and night.",
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
        "A calm mind under pressure is the mark of a trained officer.",
        "Community trust grows when the police serve with fairness.",
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
        "Shortcut keys save valuable time during the practical assessment.",
        "Regular breaks keep the fingers relaxed and the mind focused.",
    ],
    "court": [
        "The court is a place where justice is delivered with fairness and care.",
        "A stenographer must type legal dictation quickly and without any error.",
        "Every judgment is recorded carefully for the official court register.",
        "Lawyers present their arguments before the honourable presiding judge.",
        "Accuracy in legal documents protects the rights of every citizen.",
        "The clerk maintains case files and prepares the daily cause list.",
        "Witnesses give their statements under a solemn oath of truth.",
        "Court typing tests demand a very high standard of speed and accuracy.",
        "The registrar verifies documents before they are placed on record.",
        "Legal terminology must be typed exactly as it is dictated aloud.",
        "Patience and precision are the finest qualities of a court typist.",
        "The verdict is announced only after a careful review of the evidence.",
    ],
    "computer_operator": [
        "A computer operator manages daily data entry with speed and accuracy.",
        "Backing up important files prevents the loss of valuable information.",
        "The operator prepares reports using spreadsheets and word processors.",
        "Clean and organised folders make everyday work faster and easier.",
        "Regular software updates keep the office systems safe and stable.",
        "Fast and accurate typing is the core skill of a good operator.",
        "Printers, scanners and networks are handled with basic technical care.",
        "Passwords should be strong and changed at regular intervals.",
        "The operator records attendance and updates the central database.",
        "A tidy workspace and steady focus improve the quality of output.",
        "Data must be checked twice before it is saved to the main server.",
        "Simple shortcuts turn a long task into a quick and smooth routine.",
    ],
    "typing_exam": [
        "The typing exam measures both your gross speed and your net accuracy.",
        "Sit straight, relax your shoulders and place your fingers on the keys.",
        "Read a few words ahead so your fingers never have to wait.",
        "One careless error can lower your score more than a slow pace.",
        "Steady breathing keeps your hands calm during the timed test.",
        "The passage must be typed exactly as it appears on the screen.",
        "Punctuation and capital letters are counted in the final result.",
        "A short warm up before the exam sharpens your finger memory.",
        "Do not look at the keyboard; trust the training in your hands.",
        "Consistent daily practice is the surest path to a high score.",
        "Speed grows naturally once accuracy becomes a firm habit.",
        "Stay focused on the current line and let the rhythm carry you.",
    ],
    "bank": [
        "A bank keeps the savings of the public safe and secure.",
        "The clerk records every transaction with great care and honesty.",
        "Interest is the reward that a bank pays on your deposits.",
        "Loans help people and businesses grow when they are used wisely.",
        "Online banking lets customers manage money from anywhere at any time.",
        "The cashier balances the cash drawer at the end of each day.",
        "Strong passwords protect an account from fraud and theft.",
        "The bank exam tests reasoning, quantitative aptitude and English.",
        "Customer service is the heart of a trusted banking institution.",
        "Every cheque is verified before the amount is finally cleared.",
        "Financial discipline today builds a secure and stable tomorrow.",
        "The branch manager reviews reports and approves daily operations.",
    ],
    "office": [
        "A well organised office runs smoothly from morning until evening.",
        "Emails should be clear, polite and to the point at all times.",
        "Meetings work best when everyone arrives prepared and on time.",
        "Filing documents in order saves hours of searching later.",
        "Teamwork turns a heavy workload into a shared and lighter task.",
        "A neat desk reflects a calm and well organised mind.",
        "Deadlines are met when tasks are planned and reviewed daily.",
        "Good communication prevents small confusions from becoming problems.",
        "The manager assigns duties and tracks the progress of each project.",
        "Taking short notes during a call helps you remember the details.",
        "Respect and courtesy make the workplace pleasant for everyone.",
        "A printed report should be checked once more before it is sent.",
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
        "Revision notes turn a huge syllabus into small manageable pieces.",
        "Mock interviews build the confidence needed for the final stage.",
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
        "A good data structure often makes a hard problem feel simple.",
        "Refactoring keeps a growing project healthy and easy to maintain.",
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
        "The moon controls the rise and fall of the ocean tides.",
        "Honey never spoils and can last for thousands of years.",
    ],
    "current_affairs": [
        "Digital payments have become a part of everyday life across the nation.",
        "Renewable energy projects are growing rapidly in many states.",
        "Space missions continue to inspire young students to study science.",
        "New expressways are reducing travel time between major cities.",
        "Start ups are creating fresh jobs and bold ideas every single year.",
        "Clean water and sanitation remain important goals for every village.",
        "Sports achievements bring pride and unity to the whole country.",
        "Awareness of climate change is rising among students and citizens.",
        "Online education has reached learners in the most remote areas.",
        "Financial literacy helps families plan their savings more wisely.",
        "Healthcare services are expanding to smaller towns and districts.",
        "Technology is making government services faster and more transparent.",
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
        "Keep your elbows close and your fingers curved over the keys.",
        "A quiet room and a clear mind make practice far more effective.",
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
    "honest brave bright simple strong gentle quiet happy clever modern global "
    "answer chance course design effort growth income market notice object "
    "policy quality region source target update village weather balance culture"
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
        "हर सूर्यास्त एक नए सवेरे का मधुर वादा लेकर आता है।",
        "जिज्ञासा ही सच्चे ज्ञान का दीपक जलाने वाली चिंगारी है।",
        "एक मधुर वचन कठिन दिन को भी सुखद बना देता है।",
        "पर्वत श्वेत बर्फ की चादर ओढ़े मौन खड़े रहते हैं।",
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
        "पिछले वर्षों के प्रश्नपत्र हल करने से हर विषय का महत्व समझ आता है।",
        "अनुशासित समय सारणी तैयारी को स्थिर और तनावमुक्त बनाती है।",
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
        "सिग्नल प्रणाली हर गाड़ी को सही क्रम में चलाए रखती है।",
        "माल गाड़ियाँ दिन रात देशभर में सामान पहुँचाती रहती हैं।",
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
        "दबाव में शांत मन प्रशिक्षित अधिकारी की पहचान है।",
        "निष्पक्ष सेवा से जनता का विश्वास बढ़ता है।",
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
        "शॉर्टकट कुंजियाँ व्यावहारिक परीक्षा में बहुमूल्य समय बचाती हैं।",
        "नियमित विराम अंगुलियों को शिथिल और मन को केंद्रित रखते हैं।",
    ],
    "court": [
        "न्यायालय वह स्थान है जहाँ निष्पक्षता से न्याय दिया जाता है।",
        "आशुलिपिक को विधिक श्रुतलेख तेज और बिना त्रुटि के टाइप करना होता है।",
        "हर निर्णय न्यायालय के आधिकारिक रजिस्टर में सावधानी से दर्ज होता है।",
        "अधिवक्ता माननीय न्यायाधीश के समक्ष अपने तर्क प्रस्तुत करते हैं।",
        "विधिक दस्तावेज़ों की शुद्धता हर नागरिक के अधिकारों की रक्षा करती है।",
        "लिपिक मुकदमों की फाइलें रखता और दैनिक वाद सूची तैयार करता है।",
        "गवाह सत्य की गंभीर शपथ लेकर अपना बयान देते हैं।",
        "न्यायालय की टाइपिंग परीक्षा गति और शुद्धता का ऊँचा स्तर माँगती है।",
        "रजिस्ट्रार दस्तावेज़ों को अभिलेख में रखने से पहले सत्यापित करता है।",
        "विधिक शब्दावली को ठीक वैसे ही टाइप करना होता है जैसे बोली जाती है।",
        "धैर्य और सटीकता न्यायालय आशुलिपिक के श्रेष्ठ गुण हैं।",
        "साक्ष्य की सावधानी से समीक्षा के बाद ही निर्णय सुनाया जाता है।",
    ],
    "computer_operator": [
        "कंप्यूटर ऑपरेटर दैनिक डेटा प्रविष्टि को गति और शुद्धता से करता है।",
        "महत्वपूर्ण फाइलों का बैकअप सूचना के नुकसान को रोकता है।",
        "ऑपरेटर स्प्रेडशीट और वर्ड प्रोसेसर से रिपोर्ट तैयार करता है।",
        "स्वच्छ और व्यवस्थित फोल्डर रोज़मर्रा के काम को आसान बनाते हैं।",
        "नियमित सॉफ्टवेयर अपडेट कार्यालय प्रणालियों को सुरक्षित रखते हैं।",
        "तेज और सटीक टाइपिंग एक अच्छे ऑपरेटर का मुख्य कौशल है।",
        "प्रिंटर स्कैनर और नेटवर्क को बुनियादी तकनीकी सावधानी से संभाला जाता है।",
        "पासवर्ड मजबूत होने चाहिए और नियमित अंतराल पर बदलने चाहिए।",
        "ऑपरेटर उपस्थिति दर्ज करता और केंद्रीय डेटाबेस अद्यतन करता है।",
        "साफ कार्यस्थल और स्थिर ध्यान कार्य की गुणवत्ता बढ़ाते हैं।",
        "डेटा को मुख्य सर्वर पर सहेजने से पहले दो बार जाँचना चाहिए।",
        "सरल शॉर्टकट लंबे कार्य को तेज और सहज बना देते हैं।",
    ],
    "typing_exam": [
        "टाइपिंग परीक्षा आपकी सकल गति और शुद्ध सटीकता दोनों मापती है।",
        "सीधे बैठें कंधे ढीले रखें और अंगुलियाँ कुंजियों पर रखें।",
        "कुछ शब्द आगे पढ़ें ताकि अंगुलियों को कभी रुकना न पड़े।",
        "एक लापरवाह त्रुटि धीमी गति से भी अधिक अंक घटा सकती है।",
        "स्थिर साँस समयबद्ध परीक्षा में हाथों को शांत रखती है।",
        "पाठ को ठीक वैसे ही टाइप करना है जैसा स्क्रीन पर दिखता है।",
        "विराम चिह्न और बड़े अक्षर अंतिम परिणाम में गिने जाते हैं।",
        "परीक्षा से पहले छोटा अभ्यास अंगुलियों की स्मृति को तेज करता है।",
        "कीबोर्ड की ओर न देखें अपने हाथों के प्रशिक्षण पर भरोसा रखें।",
        "निरंतर दैनिक अभ्यास ऊँचे अंक तक पहुँचने का सुनिश्चित मार्ग है।",
        "शुद्धता आदत बनते ही गति स्वयं ही बढ़ने लगती है।",
        "वर्तमान पंक्ति पर ध्यान दें और लय को आगे बढ़ने दें।",
    ],
    "bank": [
        "बैंक जनता की बचत को सुरक्षित और संरक्षित रखता है।",
        "लिपिक हर लेन देन को बड़ी सावधानी और ईमानदारी से दर्ज करता है।",
        "ब्याज वह पुरस्कार है जो बैंक आपकी जमा राशि पर देता है।",
        "ऋण लोगों और व्यवसायों को समझदारी से उपयोग करने पर बढ़ने में मदद करता है।",
        "ऑनलाइन बैंकिंग ग्राहकों को कहीं भी कभी भी धन प्रबंधन की सुविधा देती है।",
        "खजांची हर दिन के अंत में नकद दराज का मिलान करता है।",
        "मजबूत पासवर्ड खाते को धोखाधड़ी और चोरी से बचाते हैं।",
        "बैंक परीक्षा तर्क संख्यात्मक योग्यता और अंग्रेजी का परीक्षण करती है।",
        "ग्राहक सेवा एक विश्वसनीय बैंकिंग संस्था का हृदय है।",
        "राशि अंतिम रूप से स्वीकृत होने से पहले हर चेक सत्यापित होता है।",
        "आज की वित्तीय अनुशासन सुरक्षित और स्थिर कल का निर्माण करती है।",
        "शाखा प्रबंधक रिपोर्ट देखता और दैनिक कार्यों को स्वीकृति देता है।",
    ],
    "office": [
        "एक सुव्यवस्थित कार्यालय सुबह से शाम तक सुचारु रूप से चलता है।",
        "ईमेल हमेशा स्पष्ट विनम्र और सटीक होने चाहिए।",
        "बैठकें तब सर्वोत्तम चलती हैं जब सब तैयार और समय पर आते हैं।",
        "दस्तावेज़ों को क्रम में रखना बाद में घंटों की खोज बचाता है।",
        "टीम भावना भारी काम को साझा और हल्का कार्य बना देती है।",
        "साफ मेज एक शांत और व्यवस्थित मन को दर्शाती है।",
        "कार्य की योजना और दैनिक समीक्षा से समय सीमा पूरी होती है।",
        "अच्छा संवाद छोटी उलझनों को समस्या बनने से रोकता है।",
        "प्रबंधक कार्य सौंपता और हर परियोजना की प्रगति पर नज़र रखता है।",
        "कॉल के दौरान छोटे नोट लेना विवरण याद रखने में मदद करता है।",
        "सम्मान और शिष्टाचार कार्यस्थल को सबके लिए सुखद बनाते हैं।",
        "भेजने से पहले छपी हुई रिपोर्ट को एक बार और जाँचना चाहिए।",
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
        "पुनरावृत्ति नोट्स विशाल पाठ्यक्रम को छोटे भागों में बदल देते हैं।",
        "मॉक साक्षात्कार अंतिम चरण के लिए आवश्यक आत्मविश्वास बनाते हैं।",
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
        "अच्छी डेटा संरचना कठिन समस्या को अक्सर सरल बना देती है।",
        "रीफैक्टरिंग बढ़ती परियोजना को स्वस्थ और सरल बनाए रखती है।",
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
        "चंद्रमा समुद्र में ज्वार भाटा के उतार चढ़ाव को नियंत्रित करता है।",
        "शहद कभी खराब नहीं होता और हजारों वर्ष तक टिक सकता है।",
    ],
    "current_affairs": [
        "डिजिटल भुगतान अब देशभर में रोज़मर्रा के जीवन का हिस्सा बन गया है।",
        "नवीकरणीय ऊर्जा परियोजनाएँ कई राज्यों में तेजी से बढ़ रही हैं।",
        "अंतरिक्ष अभियान युवा छात्रों को विज्ञान पढ़ने के लिए प्रेरित करते हैं।",
        "नए एक्सप्रेसवे प्रमुख शहरों के बीच यात्रा समय घटा रहे हैं।",
        "स्टार्ट अप हर वर्ष नए रोजगार और साहसी विचार पैदा कर रहे हैं।",
        "स्वच्छ जल और स्वच्छता हर गाँव के लिए महत्वपूर्ण लक्ष्य हैं।",
        "खेल उपलब्धियाँ पूरे देश में गर्व और एकता लाती हैं।",
        "जलवायु परिवर्तन के प्रति जागरूकता छात्रों और नागरिकों में बढ़ रही है।",
        "ऑनलाइन शिक्षा सबसे दूरदराज के क्षेत्रों तक पहुँच गई है।",
        "वित्तीय साक्षरता परिवारों को अपनी बचत की समझदारी से योजना बनाने में मदद करती है।",
        "स्वास्थ्य सेवाएँ छोटे शहरों और जिलों तक फैल रही हैं।",
        "तकनीक सरकारी सेवाओं को तेज और अधिक पारदर्शी बना रही है।",
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
        "कोहनियाँ पास रखें और अंगुलियों को कुंजियों पर मोड़ कर रखें।",
        "शांत कमरा और स्पष्ट मन अभ्यास को कहीं अधिक प्रभावी बनाते हैं।",
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
    "भूमि भविष्य ऋतु प्रकृति ईमानदार बहादुर उज्ज्वल सरल मजबूत शांत प्रसन्न आधुनिक "
    "उत्तर अवसर पाठ्यक्रम रचना प्रयास वृद्धि आय सूचना नीति गुणवत्ता स्रोत लक्ष्य गाँव मौसम"
).split()


# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------

def _compose_paragraph(rng, sentences, difficulty):
    low, high = SENTENCES_PER_DIFFICULTY[difficulty]
    count = rng.randint(low, high)

    pool = sentences[:]
    rng.shuffle(pool)

    chosen = []
    # Fill up to ``count`` sentences, reshuffling the pool when exhausted so we
    # can build the long "hard" paragraphs without index errors.
    while len(chosen) < count:
        if not pool:
            pool = sentences[:]
            rng.shuffle(pool)
        chosen.append(pool.pop())

    return " ".join(chosen)


def _compose_words(rng, word_bank, difficulty):
    count = WORDS_PER_DIFFICULTY[difficulty]
    return " ".join(rng.choice(word_bank) for _ in range(count))


def _word_count(text):
    return len(text.split())


def build_entries():
    """Return a deterministic list of paragraph dicts (2000 total)."""
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

    # ---- Paragraphs: 500 English + 500 Hindi ----
    for language, banks in (("english", EN_SENTENCES), ("hindi", HI_SENTENCES)):
        produced = 0
        guard = 0
        di = 0
        ci = 0
        while produced < PARAGRAPHS_PER_LANGUAGE and guard < 200000:
            guard += 1
            category = PARAGRAPH_CATEGORIES[ci % len(PARAGRAPH_CATEGORIES)]
            difficulty = DIFFICULTIES[di % len(DIFFICULTIES)]
            content = _compose_paragraph(rng, banks[category], difficulty)
            if add(language, category, difficulty, "paragraph", content):
                produced += 1
                ci += 1
                di += 1

    # ---- Random words: 500 English + 500 Hindi ----
    for language, bank in (("english", EN_WORDS), ("hindi", HI_WORDS)):
        produced = 0
        guard = 0
        di = 0
        while produced < WORDSETS_PER_LANGUAGE and guard < 200000:
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
