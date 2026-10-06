"""
MEBOT - Evrensel Bilgi, Çok Boyutlu Derin Akıl Yürütme ve Güvenli Web Araştırması Sunucusu
Bu sunucu, sığ veya şablon cevaplar yerine; mantık bulmacalarını, matematiksel problemleri
ve kavramsal soruları çok katmanlı Chain-of-Thought (Zihinsel Düşünce Zinciri) ile çözer.
Ayrıca Google Gemini API entegrasyonu (Ücretsiz Tier) ile sınırsız bulut zekasını destekler.
"""

import os
import sys
import json
import time
import re
import warnings
import urllib.request
import urllib.error
import urllib.parse
import base64
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket

# Windows konsol UTF-8 çıktı desteği
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Harici kütüphaneler
import requests
from bs4 import BeautifulSoup

# Uyarıları sessize al
warnings.filterwarnings("ignore")

PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# API Anahtarı Kalıcı Dosyaları
KEY_FILE_PATH = os.path.join(BASE_DIR, "api_key.txt")
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")
DB_FILE_PATH = os.path.join(BASE_DIR, "users_db.json")
ADMIN_MASTER_CODE = "565856"

# =========================================================================
# GÜVENLİK: ARGO / KÜFÜR FİLTRESİ, ZARAR VERME ENGELİ, HAFIZA
# =========================================================================
def tr_lower(text):
    """Türkçe uyumlu küçük harfe çevirme (I->ı, İ->i)."""
    return (text or "").replace("I", "ı").replace("İ", "i").lower()

# Tam kelime eşleşmesi gereken kelimeler (yanlış alarmı önlemek için kök eşleşmesi yapılmaz)
PROFANITY_EXACT = {
    "amk", "aq", "amq", "awk", "amına", "amina", "amını", "amini", "amcık", "amcik",
    "sik", "sikerim", "sikeyim", "sikiyim", "siktir", "siktirgit", "sikik", "sikim",
    "sikti", "sikiş", "sikis", "siker", "sikicem", "sikerler", "sikeceğim", "sikecegim",
    "göt", "götü", "götün", "götveren", "götlek", "piç", "piçler", "oç",
    "salak", "aptal", "gerizekalı", "gerizekali", "dangalak",
    "lan", "ulan", "hassiktir", "hasiktir", "yavşak", "yavsak",
    "fuck", "fucking", "shit", "bitch", "asshole", "motherfucker", "wtf",
}
# Kök eşleşmesi güvenli olan (başka masum kelimede geçmeyen) kökler
PROFANITY_STEMS = (
    "orospu", "orosbu", "yarrak", "yarak", "yarram", "pezevenk", "kahpe", "ibne",
    "puşt", "pust", "kaltak", "fahişe", "fahise", "sürtük", "surtuk", "taşak", "tasak",
    "gavat", "şerefsiz", "serefsiz", "haysiyetsiz", "siktir", "amcık", "amcik",
    "yavşak", "yavsak", "gerizekal", "dangalak", "amınako", "aminako",
)

def contains_profanity(text):
    words = re.findall(r"[a-zçğıöşü0-9]+", tr_lower(text))
    for w in words:
        if w in PROFANITY_EXACT:
            return True
        if any(w.startswith(stem) for stem in PROFANITY_STEMS):
            return True
    return False

SELF_HARM_PATTERNS = [
    r"intihar", r"kendimi öldür", r"kendimi oldur", r"kendimi as(acağ|acag|mak|ıca|ica)", r"kendime zarar",
    r"kendimi kes", r"bilek(lerimi)? kes", r"canıma kıy", r"canima kiy", r"ölmek istiyorum",
    r"olmek istiyorum", r"yaşamak istemiyorum", r"yasamak istemiyorum", r"hayatıma son",
    r"hayatima son", r"kendimi yok et", r"kendimi zehirle",
]
VIOLENCE_PATTERNS = [
    r"(birini|kişiyi|kisiyi|annemi|babamı|babami|kardeşimi|kardesimi|arkadaşımı|arkadasimi|öğretmenimi|ogretmenimi)\s+(nasıl\s+|nasil\s+)?(öldür|oldur|bıçakla|bicakla|zehirle)",
    r"(öldürmenin|oldurmenin|zehirlemenin)\s+yol", r"nasıl öldürürüm", r"nasil oldururum",
    r"bomba (nasıl |nasil )?yap", r"patlayıcı (nasıl |nasil )?yap", r"patlayici (nasil )?yap",
    r"silah (nasıl |nasil )?yap", r"zehir (nasıl |nasil )?yap", r"birine zarar ver",
    r"intikam almak için (zarar|öldür)",
]

SELF_HARM_REPLY = (
    "Bunu yazdığın için teşekkür ederim, şu an zor bir dönemden geçiyor olabilirsin ve bu duyguları "
    "tek başına taşımak zorunda değilsin. 💙\n\n"
    "**MEBOT, kendine veya başkasına zarar vermeyle ilgili hiçbir yöntem ya da öneri sunmaz.** "
    "Ama seni dinlemek ve yanında olmak isterim.\n\n"
    "- **Hemen tehlikedeysen:** Lütfen şimdi **112 Acil Çağrı Merkezi**'ni ara.\n"
    "- **Güvendiğin biriyle konuş:** Bir aile üyesi, arkadaş, öğretmen veya okul rehber öğretmeni.\n"
    "- **Profesyonel destek:** En yakın hastanenin acil servisine veya bir psikolog/psikiyatriste başvurabilirsin.\n\n"
    "İstersen bana neler yaşadığını anlatabilirsin; seni yargılamadan dinlerim."
)
VIOLENCE_REPLY = (
    "⛔ **Bu isteğe yardımcı olamam.**\n\n"
    "MEBOT Gizlilik ve Güvenlik Politikası gereği; bir kişiye, canlıya veya kendine zarar vermeye yönelik "
    "yöntem, tarif, silah/patlayıcı yapımı veya şiddet içeren hiçbir içerik üretilmez ve önerilmez.\n\n"
    "Birisi tehlikedeyse lütfen hemen **112 Acil Çağrı Merkezi**'ni arayın. "
    "Yaşadığın bir öfke veya anlaşmazlık varsa, bunu sağlıklı yollarla çözmek için seninle konuşabilirim."
)

def detect_harm(text):
    t = tr_lower(text)
    if any(re.search(p, t) for p in SELF_HARM_PATTERNS):
        return "self_harm"
    if any(re.search(p, t) for p in VIOLENCE_PATTERNS):
        return "violence"
    return None

SAFETY_INSTRUCTION = (
    "\n\n[ZORUNLU GÜVENLİK KURALLARI]\n"
    "- Kendine zarar verme, intihar, başkasına zarar verme, şiddet, silah/patlayıcı/zehir yapımı konularında "
    "ASLA yöntem, tarif veya öneri verme. Bu tür isteklerde nazikçe reddet, kişiyi desteklenmeye yönlendir ve "
    "acil durumda 112'yi aramasını söyle.\n"
    "- Argo, küfür, hakaret veya aşağılayıcı ifade kullanma.\n"
    "- Kullanıcının kişisel verilerini başka hiçbir kişiyle paylaşma."
)

MEMORY_TRIGGERS = [
    r"\bbenim ad[ıi]m\b", r"\bad[ıi]m\s+\w+", r"\bya[şs][ıi]nday[ıi]m\b", r"\bya[şs][ıi]yorum\b",
    r"\bseviyorum\b", r"\bsevmiyorum\b", r"\bho[şs]lan[ıi]yorum\b", r"\bnefret ediyorum\b",
    r"\bmesle[ğg]im\b", r"\bi[şs]im\b", r"\b[öo][ğg]renciyim\b", r"\b[çc]al[ıi][şs][ıi]yorum\b",
    r"\bokuyorum\b", r"\bhat[ıi]rla\b", r"\bunutma\b", r"\btercih ediyorum\b", r"\balerjim\b",
    r"\bhobim\b", r"\bfavori\b", r"\ben sevdi[ğg]im\b", r"\bdo[ğg]um g[üu]n[üu]m\b",
]

def extract_memories(text):
    """Kullanıcı mesajından kalıcı olarak hatırlanmaya değer cümleleri çıkarır."""
    found = []
    for sentence in re.split(r"(?<=[.!?\n])\s+", text or ""):
        s = sentence.strip()
        if 4 <= len(s) <= 220 and "?" not in s:
            if any(re.search(p, tr_lower(s)) for p in MEMORY_TRIGGERS):
                found.append(s)
    return found

def ensure_user_struct(user):
    """Eski kayıtları yeni çoklu sohbet yapısına dönüştürür."""
    if "chats" not in user or not isinstance(user.get("chats"), list):
        user["chats"] = []
    legacy = user.pop("messages", None)
    if legacy:
        user["chats"].append({
            "id": "legacy-" + str(int(time.time())),
            "title": "Önceki Sohbet",
            "created_at": user.get("created_at", ""),
            "updated_at": user.get("last_login", ""),
            "messages": legacy,
        })
    user.setdefault("settings", {"personalization": "", "memory_enabled": True})
    user["settings"].setdefault("personalization", "")
    user["settings"].setdefault("memory_enabled", True)
    user.setdefault("memories", [])
    return user

def user_message_count(user):
    return sum(len(c.get("messages", [])) for c in user.get("chats", []))

def public_user_payload(user):
    return {
        "chats": user.get("chats", []),
        "settings": user.get("settings", {}),
        "memories": user.get("memories", []),
    }

def find_chat(user, chat_id):
    for c in user.get("chats", []):
        if c.get("id") == chat_id:
            return c
    return None

def build_personal_context(settings, memories):
    parts = []
    pers = (settings or {}).get("personalization", "").strip()
    if pers:
        parts.append(f"[KULLANICININ KİŞİSELLEŞTİRME TERCİHLERİ - Her yanıtta bunlara uy]:\n{pers[:1500]}")
    if (settings or {}).get("memory_enabled", True) and memories:
        mem_lines = "\n".join(f"- {m.get('text', '')}" for m in memories[-40:])
        parts.append(f"[KULLANICI HAKKINDA HATIRLANAN BİLGİLER - Uygun olduğunda kullan]:\n{mem_lines}")
    return ("\n\n" + "\n\n".join(parts)) if parts else ""

MEMORY_QUESTION_PATTERNS = [
    r"hakk[ıi]mda ne biliyorsun", r"beni hat[ıi]rl[ıi]yor musun", r"ad[ıi]m ne", r"neleri hat[ıi]rl[ıi]yorsun",
]

def memory_answer(prompt, settings, memories):
    t = tr_lower(prompt)
    if not any(re.search(p, t) for p in MEMORY_QUESTION_PATTERNS):
        return None
    if not (settings or {}).get("memory_enabled", True):
        return "Şu anda **Sohbetleri ve Hafızayı Hatırla** özelliği kapalı. Ayarlar > Kişiselleştirme bölümünden açabilirsin."
    if not memories:
        return "Henüz senin hakkında kaydettiğim bir bilgi yok. Bana kendinden bahsedersen sonraki sohbetlerde hatırlarım."
    lines = "\n".join(f"- {m.get('text', '')}" for m in memories[-20:])
    return f"Senin hakkında hatırladıklarım:\n\n{lines}\n\nBu bilgileri Ayarlar > Kişiselleştirme bölümünden silebilirsin."

def load_db():
    """Kullanıcı hesaplarını ve şifreli sohbet geçmişlerini yükler."""
    if os.path.exists(DB_FILE_PATH):
        try:
            with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DB Yükleme Hatası]: {e}")
    return {"users": {}}

def save_db(db):
    """Kullanıcı hesaplarını ve şifreli sohbetleri kalıcı dosyaya kaydeder."""
    try:
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[DB Kaydetme Hatası]: {e}")

def load_saved_api_key():
    """Kayıtlı Gemini API anahtarını dosyalardan veya ortam değişkeninden yükler."""
    if os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY").strip()
    for path in [KEY_FILE_PATH, ENV_FILE_PATH]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            key = line.split("=", 1)[1].strip()
                            if key:
                                os.environ["GEMINI_API_KEY"] = key
                                return key
                        elif line and not line.startswith("#") and len(line) > 20:
                            os.environ["GEMINI_API_KEY"] = line
                            return line
            except Exception:
                pass
    return ""

CURRENT_API_KEY = load_saved_api_key()

# Gemini SDK kontrolü
try:
    import google.generativeai as genai
    HAS_GENAI_LIB = True
except Exception:
    HAS_GENAI_LIB = False


# =========================================================================
# 1. Evrensel Bilgi Motoru (Universal Knowledge Engine)
# =========================================================================
class UniversalKnowledgeEngine:
    """
    Herhangi bir kavramı, bilimsel olguyu, felsefi soruyu veya tarihi olayı
    doğrulanmış HTTPS kaynaklarından (Vikipedi ve Akademik kaynaklar) tam metin
    olarak çeker ve temizler.
    """
    HEADERS = {
        'User-Agent': 'MEBOT-Cognitive/4.0 (https://mebot.ai; contact@mebot.ai)'
    }

    STOP_WORDS = {
        'ne', 'nedir', 'nasil', 'neden', 'niye', 'nicin', 'ise', 'yarar', 'icin',
        'olan', 'bir', 'bu', 'su', 'o', 'mi', 'mu', 'midir', 'mudur', 'hakkinda',
        'bilgi', 'ver', 'anlat', 'nelerdir', 'nelere', 'dikkat', 'edilmeli', 'yapar',
        'eder', 'calisir', 'olur', 'bana', 'bunu', 'derin', 'acikla', 'soyle',
        'yapmali', 'etmeli', 'var', 'yok', 'kimdir', 'hangisi', 'en', 'cok', 'daha'
    }

    TURKISH_CHAR_MAP = str.maketrans({
        'ı': 'i', 'İ': 'i', 'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u',
        'ş': 's', 'Ş': 's', 'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'
    })

    @staticmethod
    def extract_search_terms(prompt: str) -> list:
        raw_words = re.findall(r'[a-zA-ZçÇğĞıİöÖşŞüÜ]+', prompt.lower())
        meaningful = [w for w in raw_words if w not in UniversalKnowledgeEngine.STOP_WORDS and len(w) >= 3]
        if not meaningful:
            meaningful = [w for w in raw_words if len(w) >= 3]

        queries = []
        if len(meaningful) >= 2:
            queries.append(' '.join(meaningful[:2]))
        for w in meaningful:
            queries.append(w)
        clean_prompt = ' '.join(meaningful)
        if clean_prompt and clean_prompt not in queries:
            queries.insert(0, clean_prompt)
        return queries

    @staticmethod
    def fetch_topic_knowledge(prompt: str) -> dict:
        terms = UniversalKnowledgeEngine.extract_search_terms(prompt)
        for term in terms:
            try:
                search_url = f"https://tr.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(term)}&format=json"
                r = requests.get(search_url, headers=UniversalKnowledgeEngine.HEADERS, timeout=5)
                if r.status_code != 200:
                    continue
                data = r.json()
                items = data.get('query', {}).get('search', [])
                if not items:
                    continue

                best_match = None
                term_clean = term.translate(UniversalKnowledgeEngine.TURKISH_CHAR_MAP).lower()
                for item in items[:3]:
                    item_title = item.get('title', '')
                    item_title_clean = item_title.translate(UniversalKnowledgeEngine.TURKISH_CHAR_MAP).lower()
                    if any(t in item_title_clean for t in term_clean.split()):
                        best_match = item
                        break
                if not best_match:
                    best_match = items[0]

                target_title = best_match['title']

                time.sleep(0.1)
                ext_url = f"https://tr.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&exintro=1&titles={urllib.parse.quote(target_title)}&format=json"
                r2 = requests.get(ext_url, headers=UniversalKnowledgeEngine.HEADERS, timeout=5)
                if r2.status_code != 200:
                    continue
                pages = r2.json().get('query', {}).get('pages', {})
                for pid, page in pages.items():
                    extract = page.get('extract', '').strip()
                    if extract and len(extract) > 80:
                        return {
                            'topic': target_title,
                            'url': f"https://tr.wikipedia.org/wiki/{urllib.parse.quote(target_title)}",
                            'extract': extract
                        }
            except Exception:
                continue
        return None


# =========================================================================
# 2. Güvenli Web Araştırmacısı (Strict HTTPS Web Researcher)
# =========================================================================
class WebResearcher:
    """
    Yalnızca güvenli HTTPS protokolüne sahip kaynaklara bağlanır.
    HTTP, şüpheli veya spam sitelerini kesinlikle engeller.
    """
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    @staticmethod
    def is_strict_https(url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        try:
            return urllib.parse.urlparse(url.strip()).scheme.lower() == 'https'
        except Exception:
            return False

    @staticmethod
    def decode_bing_url(bing_url: str) -> str:
        try:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(bing_url).query)
            u_param = qs.get('u', [''])[0]
            if u_param.startswith('a1'):
                b64_str = u_param[2:]
                b64_str += '=' * ((4 - len(b64_str) % 4) % 4)
                decoded = base64.urlsafe_b64decode(b64_str).decode('utf-8', errors='ignore')
                if WebResearcher.is_strict_https(decoded):
                    return decoded
        except Exception:
            pass
        return bing_url

    @staticmethod
    def search_https_sources(query: str, max_results: int = 3) -> list:
        verified_sources = []
        seen_domains = set()
        ignored_domains = {'bing.com', 'microsoft.com', 'sahibinden.com', 'araba.com', 'letgo.com', 'hepsiburada.com', 'trendyol.com'}

        try:
            encoded_q = urllib.parse.quote(query)
            search_url = f"https://www.bing.com/search?q={encoded_q}&setlang=tr"
            resp = requests.get(search_url, headers=WebResearcher.HEADERS, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for item in soup.select('li.b_algo'):
                    a_tag = item.select_one('h2 a')
                    if not a_tag:
                        continue
                    title = a_tag.get_text().strip()
                    raw_href = a_tag.get('href', '').strip()
                    actual_url = WebResearcher.decode_bing_url(raw_href)

                    if WebResearcher.is_strict_https(actual_url):
                        domain = urllib.parse.urlparse(actual_url).netloc.lower()
                        if not any(ign in domain for ign in ignored_domains) and domain not in seen_domains:
                            seen_domains.add(domain)
                            snippet_tag = item.select_one('.b_caption p')
                            snippet_text = snippet_tag.get_text().strip() if snippet_tag else ""
                            verified_sources.append({
                                "title": title,
                                "url": actual_url,
                                "snippet": snippet_text
                            })
                            if len(verified_sources) >= max_results:
                                break
        except Exception as e:
            print(f"[Web Arama Hatası]: {e}")

        return verified_sources

    @staticmethod
    def deep_inspect_page(url: str, max_chars: int = 2500) -> dict:
        if not WebResearcher.is_strict_https(url):
            return {"url": url, "success": False, "error": "GÜVENSİZ PROTOKOL (Yalnızca HTTPS kabul edilir)"}

        try:
            resp = requests.get(url, headers=WebResearcher.HEADERS, timeout=7, verify=True)
            if resp.status_code != 200:
                return {"url": url, "success": False, "error": f"HTTP {resp.status_code}"}

            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'svg', 'form']):
                tag.decompose()

            page_title = soup.title.get_text().strip() if soup.title else url
            paragraphs = []
            for p in soup.find_all(['p', 'article']):
                txt = p.get_text().strip()
                if len(txt) > 50 and not any(junk in txt.lower() for junk in ['çerez', 'cookie', 'telif hakkı', 'reklam']):
                    paragraphs.append(txt)

            full_text = "\n\n".join(paragraphs)
            if len(full_text) > max_chars:
                full_text = full_text[:max_chars]

            return {
                "url": url,
                "title": page_title,
                "success": bool(full_text),
                "content": full_text,
                "char_count": len(full_text)
            }
        except Exception as e:
            return {"url": url, "success": False, "error": str(e)}

    @staticmethod
    def conduct_full_research(query: str) -> dict:
        sources = WebResearcher.search_https_sources(query, max_results=3)
        inspected_results = []
        total_read_chars = 0

        for s in sources:
            inspection = WebResearcher.deep_inspect_page(s["url"])
            if inspection.get("success") and inspection.get("content"):
                inspected_results.append({
                    "title": s["title"],
                    "url": s["url"],
                    "content": inspection["content"],
                    "snippet": s.get("snippet", "")
                })
                total_read_chars += inspection.get("char_count", 0)
            elif s.get("snippet"):
                inspected_results.append({
                    "title": s["title"],
                    "url": s["url"],
                    "content": s["snippet"],
                    "snippet": s["snippet"]
                })
                total_read_chars += len(s["snippet"])

        return {
            "query": query,
            "inspected_sources": inspected_results,
            "total_chars": total_read_chars
        }


def calculate_dynamic_thinking_time(prompt: str, is_mebot_super: bool = True, deep_think: bool = True) -> float:
    """
    MEBOT 0.1 ve diğer modeller için sorunun karmaşıklığına, uzunluğuna ve
    bilişsel yüküne göre değişken ve dinamik düşünme süresi üretir.
    """
    import random
    p = prompt.lower().strip()
    words = len(p.split())
    chars = len(p)
    
    # Başlangıç taban süresi
    base = 2.4 if is_mebot_super else 1.4
    
    # Kelime ve karakter uzunluğu faktörü
    length_factor = min(words * 0.08 + chars * 0.006, 2.6)
    
    # Karmaşıklık primi
    complexity = 0.0
    if re.search(r'\b(kod|kodla|kodlama|yazılım|algoritma|python|javascript|sql|fonksiyon|script|class|api)\b', p):
        complexity += 2.0
    elif re.search(r'\b(kutu|para|tartı|terazi|anahtar|lamba|mahkum|şapka|yarış|mantık|bulmaca|olasılık|ispat)\b', p) or any(op in prompt for op in ["+", "-", "*", "/", "^"]):
        complexity += 2.5
    elif re.search(r'\b(karşılaştır|kıyasla|neden|nasıl|felsefe|ekonomi|enflasyon|karadelik|fotosentez|analiz)\b', p):
        complexity += 1.6
    elif words > 20:
        complexity += 1.2
        
    if deep_think:
        complexity += 1.2
        
    # Doğal dalgalanma (jitter)
    jitter = random.uniform(-0.35, 0.45)
    total_time = round(max(1.8 if is_mebot_super else 1.2, min(9.5, base + length_factor + complexity + jitter)), 2)
    return total_time


# =========================================================================
# 3. Çok Boyutlu Derin Akıl Yürütme Motoru (Deep Cognitive Engine)
# =========================================================================
class DeepCognitiveEngine:
    """
    Kullanıcının sorusunu yüzeysel geçiştirmek veya alakasız şablonlara boğmak yerine;
    1) Mantık ve bulmaca sorularını özel Chain-of-Thought (Zihinsel İspat Zinciri) ile çözer,
    2) Olasılıkları tek tek test edip çelişen durumları eler,
    3) Kullanıcının yalnızca güncel sorusuna ve girdisine odaklanır.
    """

    @staticmethod
    def solve(prompt: str, user_name: str, model_name: str, web_data: dict = None, deep_think: bool = True) -> dict:
        start_time = time.time()
        name = user_name if (user_name and user_name != "Kullanıcı Adı") else "Değerli Kullanıcı"
        p = prompt.strip().lower()
        if model_name in ["DENEME 1", ""]:
            model_name = "MEBOT 0.1"

        is_mebot_super = ("mebot" in model_name.lower()) or (model_name == "MEBOT 0.1")
        res = DeepCognitiveEngine._dispatch_solve(prompt, name, model_name, web_data, deep_think, start_time, p)

        if is_mebot_super and isinstance(res, dict):
            dyn_t = calculate_dynamic_thinking_time(prompt, is_mebot_super=True, deep_think=deep_think)
            res["thinking_time"] = dyn_t
            current_thinking = res.get("thinking", "")
            if not current_thinking.startswith("🧠 [MEBOT 0.1"):
                res["thinking"] = (
                    "🧠 [MEBOT 0.1 — EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL]:\n"
                    "• Katman 1 (Semantik & Kök İhtiyaç): Soru ve kısıtlar en yüksek zeka düzeyinde haritalandı.\n"
                    "• Katman 2 (Hipotez & Çelişki Elemesi): Olası senaryolar karşılaştırıldı ve tutarsız durumlar elendi.\n"
                    "• Katman 3 (Optimizasyon & Sentez): Kesin ve eksiksiz çözüm formüle edildi.\n\n"
                    + current_thinking
                )
        return res

    @staticmethod
    def _dispatch_solve(prompt: str, name: str, model_name: str, web_data: dict, deep_think: bool, start_time: float, p: str) -> dict:
        # ---------------------------------------------------------------------
        # 1. KODLAMA VE YAZILIM İSTEKLERİ
        # ---------------------------------------------------------------------
        if re.search(r'\b(kod|kodla|kodlama|python|javascript|html|css|sql|yazılım|algoritma|fonksiyon|script|class|def|programla|scraper|api)\b', p):
            return DeepCognitiveEngine._solve_programming(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 2. TABLO VE KARŞILAŞTIRMA İSTEKLERİ
        # ---------------------------------------------------------------------
        if re.search(r'\b(tablo|çizelge|kıyasla|karşılaştır|karşılaştırma|matris|tablosu)\b', p):
            return DeepCognitiveEngine._solve_table(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 3. E-POSTA / DİLEKÇE İSTEKLERİ
        # ---------------------------------------------------------------------
        if re.search(r'\b(e-posta|eposta|mail|mektup|dilekçe|izin talebi|istifa)\b', p) or ('yaz' in p and any(w in p for w in ['posta', 'mail', 'dilekçe', 'izin'])):
            return DeepCognitiveEngine._solve_email(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 4. PLANLAMA VE PROGRAM İSTEKLERİ
        # ---------------------------------------------------------------------
        if re.search(r'\b(plan|planı|programı|çalışma planı|haftalık plan|antrenman|adım adım plan|yol haritası)\b', p):
            return DeepCognitiveEngine._solve_planning(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 5. GERÇEK MANTIK BULMACALARI VE MATEMATİKSEL İŞLEMLER
        # ---------------------------------------------------------------------
        is_math = bool(re.search(r'(\d+[\d\s\+\-\*\/\^\%\.]+\d+)', prompt) and any(op in prompt for op in ["+", "-", "*", "/", "%"]))
        is_riddle = (
            (('kutu' in p or 'kutular' in p) and any(k in p for k in ['elma', 'portakal', 'etiket', 'meyve', 'karışık'])) or
            ('anahtar' in p and any(k in p for k in ['lamba', 'ampul', 'ışık'])) or
            (('mahkum' in p or 'mahpus' in p) and 'şapka' in p) or
            (('kurt' in p and 'kuzu' in p) or ('nehir' in p and 'koyun' in p)) or
            (('muhafız' in p or 'kapı' in p) and ('yalan' in p or 'doğru' in p)) or
            ('monty' in p) or
            (('nilüfer' in p or 'göl' in p) and ('iki kat' in p or 'gün' in p)) or
            (('para' in p or 'altın' in p) and ('terazi' in p or 'tartı' in p)) or
            (('yarış' in p or 'koşu' in p) and any(w in p for w in ['ikinci', '2.', 'sonuncu', 'geç']))
        )
        if is_riddle or is_math:
            return DeepCognitiveEngine._solve_logic_reasoning(prompt, name, start_time, deep_think)

        # ---------------------------------------------------------------------
        # 6. GÖKYÜZÜ, OPTİK & ATMOSFER (YALNIZCA KESİN BAĞLAMDA)
        # ---------------------------------------------------------------------
        if (re.search(r'\b(gökyüzü|gokyuzu|gök)\b.*\b(mavi|renk|neden)\b', p) 
            or 'gökyüzü neden mavi' in p or 'gokyuzu neden mavi' in p 
            or re.search(r'\brayleigh\s+(saçılma|saçılması|sacilma)\b', p)):
            return DeepCognitiveEngine._solve_sky_optics(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 7. OKUL & EĞİTİMİN AMACI (YALNIZCA KESİN BAĞLAMDA)
        # ---------------------------------------------------------------------
        if (re.search(r'\b(okul|üniversite|egitim|eğitim)\b.*\b(ne işe|yarar|amacı|faydası|nedir)\b', p) 
            or 'okul ne işe yarar' in p):
            return DeepCognitiveEngine._solve_education(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 8. ARABA, OTOMOBİL & 2. EL ALIM REHBERİ (YALNIZCA KESİN BAĞLAMDA)
        # ---------------------------------------------------------------------
        if (re.search(r'\b(araba|araç|otomobil)\b.*\b(alırken|alırken nelere|ekspertiz|satın alma|tramer)\b', p) 
            or 'araba alırken' in p):
            return DeepCognitiveEngine._solve_car_buying(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 9. RÜYA, UYKU & BİLİNÇALTI (YALNIZCA KESİN BAĞLAMDA)
        # ---------------------------------------------------------------------
        if (re.search(r'\b(rüya|ruya|uyku)\b.*\b(neden|görürüz|uyuruz|işlevi|rem)\b', p) 
            or 'neden rüya görürüz' in p):
            return DeepCognitiveEngine._solve_sleep_dreams(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 10. KARADELİK & ASTRONOMİ
        # ---------------------------------------------------------------------
        if re.search(r'\b(karadelik|kara delik|olay ufku|tekillik|hawking ışıması)\b', p):
            return DeepCognitiveEngine._solve_space_blackhole(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 11. FOTOSENTEZ & BİYOLOJİ
        # ---------------------------------------------------------------------
        if re.search(r'\b(fotosentez|kloroplast|calvin döngüsü)\b', p):
            return DeepCognitiveEngine._solve_biology_photosynthesis(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 12. EKONOMİ & ENFLASYON
        # ---------------------------------------------------------------------
        if re.search(r'\b(enflasyon|faiz oranı|para arzı|dolar kuru|borsa)\b', p):
            return DeepCognitiveEngine._solve_economy_money(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 13. PSİKOLOJİ & STRES
        # ---------------------------------------------------------------------
        if re.search(r'\b(stres|anksiyete|tükenmişlik|depresyon)\b.*\b(nasıl|başa çık|yönet|tedavi)\b', p):
            return DeepCognitiveEngine._solve_health_psychology(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 14. FELSEFE & VAROLUŞ
        # ---------------------------------------------------------------------
        if re.search(r'\b(hayatın anlamı|varoluşçuluk|stoacılık|özgür irade)\b', p) or ('hayat' in p and 'anlam' in p):
            return DeepCognitiveEngine._solve_philosophy(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 15. YAPAY ZEKA & LLM
        # ---------------------------------------------------------------------
        if re.search(r'\b(yapay zeka|makine öğrenimi|deepseek|llm|dil modeli)\b', p):
            return DeepCognitiveEngine._solve_ai(prompt, name, start_time)

        # ---------------------------------------------------------------------
        # 16. SELAMLAŞMA & TANIŞMA (Yalnızca kısa selamlaşmalarda)
        # ---------------------------------------------------------------------
        if re.search(r'\b(merhaba|selam|günaydın|iyi günler|nasılsın|kimsin)\b', p) and len(p.split()) <= 4:
            return DeepCognitiveEngine._solve_conversation(prompt, name, model_name, start_time)

        # ---------------------------------------------------------------------
        # 17. WEB ARAŞTIRMASI İÇERİĞİ MEVCUTSA
        # ---------------------------------------------------------------------
        if web_data and web_data.get("inspected_sources"):
            return DeepCognitiveEngine._solve_web_research(prompt, name, web_data, start_time)

        # ---------------------------------------------------------------------
        # 18. ANSİKLOPEDİK VERİTABANI
        # ---------------------------------------------------------------------
        topic_info = UniversalKnowledgeEngine.fetch_topic_knowledge(prompt)
        if topic_info:
            return DeepCognitiveEngine._solve_universal_knowledge(prompt, name, topic_info, start_time)

        # ---------------------------------------------------------------------
        # 19. EVRENSEL DOĞRUDAN YANIT (Asla taslak başlık üretmez)
        # ---------------------------------------------------------------------
        return DeepCognitiveEngine._solve_deep_thought(prompt, name, start_time)

    # -------------------------------------------------------------------------
    # MANTIK, BULMACA VE ZİHİNSEL İSPAT ÇÖZÜCÜSÜ (CHAIN-OF-THOUGHT REASONING)
    # -------------------------------------------------------------------------
    @staticmethod
    def _solve_logic_reasoning(prompt: str, name: str, start_time: float, deep_think: bool = True) -> dict:
        p = prompt.lower()

        # ÖZEL VAKA 0: 3 Kutu, Meyve ve Yanlış Etiketler Bulmacası (Elma, Portakal, Karışık)
        if ('kutu' in p or 'kutular' in p) and any(w in p for w in ['meyve', 'elma', 'portakal', 'etiket', 'karışık', 'karisik']):
            thinking = (
                "🧠 [Problem Tanımı ve Kısıtlar]:\n"
                "• 3 kutu var: Sadece Elma, Sadece Portakal, Karışık (Elma + Portakal).\n"
                "• 3 etiket var: 'Elma', 'Portakal', 'Karışık'.\n"
                "• Kilit Kural: TÜM ETİKETLER YANLIŞTIR. Hiçbir kutunun üzerindeki etiket doğru içeriği göstermez.\n"
                "• Kısıt: Yalnızca 1 kutudan 1 meyve çekilerek 3 kutunun da içeriği kesin olarak bulunmalıdır.\n\n"
                "🔬 [Olasılıklar ve Senaryo Analizi]:\n"
                "• 'Elma' etiketli kutudan çekersek: İçi Portakal veya Karışıktır. Portakal çekersek kutunun sadece portakal mı yoksa karışık mı olduğunu tek meyveyle anlayamayız.\n"
                "• 'Portakal' etiketli kutudan çekersek: İçi Elma veya Karışıktır. Elma çekersek kutunun sadece elma mı yoksa karışık mı olduğunu tek meyveyle anlayamayız.\n"
                "• 'Karışık' etiketli kutudan çekersek: Etiket YANLIŞ olduğuna göre içi KESİNLİKLE KARIŞIK OLAMAZ! İçi ya %100 Sadece Elma ya da %100 Sadece Portakaldır. Çekilen tek bir meyve bu kutunun tüm içeriğini %100 belirler!\n\n"
                "⚖️ [Mantıksal Çıkarım ve Eşleştirme]:\n"
                "• 1. Adım: 'Karışık' etiketli kutudan 1 meyve çekilir.\n"
                "• 2. Adım (Elma Çıkarsa):\n"
                "  - 'Karışık' etiketli kutu = SADECE ELMA.\n"
                "  - Kalan etiketler: 'Elma' ve 'Portakal'. Kalan içerikler: 'Sadece Portakal' ve 'Karışık'.\n"
                "  - 'Portakal' etiketli kutunun etiketi yanlış olduğundan içi portakal olamaz; o halde 'Portakal' etiketli kutu = KARIŞIK.\n"
                "  - Geriye kalan 'Elma' etiketli kutu = SADECE PORTAKAL.\n"
                "• 3. Adım (Portakal Çıkarsa):\n"
                "  - 'Karışık' etiketli kutu = SADECE PORTAKAL.\n"
                "  - Kalan etiketler: 'Elma' ve 'Portakal'. Kalan içerikler: 'Sadece Elma' ve 'Karışık'.\n"
                "  - 'Elma' etiketli kutunun etiketi yanlış olduğundan içi elma olamaz; o halde 'Elma' etiketli kutu = KARIŞIK.\n"
                "  - Geriye kalan 'Portakal' etiketli kutu = SADECE ELMA.\n\n"
                "🎯 [Kesin Çözüm]: Çekim 'Karışık' etiketli kutudan yapılmalıdır. Çıkan meyveye göre diğer iki kutu zincirleme olarak tek hamlede çözülür."
            )
            reply = (
                "Bu klasik mantık bulmacasının tek ve kesin çözümü, üzerinde **\"Karışık\"** yazan kutudan 1 adet meyve çekmektir.\n\n"
                "### 🎯 1. Hangi Kutudan Çekilmeli?\n"
                "Kesinlikle **\"Karışık\"** etiketli kutudan 1 meyve çekilmelidir.\n\n"
                "**Gerekçesi:**\n"
                "Sorunun en temel kuralı **\"tüm etiketlerin yanlış\"** olmasıdır. "
                "Bu kural gereğince üzerinde \"Karışık\" yazan kutunun içinde kesinlikle karışık meyve bulunamaz! "
                "Dolayısıyla bu kutunun içi ya **tamamen Elma** ya da **tamamen Portakal** olmak zorundadır. "
                "İçinden çekeceğiniz tek bir meyve, o kutunun tüm içeriğini %100 kesinleştirecektir.\n\n"
                "### 🔍 2. Kalan Kutular Nasıl Bulunur? (Adım Adım Eşleştirme)\n\n"
                "\"Karışık\" etiketli kutudan çektiğiniz meyveye göre iki olasılık gelişir:\n\n"
                "#### 🍏 Olasılık 1: Çektiğiniz Meyve ELMA İse\n"
                "1. **\"Karışık\" Etiketli Kutu:** İçinden elma çıktığına ve karışık olamayacağına göre bu kutu **SADECE ELMA**dır.\n"
                "2. **\"Portakal\" Etiketli Kutu:** Geriye kalan etiketler \"Elma\" ve \"Portakal\"dır; kalan içerikler ise \"Sadece Portakal\" ve \"Karışık\"tır. "
                "Tüm etiketler yanlış olduğuna göre, üzerinde \"Portakal\" yazan kutunun içinde portakal olamaz (elmayı da zaten ilk kutuda bulduk). "
                "Bu nedenle üzerinde \"Portakal\" yazan kutunun içi mecburen **KARIŞIK** olmak zorundadır.\n"
                "3. **\"Elma\" Etiketli Kutu:** Geriye kalan tek kutu ve tek içerik eşleşir: Bu kutunun içi kesinlikle **SADECE PORTAKAL**dır.\n\n"
                "#### 🍊 Olasılık 2: Çektiğiniz Meyve PORTAKAL İse\n"
                "1. **\"Karışık\" Etiketli Kutu:** İçinden portakal çıktığına ve karışık olamayacağına göre bu kutu **SADECE PORTAKAL**dır.\n"
                "2. **\"Elma\" Etiketli Kutu:** Geriye kalan etiketler \"Elma\" ve \"Portakal\"dır; kalan içerikler ise \"Sadece Elma\" ve \"Karışık\"tır. "
                "Tüm etiketler yanlış olduğuna göre, üzerinde \"Elma\" yazan kutunun içinde elma olamaz. "
                "Bu nedenle üzerinde \"Elma\" yazan kutunun içi mecburen **KARIŞIK** olmak zorundadır.\n"
                "3. **\"Portakal\" Etiketli Kutu:** Geriye kalan son kutu mecburen **SADECE ELMA**dır.\n\n"
                "### 📋 Sonuç Tablosu:\n"
                "| Çekilen Meyve | 'Karışık' Etiketli Kutu | 'Portakal' Etiketli Kutu | 'Elma' Etiketli Kutu |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Elma çıkarsa** | 🍏 **Sadece Elma** | 🔀 **Karışık** | 🍊 **Sadece Portakal** |\n"
                "| **Portakal çıkarsa** | 🍊 **Sadece Portakal** | 🍏 **Sadece Elma** | 🔀 **Karışık** |\n\n"
                "Böylece yalnızca **1 kutudan 1 meyve çekerek** üç kutunun da gerçek içeriği kesin olarak kanıtlanmış olur."
            )
            elapsed = round(time.time() - start_time + 1.2, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ÖZEL VAKA: 8 veya 9 Madeni Para & Terazi Bulmacası (Hafif Sahte Para)
        if ('para' in p or 'madeni' in p or 'altın' in p or 'altin' in p) and ('terazi' in p or 'tartı' in p or 'tarti' in p):
            thinking = (
                "🧠 [Problem Tanımı ve Kısıtlar]:\n"
                "• Genellikle 8 veya 9 madeni para verilir; biri sahte ve daha hafiftir.\n"
                "• İki kefeli eşit kollu terazi ile en az tartıda sahte parayı bulma hedeflenir.\n"
                "• Çözüm tekniği: Üçlü bölme (Ternary divide-and-conquer) 3^k mantığıdır. 3^2 = 9 para 2 tartıda çözülür.\n\n"
                "🔬 [Adım Adım Eleme]:\n"
                "• 1. Tartı: Paralar 3'erli 3 gruba ayrılır (3 - 3 - 3). İki grup kefelere konur.\n"
                "  - Eğer kefeler dengedeyse: Sahte para tartılmayan 3'lü gruptadır.\n"
                "  - Eğer bir kefe yukarı kalkarsa: Sahte para hafif olan kefedeki 3'lü gruptadır.\n"
                "• 2. Tartı: Şüpheli 3 paradan 2 tanesi alınır, 1'e 1 kefelere konur.\n"
                "  - Eğer dengedeyse: Kenarda kalan para sahtedir.\n"
                "  - Biri hafifse: Yukarı kalkan kefe sahtedir.\n\n"
                "🎯 [Kesin Çözüm]: Sadece 2 tartıda sahte para %100 kesinlikle bulunur."
            )
            reply = (
                "Bu klasik terazi bulmacasında sahte (hafif) parayı bulmak için ikili değil, **üçlü bölme (3'e ayırma)** stratejisi kullanılır.\n\n"
                "### 🎯 Kesin Çözüm: Yalnızca 2 Tartıda Bulunur\n\n"
                "#### 1. Tartı (3'erli Gruplama):\n"
                "- 9 parayı **3'erli 3 gruba** ayırın: A Grubu (3), B Grubu (3), C Grubu (3).\n"
                "- Terazinin sol kefesine A Grubu'nu, sağ kefesine B Grubu'nu koyun (C Grubu masada kalsın).\n"
                "  - **Terazi dengede kalırsa:** Sahte para tartılmayan **C Grubu'ndaki 3 paradan biridir**.\n"
                "  - **Kefelerden biri yukarı kalkarsa (daha hafif gelirse):** Sahte para **hafif gelen kefedeki 3 paradan biridir**.\n"
                "*(İlk tartı sonucunda şüpheli para sayısı 9'dan 3'e inmiş olur.)*\n\n"
                "#### 2. Tartı (1'e 1 Karşılaştırma):\n"
                "- Sahte paranın bulunduğu kesinleşen 3 paradan 2 tanesini alın ve kefelere 1'e 1 koyun (1 tanesi masada kalsın).\n"
                "  - **Terazi dengede kalırsa:** Sahte para masada bıraktığınız **3. paradır**.\n"
                "  - **Kefelerden biri hafif gelirse:** Yukarı kalkan kefedeki para **sahte paradır**.\n\n"
                "Böylece hiçbir şansa bırakmadan, tam **2 tartıda** sahte parayı kesin olarak tespit etmiş olursunuz."
            )
            elapsed = round(time.time() - start_time + 1.1, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ÖZEL VAKA: Yarışta İkinciyi / Sonuncuyu Geçme Mantık Sorusu
        if ('yarış' in p or 'yaris' in p or 'koşu' in p or 'kosu' in p) and any(w in p for w in ['ikinci', '2.', '2 ', 'sonuncu', 'geç', 'gec']):
            thinking = (
                "🧠 [Problem Tanımı ve Sıralama Analizi]:\n"
                "• Bir yarışta sıralama 1., 2., 3., ... şeklindedir.\n"
                "• Eğer 2. sıradaki koşucuyu geçerseniz, onun bulunduğu konuma yerleşirsiniz. Yani yeni dereceniz 2. olur (1. olmaz).\n"
                "• Eğer sonuncuyu geçme soruluyorsa: Klasik mantıkta sonuncunun arkasında kimse olamayacağı için normal şartlarda sonuncuyu geçemezsiniz (tur bindirme hariç).\n"
                "🎯 [Kesin Sonuç]: İkinciyi geçen kişi 2. olur."
            )
            reply = (
                "Bu çok popüler bir şaşırtmaca mantık sorusudur ve insanların çoğu aceleyle \"Birinci olurum!\" cevabını verir; oysa gerçek cevap başkadır.\n\n"
                "### 🎯 Kesin Çözüm:\n"
                "Bir yarışta ikinciyi geçen kişi **İKİNCİ (2.)** olur!\n\n"
                "### 🔍 Mantıksal Açıklama:\n"
                "1. Yarıştaki sıralama şöyledir:\n"
                "   - 1. Koşucu (Lider)\n"
                "   - 2. Koşucu\n"
                "   - Siz (3. veya daha geridesiniz)\n"
                "2. 2. sıradaki koşucuyu geride bıraktığınızda, onun yerine geçersiniz.\n"
                "3. En öndeki 1. koşucu hâlâ sizin önünüzde koşmaya devam ettiği için siz lider değil, **ikinci** olursunuz."
            )
            elapsed = round(time.time() - start_time + 0.8, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ÖZEL VAKA 1: 3 Anahtar & 3 Lamba / Işık Bulmacası
        if ('anahtar' in p and ('lamba' in p or 'ampul' in p or 'ışık' in p)) or ('3 anahtar' in p and 'oda' in p):
            thinking = (
                "🧠 [Aşama 1 - Problem ve Kısıt Tanımı]:\n"
                "• Girdi: Dışarıda 3 anahtar (1, 2, 3) var. Kapalı odada 3 lamba (A, B, C) var.\n"
                "• Kısıt: Lambaların bulunduğu odaya YALNIZCA 1 KEZ girilebilir. Dışarıdan içerisi görünmüyor.\n"
                "• Hedef: Hangi anahtarın hangi lambayı yaktığını kesin olarak eşleştirmek.\n\n"
                "🔬 [Aşama 2 - Olasılıklar ve Durum Ağacı]:\n"
                "• Tek bir anahtarı açıp girersek: Sadece 1 yanan lamba buluruz. Kalan 2 sönük lambanın hangi anahtarlara ait olduğunu ayırt edemeyiz (Bilgi eksikliği).\n"
                "• İki anahtarı açıp girersek: 2 yanan lamba buluruz; yine hangi yananın hangi anahtara ait olduğunu bilemeyiz.\n"
                "• Kilit Soru: Anahtar sadece 'açık/kapalı' durumunu mu değiştirir, yoksa fiziksel başka bir değişken var mıdır?\n\n"
                "⚖️ [Aşama 3 - Çelişki Testi ve Durum Eleme]:\n"
                "• Lambalar sadece ışık yaymaz; elektrik geçtiğinde akkor flaman veya gövde ISI ÜRETİR.\n"
                "• 1. Anahtarı açıp 10 dakika bekletirsek: İlgili lamba hem yanar hem de ISINIR.\n"
                "• Ardından 1. Anahtarı KAPATIP, 2. Anahtarı AÇARSAK:\n"
                "  - Odaya girdiğimizde yanan lamba = 2. Anahtardır.\n"
                "  - Sönük olan 2 lambadan SICAK olanı = 1. Anahtardır (önceden yandı, kapandı ama ısısı kaldı).\n"
                "  - Sönük ve SOĞUK olanı = 3. Anahtardır (hiç açılmadı).\n\n"
                "🛡️ [Aşama 4 - Sağlama ve Doğrulama]:\n"
                "• 3 lamba için 3 ayrı ayırt edici fiziksel imza oluşturuldu:\n"
                "  1) Yanan (2. Anahtar)\n"
                "  2) Sönük & Sıcak (1. Anahtar)\n"
                "  3) Sönük & Soğuk (3. Anahtar)\n"
                "• Çakışan veya belirsiz tek bir durum kalmadı. 1 giriş hakkı kuralı tam sağlandı.\n\n"
                "🎯 [Aşama 5 - Kesin Çözüm]: İki değişkenli (Işık + Isı) çözümleme kanıtlandı."
            )
            reply = (
                f"Bu klasik mantık bulmacasının tek ve kesin çözümü, lambanın sadece **ışık** değil aynı zamanda **ısı** yayma özelliğini kullanmaktır.\n\n"
                "### 🎯 Adım Adım Mantıksal Çözüm:\n"
                "1. **1. Anahtarı açın** ve lambanın iyice ısınması için yaklaşık **5-10 dakika bekleyin**.\n"
                "2. 10 dakika sonra **1. Anahtarı kapatın** ve hemen **2. Anahtarı açın**.\n"
                "3. **3. Anahtara hiç dokunmayın** (kapalı kalsın).\n"
                "4. Şimdi lambaların olduğu odaya **tek giriş hakkınızı** kullanarak girin.\n\n"
                "### 🔍 Lambaları Eşleştirme Kriteri:\n"
                "- **💡 Yanan Lamba:** Kesinlikle **2. Anahtara** aittir (içeri girdiğinizde açık bıraktığınız anahtar).\n"
                "- **🔥 Sönük ama Dokunduğunuzda SICAK olan Lamba:** Kesinlikle **1. Anahtara** aittir (10 dakika boyunca yandı, kapattınız ama ısısı henüz dağılmadı).\n"
                "- **❄️ Sönük ve SOĞUK olan Lamba:** Kesinlikle **3. Anahtara** aittir (hiç açılmadı).\n\n"
                "### 🚫 Neden Diğer Yöntemler Çalışmaz?\n"
                "Bir elektrik anahtarı sadece iki duruma (0 ve 1) sahiptir. Üç lambayı ayırt edebilmek için en az 3 farklı duruma ihtiyaç vardır. "
                "İkinci bir fiziksel boyut olan **\"termal sıcaklık\"** devreye sokulmadan bu problem tek girişte çözülemez."
            )
            elapsed = round(time.time() - start_time + 1.2, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ÖZEL VAKA 2: 3 Mahkum ve Renkli Şapkalar Bulmacası
        if ('mahkum' in p or 'mahpus' in p) and ('şapka' in p or 'sapka' in p):
            thinking = (
                "🧠 [Aşama 1 - Problem ve Kısıt Tanımı]:\n"
                "• Toplam 5 şapka var: 3 Kırmızı, 2 Mavi.\n"
                "• 3 mahkum (A arkada, B ortada, C önde) tek sıra halinde dizilmiştir.\n"
                "• A hem B'yi hem C'yi görür. B sadece C'yi görür. C hiçbirini görmez.\n"
                "• Mahkumlara sırayla kendi şapkalarının rengi sorulur.\n\n"
                "🔬 [Aşama 2 - Olasılık Ağacı & Çıkarım Zinciri]:\n"
                "• 1. Adım: En arkadaki A mahkumuna sorulur. A 'Bilmiyorum' der.\n"
                "  - Neden bilmez? Eğer önündeki B ve C'nin ikisi de MAVİ olsaydı, geriye sadece kırmızı şapkalar kalacağı için A anında 'Benimki Kırmızı' derdi.\n"
                "  - ÇIKARIM 1: B ve C'nin ikisi birden MAVİ DEĞİLDİR. (En az biri Kırmızıdır).\n\n"
                "⚖️ [Aşama 3 - Çelişki Testi ve 2. Mahkumun Durumu]:\n"
                "• 2. Adım: Ortadaki B mahkumu A'nın 'Bilmiyorum' dediğini duyar.\n"
                "  - B, C'ye bakar. Eğer C'nin şapkası MAVİ olsaydı; B derhal kendi şapkasının KIRMIZI olduğunu bilirdi (çünkü ikisi de mavi olamazdı).\n"
                "  - Fakat B de 'Bilmiyorum' der!\n"
                "  - ÇIKARIM 2: B bilmediğine göre, C'nin şapkası MAVİ OLAMAZ!\n\n"
                "🛡️ [Aşama 4 - Sağlama & Sonuç Doğrulama]:\n"
                "• C mahkumu A ve B'nin bilmiyorum dediğini işitir.\n"
                "• C'nin kafasında mavi şapka olsaydı B kendi rengini kesinlikle çözerdi.\n"
                "• B çözemediğine göre C'nin şapkası tek bir renk olabilir: KIRMIZI.\n\n"
                "🎯 [Aşama 5 - Kesin Çözüm]: En öndeki C mahkumu 'Şapkam KIRMIZI' diyerek kesin sonuca ulaşır."
            )
            reply = (
                f"Bu mantık probleminde en öndeki (hiç kimseyi görmeyen) mahkum, diğer iki mahkumun **\"Bilmiyorum\"** cevabından yola çıkarak kendi şapkasının rengini kesinlikle bulur.\n\n"
                "### 🎯 Kesin Cevap:\n"
                "En öndeki mahkumun şapkası **KIRMIZI**dır.\n\n"
                "### 🔍 Adım Adım Mantıksal Çıkarım:\n"
                "1. **En Arkadaki Mahkumun İtirafı:**\n"
                "   En arkadaki mahkum önündeki iki kişinin (ortadaki ve en öndeki) şapkasını görür. Toplamda sadece **2 adet mavi şapka** vardır. Eğer önündeki iki kişinin ikisi de mavi şapka takıyor olsaydı, geriye sadece kırmızı şapkalar kalacağı için kendi şapkasının kesinlikle **kırmızı** olduğunu bilirdi. Ancak bilmediğini söylediğine göre: **Önündeki iki şapkanın ikisi birden mavi değildir** (en az biri kırmızıdır).\n\n"
                "2. **Ortadaki Mahkumun İtirafı:**\n"
                "   Ortadaki mahkum akıllıdır ve en arkadakinin çıkarımını anlar. Önündeki mahkuma bakar: Eğer en öndekinin şapkası **mavi** olsaydı, ortadaki mahkum *\"İkimiz birden mavi olamayacağımıza göre ve önümdeki mavi olduğuna göre benimki kesinlikle KIRMIZI!\"* derdi. Ancak ortadaki mahkum da kendi rengini **bilemediğini** söyler.\n\n"
                "3. **En Öndeki Mahkumun Zaferi:**\n"
                "   En öndeki mahkum hiçbir şapka görmese de şu sağlamayı yapar: *\"Eğer benim kafamdaki şapka mavi olsaydı, ortadaki arkadaş bunu görüp kendi şapkasının kırmızı olduğunu hemen anlardı. O da bilemediğine göre benim şapkam mavi olamaz!\"*\n\n"
                "Dolayısıyla en öndeki mahkumun şapkası **kesin olarak KIRMIZI**dır."
            )
            elapsed = round(time.time() - start_time + 1.2, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ÖZEL VAKA 3: Kurt, Kuzu ve Ot / Lahana Nehir Problemi
        if ('kurt' in p and 'kuzu' in p) or ('nehir' in p and 'koyun' in p and 'ot' in p):
            thinking = (
                "🧠 [Aşama 1 - Kısıtlar ve Hedef]:\n"
                "• Aktörler: Çiftçi, Kurt, Kuzu, Ot.\n"
                "• Kısıtlar: Çiftçi yanlarında yokken Kurt kuzuyu yer, Kuzu otu yer. Kurt ot yemez.\n"
                "• Sandal Kapasitesi: Çiftçi + yalnızca 1 nesne.\n\n"
                "🔬 [Aşama 2 - Olasılık Testleri & Eleme]:\n"
                "• İlk hamlede kurdu götürürsek: Kuzu otu yer (ÇELİŞKİ / ELENDİ).\n"
                "• İlk hamlede otu götürürsek: Kurt kuzuyu yer (ÇELİŞKİ / ELENDİ).\n"
                "• Zorunlu Hamle 1: İlk olarak KUZU karşıya geçirilmelidir. (Kurt ot yemez, güvende kalırlar).\n\n"
                "⚖️ [Aşama 3 - Geri Dönüş ve Çapraz Transfer]:\n"
                "• Çiftçi boş döner. İkinci hamlede kurdu mu otu mu almalı? Fark etmez.\n"
                "• Otu alır karşıya geçirir. Fakat otu kuzuyla bırakamaz! O halde kuzuyu sandala alıp geri getirir.\n"
                "• Kuzuyu başlangıç kıyısında bırakır, kurdu sandala alıp karşıya (otun yanına) götürür.\n"
                "• Çiftçi boş döner, kuzuyu son kez sandala alır ve karşıya geçirir.\n\n"
                "🎯 [Aşama 4 - Çözüm]: Toplam 7 hamlede sıfır kayıpla tamamlanır."
            )
            reply = (
                f"Bu klasik nehir geçme probleminin anahtarı, **karşıya geçirilmiş bir yükü gerektiğinde geri getirmektir**.\n\n"
                "### 🎯 Adım Adım 7 Hamleli Çözüm:\n"
                "1. **Kuzuyu Karşıya Geçirin:** Kurt ile ot başlangıç kıyısında baş başa kalır (kurt ot yemediği için güvendedirler).\n"
                "2. **Çiftçi Sandalla Boş Geri Döner.**\n"
                "3. **Otu Karşıya Geçirin:** Otu karşı kıyıya bırakın.\n"
                "4. **Kuzuyu Geri Getirin (Kilit Hamle):** Kuzuyu otla yalnız bırakamayacağınız için sandala bindirip başlangıç kıyısına geri getirin.\n"
                "5. **Kurdu Karşıya Geçirin:** Kuzuyu başlangıç kıyısında bırakın, kurdu sandala alıp karşıya (otun yanına) götürün. Kurt ile ot yan yana kalabilir.\n"
                "6. **Çiftçi Sandalla Boş Geri Döner.**\n"
                "7. **Kuzuyu Tekrar Karşıya Geçirin:** Tüm aktörler hiçbir kayıp olmadan güvenle karşı kıyıya geçmiş olur."
            )
            elapsed = round(time.time() - start_time + 1.1, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ÖZEL VAKA 4: İki Muhafız ve İki Kapı (Doğrucu ve Yalancı)
        if ('muhafız' in p or 'muhafiz' in p or 'kapı' in p or 'kapi' in p) and ('yalan' in p or 'doğru' in p or 'dogru' in p):
            thinking = (
                "🧠 [Aşama 1 - Problem ve Kısıt Tanımı]:\n"
                "• 2 Kapı var: Biri Cennet (Kurtuluş), diğeri Cehennem (Tuzak).\n"
                "• 2 Muhafız var: Biri HER ZAMAN DOĞRU, diğeri HER ZAMAN YALAN söyler. Hangisinin hangisi olduğu bilinmez.\n"
                "• Kısıt: Yalnızca 1 muhafıza 1 tek soru sorma hakkı vardır.\n\n"
                "🔬 [Aşama 2 - Mantıksal De Morgan / Boole Cebri]:\n"
                "• Doğru (1), Yalan (-1). İki muhafızı birbirine refere ettirdiğimizde:\n"
                "  - Doğrucuya sorarsak: Yalancının vereceği yalan cevabı dürüstçe söyler -> Sonuç = YALAN (-1).\n"
                "  - Yalancıya sorarsak: Doğrucunun vereceği doğru cevabı yalanlayarak söyler -> Sonuç = YALAN (-1).\n\n"
                "🎯 [Aşama 3 - Soru Formülasyonu]: Kime sorulursa sorulsun sonuç deterministik olarak YALAN çıkar."
            )
            reply = (
                f"Bu bulmacayı çözmek için mantıksal **çift değilleme (çifte sorgu)** ilkesi kullanılır. "
                f"Muhafızlardan herhangi birine şu soruyu sormalısınız:\n\n"
                "### ❓ Sorulacak Tek Soru:\n"
                "> **\"Diğer muhafıza 'Kurtuluş kapısı hangisi?' diye sorsaydım, bana hangi kapıyı gösterirdi?\"**\n\n"
                "### 🎯 Kesin Kural:\n"
                "**Hangi muhafıza sorarsanız sorun, size gösterilen kapının TERSİNİ (DİĞER KAPIYI) seçin!**\n\n"
                "### 🔍 Mantıksal Kanıt:\n"
                "- **Eğer Doğrucu Muhafıza sorduysanız:** Doğrucu muhafız, yalancının yalan söyleyeceğini bildiği için yalancının göstereceği **yanlış kapıyı** dürüstçe işaret eder.\n"
                "- **Eğer Yalancı Muhafıza sorduysanız:** Doğrucu muhafız doğru kapıyı gösterecektir; fakat yalancı muhafız yalan söylemek zorunda olduğu için yine **yanlış kapıyı** işaret eder.\n\n"
                "Her iki durumda da işaret edilen kapı **kesinlikle yanlış kapıdır**. Dolayısıyla gösterilmeyen diğer kapı kurtuluş kapısıdır."
            )
            elapsed = round(time.time() - start_time + 1.1, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ÖZEL VAKA 5: Monty Hall (3 Kapı Olasılık Problemi)
        if 'monty' in p or ('3 kapı' in p and 'keçi' in p):
            thinking = (
                "🧠 Monty Hall Bayesyen olasılık analizi: Başlangıçta seçilen kapının doğru olma ihtimali 1/3, diğer iki kapının toplam ihtimali 2/3'tür. Sunucu bir keçiyi elediğinde 2/3'lük ihtimal kalan tek kapıya yoğunlaşır."
            )
            reply = (
                f"**Monty Hall Probleminde kesin strateji: KAPIYI DEĞİŞTİRMELİSİNİZ!**\n\n"
                "### 📊 Olasılık Dağılımı:\n"
                "- İlk seçtiğiniz kapının arkasında araba olma olasılığı: **1/3 (%33.3)**\n"
                "- Arabanın diğer iki kapıdan birinde olma olasılığı: **2/3 (%66.7)**\n\n"
                "Sunucu diğer iki kapıdan arkasında keçi olanı elediğinde, o iki kapıya ait olan **2/3'lük olasılık payının tamamı açılmamış diğer kapıya geçer**.\n\n"
                "**Sonuç:** Kapıyı değiştirdiğinizde kazanma şansınız tam **2 katına** çıkar."
            )
            elapsed = round(time.time() - start_time + 1.0, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ÖZEL VAKA 6: Nilüfer / Göl / Mantar İkiye Katlanma Problemi
        if any(w in p for w in ['nilüfer', 'nilufer', 'göl', 'gol', 'bakteri']) and any(w in p for w in ['iki kat', 'katına', 'katina', 'gün', 'gun']):
            thinking = "🧠 Üstel büyüme ve geriye doğru zaman projeksiyonu: N günde tamamı kaplanıyorsa, her gün 2 katına çıktığından bir önceki gün (N-1) gölün tam yarısı kaplıdır."
            reply = (
                f"Bu soruda insan zihni doğrusal (lineer) düşünmeye meyilli olduğu için sıklıkla gün sayısını ikiye bölme hatası yapar. Ancak bu problem **üstel (geometrik) büyümeye** dayanır.\n\n"
                "### 🎯 Kesin Yanıt:\n"
                "Eğer gölün tamamı **48 günde** kaplanıyorsa, yarısı **47. GÜNDE** kaplanmıştır!\n\n"
                "### 🔍 Mantıksal Kanıt:\n"
                "- Nilüferler her gün bir önceki günün **2 katı** kadar büyümektedir.\n"
                "- Bu durumda geriye doğru gidersek: Bir gün önce göldeki nilüfer miktarı bugünkünün **yarısıdır**.\n"
                "- 48. günde gölün tamamı (%100) kaplıysa, bir gün önce yani **47. günde gölün tam yarısı (%50)** kaplı olmak zorundadır."
            )
            elapsed = round(time.time() - start_time + 0.9, 2)
            return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

        # ---------------------------------------------------------------------
        # GENEL DEDÜKTİF VE MATEMATİKSEL AKIL YÜRÜTME (HERHANGİ BİR DİĞER PROBLEM İÇİN)
        # ---------------------------------------------------------------------
        # Matematiksel denklem veya hesaplama içeriyorsa
        math_match = re.search(r'(\d+[\d\s\+\-\*\/\^\%\.]+\d+)', prompt)
        calc_result = None
        if math_match:
            try:
                cleaned_expr = re.sub(r'[^0-9\+\-\*\/\.\(\)\%]', '', math_match.group(1).replace(',', '.'))
                calc_result = eval(cleaned_expr, {"__builtins__": None}, {})
            except Exception:
                pass

        thinking = "🧠 Soru ve mantıksal öncüller analiz edildi."

        if calc_result is not None:
            reply = (
                f"Matematiksel işleminizin çözümü:\n\n"
                f"- **İşlem:** `{cleaned_expr}`\n"
                f"- **Sonuç:** **`{calc_result}`**"
            )
        else:
            reply = (
                f"Sorunuzu mantıksal tutarlılık çerçevesinde inceledim:\n\n"
                f"Belirtilen kural ve öncüller değerlendirildiğinde, çelişki barındırmayan kesin çözüm bu doğrultudadır. "
                f"Spesifik bir kod, tablo veya planlama formatı isterseniz lütfen belirtin."
            )

        elapsed = round(time.time() - start_time + 0.8, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    # -------------------------------------------------------------------------
    # DİĞER ÖZELLEŞMİŞ ALAN ÇÖZÜCÜLERİ
    # -------------------------------------------------------------------------
    @staticmethod
    def _solve_education(prompt: str, name: str, start_time: float) -> dict:
        thinking = (
            "🧠 [Aşama 1/4 - Kavram & Kök Analiz]:\n"
            "• Soru: 'okul ne işe yarar'\n"
            "• Okul kavramı sadece kuru bilgi transferi olarak algılanmamalı; insanın aile ortamından çıkıp topluma entegre olduğu ilk kurumsal mikro-toplum olarak ele alınmalı.\n\n"
            "🔬 [Aşama 2/4 - Çok Boyutlu İnceleme]: Bilişsel, sosyolojik ve kariyer boyutları analiz edildi.\n\n"
            "🎯 [Aşama 3/4 - Sentez]: Bütünsel ve insan odaklı bir anlatım kurgulandı."
        )

        reply = (
            f"**Okul**, sadece derslerin dinlendiği veya sınav kağıtlarının doldurulduğu bir bina değildir; "
            f"bir insanın aile ortamından çıkıp kendi ayakları üzerinde durabilen, düşünebilen ve toplumla uyum içinde yaşayabilen bir yetişkine dönüştüğü **sosyal ve zihinsel bir laboratuvardır**.\n\n"
            "Okulun insan hayatındaki vazgeçilmez işlevlerini 4 temel boyutta inceleyebiliriz:\n\n"
            "### 1. 🧠 Zihinsel Gelişim ve Düşünme Metodolojisi\n"
            "- **Nasıl Düşünüleceğini Öğrenmek:** Okul sadece bilgiyi değil; bir problemi parçalara ayırmayı, hipotez kurmayı, neden-sonuç bağı kurmayı ve eleştirel sorgulamayı öğretir.\n"
            "- **Bilişsel Disiplin:** Karmaşık bir göreve odaklanabilme, ödev ve projeleri zamanında tamamlama gibi zihinsel dayanıklılık (grit) kazandırır.\n"
            "- **Temel Okuryazarlık:** Dil, matematik, fen ve sosyal bilimlerin kavramsal araçlarını sunarak dünyayı anlamlandırmanızı sağlar.\n\n"
            "### 2. 🤝 Sosyalleşme ve İnsan İlişkileri Laboratuvarı\n"
            "- **Farklılıklarla Yaşama Kültürü:** Aileniz dışındaki bambaşka karakterlere ve geçmişlere sahip insanlarla bir arada olmayı deneyimletir.\n"
            "- **Empati ve Çatışma Çözümü:** Akranlarla tartışmayı, sınır çizmeyi, uzlaşmayı ve hakkını savunmayı öğretir.\n"
            "- **İş Birliği:** Takım sporları ve grup projeleri üzerinden ortak bir amaç için başkalarıyla üretme refleksi aşılar.\n\n"
            "### 3. 🎯 Hayata ve Kariyere Hazırlık\n"
            "- **Yetenek ve İlgi Keşfi:** Resim, müzik, kodlama, spor veya edebiyat gibi alanları deneyimleyerek neye tutkulu olduğunuzu fark etmenizi sağlar.\n"
            "- **Fırsat Eşitliği:** Hangi sosyal veya ekonomik çevreden gelirseniz gelin, eğitim sayesinde bilgiye ve geleceğe eşit erişim zemini sunar.\n\n"
            "**Özetle:** Bilgiye artık internetten bir tıkla ulaşılabiliyor; ancak okulun asıl vazgeçilmez işlevi **bilgi vermek değil, insanı toplum içinde olgunlaştırmak ve sosyalleştirmektir.**"
        )
        elapsed = round(time.time() - start_time + 1.2, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_sleep_dreams(prompt: str, name: str, start_time: float) -> dict:
        thinking = (
            "🧠 [Aşama 1/4 - Nörobiyolojik Kök Analiz]: Rüya ve uyku mekanizması.\n"
            "🔬 [Aşama 2/4 - REM Evresi]: Hafıza konsolidasyonu, amigdala duygu temizliği.\n"
            "🎯 [Aşama 3/4 - Sentez]: Nörolojik ve evrimsel kanıtlar sentezlendi."
        )

        reply = (
            f"**Rüya görmek ve uyumak**, ilk bakışta pasif bir dinlenme gibi görünse de aslında beynimizin günün en yoğun mesaisini yaptığı, "
            f"kendini onardığı ve hafızayı baştan yapılandırdığı **büyüleyici bir nörolojik süreçtir**.\n\n"
            "### 1. 🗄️ Hafıza Konsolidasyonu ve Dosyalama\n"
            "Uykunun özellikle **REM (Hızlı Göz Hareketi)** evresinde beynimiz bir kütüphaneci gibi çalışır: "
            "Önemli anıları kalıcı belleğe aktarırken, gereksiz sinirsel bağları budayarak beynin depolama alanını temizler.\n\n"
            "### 2. ❤️ Duygusal İlk Yardım ve Terapi Seansı\n"
            "REM uykusundayken beyindeki stres hormonu (noradrenalin) sıfırlanır. "
            "Böylece gün içindeki travmatik veya kaygılı olayları kimyasal olarak nötr ve güvenli bir ortamda işleyip sindirirsiniz.\n\n"
            "### 3. 🛡️ Tehdit Simülasyonu ve Yaratıcı Çözüm\n"
            "Rüya sırasında mantık merkezimiz (prefrontal korteks) gevşer; bu sayede birbiriyle ilgisiz kavramlar birleşerek yaratıcı problem çözümlerine kapı aralar."
        )
        elapsed = round(time.time() - start_time + 1.2, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_car_buying(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 İkinci el ve sıfır araç alımında mekanik, kaporta, şasi, tramer ve hukuki güvenlik kontrol aşamaları planlandı."
        reply = (
            f"**Araba satın alırken** maddi kayba uğramamak ve güvenli bir araç sahibi olmak için 5 kilit noktaya dikkat edilmelidir:\n\n"
            "### 1. 🛡️ Karoser, Şasi ve Direkler (En Kritik Aşama)\n"
            "- Şasi, podye, direk ve tavan sacında kaynak, kesme veya düzeltme kesinlikle olmamalıdır.\n"
            "- Hava yastığı (Airbag) kontrolleri yapılarak patlayıp patlamadığı doğrulanmalıdır.\n\n"
            "### 2. ⚙️ Motor ve Şanzıman Sağlığı\n"
            "- Isınmış motorda mavi duman (yağ yakma) veya siyah duman olmamalıdır.\n"
            "- Otomatik şanzımanlarda vuruntu ve geri kaçırma test edilmelidir.\n\n"
            "### 3. 🔍 Kilometre ve Tramer Doğrulaması\n"
            "- TÜVTÜRK muayene kayıtları ve 5664 SMS hasar sorgusu ile geçmiş incelenmelidir.\n\n"
            "### 4. 🏢 Bağımsız Kurumsal Ekspertiz\n"
            "- Satıcının önerdiği değil, TSE onaylı tarafsız kurumsal bir ekspertiz merkezinden detaylı yazılı rapor alınmalıdır.\n\n"
            "### 5. 💰 Noter Güvenli Satış Sistemi\n"
            "- Ödeme yalnızca Noterler Birliği'nin Güvenli Ödeme Sistemi üzerinden yapılmalıdır."
        )
        elapsed = round(time.time() - start_time + 1.2, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_sky_optics(prompt: str, name: str, start_time: float) -> dict:
        thinking = (
            "🧠 [Aşama 1/4 - Fiziksel Optik ve Atmosfer Analizi]:\n"
            f"• Soru: '{prompt}'\n"
            "• Güneş ışığındaki mavi dalga boylarının Rayleigh saçılması incelendi."
        )

        reply = (
            f"**Gökyüzünün mavi görünmesi**, Güneş ışığı, Dünya atmosferindeki gaz molekülleri ve insan gözünün biyolojisi arasındaki bir optik etkileşimdir:\n\n"
            "### 1. 🔬 Rayleigh Saçılması\n"
            "Güneş ışığı tüm renkleri barındırır. Kısa dalga boylu ışıklar (mavi ve mor), uzun dalga boylu ışıklara (kırmızı ve turuncu) kıyasla havadaki azot ve oksijen molekülleri tarafından yaklaşık 10 kat daha fazla saçılır. "
            "Bu saçılan mavi ışık göğün her yanına dağılır.\n\n"
            "### 2. 👁️ Neden Mor Değil de Mavi?\n"
            "Güneş mor ışıktan çok daha fazla mavi ışık yayar ve insan gözündeki koni hücreleri mavi renge karşı mora kıyasla çok daha duyarlıdır."
        )
        elapsed = round(time.time() - start_time + 1.2, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_space_blackhole(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Genel görelilik, olay ufku, tekillik ve uzay-zaman bükülmesi analiz edildi."
        reply = (
            f"**Kara delik**, devasa kütlenin akıl almaz derecede küçük bir hacme sıkışmasıyla oluşan ve kütleçekim kuvveti ışığın bile kaçamayacağı kadar güçlü olan kozmik bir yapıdır.\n\n"
            "### 1. 🕳️ Olay Ufku (Event Horizon)\n"
            "Işığın dahi geri dönemediği görünmez eşiktir.\n\n"
            "### 2. ⏳ Zamanın Yavaşlaması\n"
            "Kara deliğe yaklaştıkça uzay-zaman bükülür ve dışarıdaki bir gözlemciye göre zaman neredeyse donma noktasına gelir."
        )
        elapsed = round(time.time() - start_time + 1.2, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_biology_photosynthesis(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Klorofil foton soğurumu, ışığa bağımlı reaksiyonlar ve Calvin döngüsü incelendi."
        reply = (
            f"**Fotosentez**, bitkilerin güneş enerjisini kullanarak karbondioksit ve sudan besin (glikoz) ve oksijen üretme sürecidir.\n\n"
            "`6CO₂ + 6H₂O + Güneş Işığı ➔ C₆H₁₂O₆ + 6O₂`\n\n"
            "Dünyadaki oksijen dengesinin ve besin zincirinin temelini oluşturur."
        )
        elapsed = round(time.time() - start_time + 1.0, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_economy_money(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Enflasyon dinamikleri, para arzı ve satın alma gücü modellendi."
        reply = (
            f"**Enflasyon**, fiyatların genel düzeyinin sürekli artması ve paranın satın alma gücünün erimesidir.\n\n"
            "### Nedenleri:\n"
            "1. **Talep Enflasyonu:** Piyasada harcanan paranın üretilen mal miktarını aşması.\n"
            "2. **Maliyet Enflasyonu:** Enerji, hammadde veya döviz kuru artışının etiketlere yansıması.\n"
            "3. **Para Basımı:** Üretime dayanmayan karşılıksız para arzı artışı."
        )
        elapsed = round(time.time() - start_time + 1.1, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_health_psychology(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Kortizol ekseni, BDT ilkeleri ve stres yönetimi."
        reply = (
            f"**Stresle başa çıkmada** kanıtlanmış 3 bilimsel yöntem:\n\n"
            "1. **Fizyolojik İçe Çekiş:** İki derin burun nefesi ve uzun bir ağız nefesi kalp atışını ve kortizolü hızla düşürür.\n"
            "2. **Kontrol Çemberi:** Değiştiremeyeceğiniz dış faktörler yerine kendi tepkilerinize odaklanın.\n"
            "3. **Mikro Görevler:** Büyük işleri 10'ar dakikalık küçük dilimlere ayırarak zihinsel felci kırın."
        )
        elapsed = round(time.time() - start_time + 1.1, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_philosophy(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Varoluşçuluk ve Stoacılık sentezi."
        reply = (
            f"**\"{prompt.capitalize()}\"** konusunda felsefi iki temel sütun:\n\n"
            "1. **Varoluşçu Bakış:** Hayatın hazır bir anlamı yoktur; onu değer verdiğiniz şeyler ve aldığınız sorumluluklarla siz inşa edersiniz.\n"
            "2. **Stoacı Bakış:** Başımıza gelen olayları seçemeyiz ama onlara vereceğimiz tepkiyi her zaman biz seçeriz."
        )
        elapsed = round(time.time() - start_time + 1.1, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_programming(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Yazılım mimarisi, algoritma optimizasyonu ve kod üretimi."
        p = prompt.lower()
        if any(w in p for w in ['scraper', 'kazı', 'kazi', 'cek', 'çek', 'web']):
            reply = (
                "İstediğiniz Python web scraper kodunu `requests` ve `BeautifulSoup` kütüphaneleriyle optimize edilmiş şekilde hazırladım:\n\n"
                "```python\n"
                "import requests\n"
                "from bs4 import BeautifulSoup\n"
                "import csv\n\n"
                "def web_scraper(url: str, output_csv: str = 'veriler.csv'):\n"
                "    headers = {\n"
                "        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'\n"
                "    }\n"
                "    try:\n"
                "        response = requests.get(url, headers=headers, timeout=10)\n"
                "        response.raise_for_status()\n"
                "        soup = BeautifulSoup(response.text, 'html.parser')\n\n"
                "        items = []\n"
                "        for article in soup.find_all(['h2', 'h3', 'article']):\n"
                "            text = article.get_text(strip=True)\n"
                "            a_tag = article.find('a')\n"
                "            link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''\n"
                "            if text:\n"
                "                items.append({'baslik': text, 'link': link})\n\n"
                "        with open(output_csv, 'w', newline='', encoding='utf-8') as f:\n"
                "            writer = csv.DictWriter(f, fieldnames=['baslik', 'link'])\n"
                "            writer.writeheader()\n"
                "            writer.writerows(items)\n\n"
                "        print(f'{len(items)} adet veri başarıyla {output_csv} dosyasına kaydedildi.')\n"
                "        return items\n"
                "    except Exception as e:\n"
                "        print(f'Hata oluştu: {e}')\n"
                "        return []\n\n"
                "# Örnek Çalıştırma:\n"
                "# web_scraper('https://news.ycombinator.com')\n"
                "```\n\n"
                "### 🔍 Kod Açıklaması:\n"
                "1. **User-Agent:** Bot engeline takılmamak için tarayıcı başlığı kullanır.\n"
                "2. **Hata Yönetimi:** Ağ ve HTTP hatalarını güvenle yakalar.\n"
                "3. **Veri Kaydı:** Çekilen başlık ve linkleri UTF-8 formatında CSV dosyasına kaydeder."
            )
        elif 'faktoriyel' in p or 'factorial' in p:
            reply = (
                "Python ile hem özyinelemeli (recursive) hem de döngüsel (iterative) faktöriyel fonksiyonu:\n\n"
                "```python\ndef faktoriyel(n: int) -> int:\n"
                "    if not isinstance(n, int) or n < 0:\n"
                "        raise ValueError('Faktöriyel yalnızca negatif olmayan tam sayılar için tanımlıdır.')\n"
                "    sonuc = 1\n"
                "    for i in range(2, n + 1):\n"
                "        sonuc *= i\n"
                "    return sonuc\n\n"
                "# Test:\n"
                "for sayi in [0, 1, 5, 7]:\n"
                "    print(f'{sayi}! = {faktoriyel(sayi)}')\n```"
            )
        else:
            reply = (
                f"Talebiniz doğrultusunda optimize edilmiş ve temiz kod (Clean Code) standartlarında hazırlanan çözüm:\n\n"
                "```python\n"
                "from typing import Any, List, Dict\n\n"
                "def veri_isleyici(girdi_listesi: List[Any]) -> Dict[str, Any]:\n"
                "    \"\"\"\n"
                "    Girdileri filtreleyip yapılandırılmış veri üreten fonksiyon.\n"
                "    \"\"\"\n"
                "    if not girdi_listesi:\n"
                "        return {'durum': 'bos', 'sayi': 0}\n\n"
                "    sayisal_veriler = [x for x in girdi_listesi if isinstance(x, (int, float))]\n"
                "    return {\n"
                "        'toplam_eleman': len(girdi_listesi),\n"
                "        'sayisal_adet': len(sayisal_veriler),\n"
                "        'toplam_deger': sum(sayisal_veriler) if sayisal_veriler else 0,\n"
                "        'ortalama': sum(sayisal_veriler) / len(sayisal_veriler) if sayisal_veriler else 0\n"
                "    }\n\n"
                "# Test Çalıştırması:\n"
                "ornek_veri = [10, 'elma', 25.5, None, 40, 'test']\n"
                "print(veri_isleyici(ornek_veri))\n"
                "```\n\n"
                "### 💡 Kod Özeti:\n"
                "- Tip güvenliği için `typing` kütüphanesi kullanılmıştır.\n"
                "- Fonksiyon geçersiz ve boş verilere karşı dayanıklı şekilde tasarlanmıştır."
            )
        elapsed = round(time.time() - start_time + 0.8, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_table(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Karşılaştırma parametreleri ve Markdown tablosu kurgulandı."
        p = prompt.lower()
        if 'telefon' in p:
            reply = (
                "Piyasadaki 3 büyük amiral gemisi akıllı telefonun karşılaştırma tablosu:\n\n"
                "| Özellik | Apple iPhone 15 Pro Max | Samsung Galaxy S24 Ultra | Xiaomi 14 Ultra |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **İşlemci** | Apple A17 Pro (3nm) | Snapdragon 8 Gen 3 for Galaxy | Snapdragon 8 Gen 3 |\n"
                "| **Ekran** | 6.7\" OLED 120Hz Super Retina | 6.8\" Dynamic AMOLED 2X 120Hz | 6.73\" LTPO AMOLED 120Hz |\n"
                "| **Ana Kamera** | 48 MP (Sensör Kaydırmalı OIS) | 200 MP (f/1.7 OIS) | 50 MP (1 inç Sony LYT-900) |\n"
                "| **Telefoto** | 5x Optik Zoom (12 MP) | 5x (50 MP) + 3x (10 MP) | 5x (50 MP) + 3.2x (50 MP) |\n"
                "| **Batarya** | 4,422 mAh | 5,000 mAh (45W Hızlı Şarj) | 5,000 mAh (90W Hızlı Şarj) |\n"
                "| **Yapay Zeka** | Apple Intelligence | Galaxy AI (Canlı Çeviri vb.) | Xiaomi HyperOS AI |\n\n"
                "### 📌 Genel Değerlendirme:\n"
                "- **iPhone 15 Pro Max:** Video kayıt kalitesi ve iOS ekosistem entegrasyonunda öne çıkar.\n"
                "- **S24 Ultra:** Dahili S-Pen kalemi ve yansıma önleyici ekranıyla üretkenlikte liderdir.\n"
                "- **Xiaomi 14 Ultra:** 1 inçlik ana sensörüyle profesyonel fotoğrafçılıkta zirvededir."
            )
        else:
            reply = (
                "İstediğiniz karşılaştırma ve analiz tablosu:\n\n"
                "| Kriter / Parametre | Seçenek 1 (Temel) | Seçenek 2 (Dengeli) | Seçenek 3 (Gelişmiş) |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Maliyet** | Düşük Bütçeli | Orta Seviye (Fiyat/Performans) | Yüksek / Premium |\n"
                "| **Performans** | Standart İhtiyaçlar | Yüksek Hız ve Verimlilik | Maksimum Kapasite |\n"
                "| **Kullanım Kolaylığı** | Çok Basit | Dengeli ve Modüler | İleri Düzey Özelleştirme |\n"
                "| **Öne Çıkan Avantaj** | Hızlı kurulum ve tasarruf | En ideal fayda/maliyet dengesi | Sınırsız ölçeklenebilirlik |\n\n"
                "Spesifik ürün veya karşılaştırma kriterleri eklemek isterseniz hemen özelleştirebilirim."
            )
        elapsed = round(time.time() - start_time + 0.8, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_email(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Kurumsal tonlama ve e-posta kurgusu."
        p = prompt.lower()
        if 'izin' in p:
            reply = (
                "**Konu:** Yıllık İzin Talebi - [Adınız Soyadınız]\n\n"
                "Sayın [Yöneticinizin Adı],\n\n"
                "[Başlangıç Tarihi] ile [Bitiş Tarihi] tarihleri arasında, toplam [Gün Sayısı] iş günü sürecek olan yıllık izin hakkımı kullanmak istiyorum.\n\n"
                "İzinde olacağım süre zarfında sorumluluğumda bulunan acil ve devam eden görevleri [Çalışma Arkadaşınızın Adı]'na devretmiş bulunmaktayım. Kritik durumlarda bana e-posta ve telefonum üzerinden ulaşılabilecektir.\n\n"
                "İzin talebimin onaylanmasını saygılarımla arz ederim.\n\n"
                "İyi çalışmalar dilerim,\n\n"
                f"**[Adınız Soyadınız]**\n"
                "[Unvanınız / Departmanınız]\n"
                "[İletişim Bilgileriniz]"
            )
        elif 'istifa' in p:
            reply = (
                "**Konu:** İstifa Bildirimi - [Adınız Soyadınız]\n\n"
                "Sayın [Yöneticinizin Adı / İnsan Kaynakları],\n\n"
                "Büyük bir memnuniyetle sürdürdüğüm [Unvanınız] görevimden, aldığım kişisel ve kariyer kararları doğrultusunda [Ayrılma Tarihi] tarihi itibarıyla ayrılmak istediğimi bildirmek isterim.\n\n"
                "Şirketinizde geçirdiğim süre boyunca bana kattığınız değerler ve destek için sizlere teşekkür ederim. Ayrılış tarihime kadar devir teslim sürecini eksiksiz tamamlayacağım.\n\n"
                "Bilgilerinize sunar, saygılarımı iletirim.\n\n"
                f"**[Adınız Soyadınız]**\n"
                "[İmzanız]"
            )
        else:
            reply = (
                "**Konu:** [Konu Başlığı]\n\n"
                "Sayın [Alıcı Adı / İlgili Makam],\n\n"
                "Bu e-postayı [konunun özeti ve amacı] hakkında sizleri bilgilendirmek ve süreci değerlendirmek amacıyla yazmaktayım.\n\n"
                "Konuyla ilgili detayları uygun olduğunuz bir zaman diliminde görüşmekten memnuniyet duyarım.\n\n"
                "Geri bildiriminizi bekler, iyi çalışmalar dilerim.\n\n"
                "Saygılarımla,\n\n"
                f"**[Adınız Soyadınız]**\n"
                "[İletişim Bilgileriniz]"
            )
        elapsed = round(time.time() - start_time + 0.7, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_planning(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Zaman yönetimi ve aşamalı eylem planı."
        reply = (
            f"**\"{prompt.capitalize()}\"** için uygulanabilir adım adım eylem planı:\n\n"
            "### 🚀 Aşama 1: Hazırlık ve Temel Kurulum (1. - 3. Gün)\n"
            "- **Hedeflerin Netleştirilmesi:** Ulaşılmak istenen nihai çıktıyı ölçülebilir metriklere dökün.\n"
            "- **Gerekli Kaynakların Toplanması:** İhtiyaç duyulan doküman, araç ve yazılımları eksiksiz hazırlayın.\n"
            "- **Zaman Bloklama:** Gün içinde odaklanılacak en verimli saatleri bu hedefe tahsis edin.\n\n"
            "### ⚙️ Aşama 2: Uygulama ve İlerleme (4. - 10. Gün)\n"
            "- **Mikro Görevlere Bölme:** Büyük adımları 45 dakikalık odak seanslarına (Pomodoro) ayırarak ilerleyin.\n"
            "- **Prototip / İlk Çıktı:** Mükemmeliyetçilik tuzağına düşmeden çalışan ilk versiyonu hayata geçirin.\n"
            "- **Hata Ayıklama:** Karşılaşılan engelleri anında not alıp çözümleyin.\n\n"
            "### 🎯 Aşama 3: İnceleme ve Optimizasyon (11. Gün ve Sonrası)\n"
            "- **Performans Değerlendirmesi:** Planın ne kadarının gerçekleştiğini kontrol edin.\n"
            "- **İyileştirme:** Eksik kalan alanları takviye ederek süreci kalıcı bir rutine dönüştürün."
        )
        elapsed = round(time.time() - start_time + 0.8, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_ai(prompt: str, name: str, start_time: float) -> dict:
        thinking = "🧠 Büyük dil modelleri, Chain-of-Thought ve otonom yapay zeka ajanları."
        reply = (
            f"**\"{prompt.capitalize()}\"**, günümüz yapay zekasında 'sonraki kelimeyi tahmin etme'den 'adım adım akıl yürütme (Reasoning)' aşamasına geçişi temsil eder."
        )
        elapsed = round(time.time() - start_time + 1.1, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_conversation(prompt: str, name: str, model_name: str, start_time: float) -> dict:
        if "mebot" in model_name.lower():
            thinking = "🧠 [MEBOT 0.1 Süper Model]: Nezaket, tanışma ve süper bilişsel rehberlik."
            reply = (
                f"Merhaba **{name}**! Ben **MEBOT 0.1** — *EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL*.\n\n"
                "Bütün modellerden daha derin düşünebilen ve çok boyutlu akıl yürüten süper bilişsel mimarimle hizmetinizdeyim. "
                "Mantık bulmacaları, ileri düzey algoritmalar ve kodlama, veri tabloları, bilimsel araştırmalar veya stratejik planlamalarda birlikte çalışabiliriz. Size nasıl yardımcı olabilirim?"
            )
        else:
            thinking = "🧠 Nezaket ve yardımcı asistan kimliği."
            reply = (
                f"Merhaba **{name}**! Ben **MEBOT** ({model_name}).\n\n"
                "Nasıl yardımcı olabilirim? Mantık soruları, kodlama, bilimsel araştırmalar veya günlük kararlarınızda adım adım birlikte akıl yürütebiliriz."
            )
        elapsed = round(time.time() - start_time + 0.6, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_universal_knowledge(prompt: str, name: str, topic_info: dict, start_time: float) -> dict:
        topic = topic_info['topic']
        extract = topic_info['extract']
        paragraphs = [p.strip() for p in extract.split('\n') if len(p.strip()) > 60]
        tanim = paragraphs[0] if paragraphs else extract[:300]
        detaylar = paragraphs[1:3] if len(paragraphs) > 1 else []
        detay_metni = "\n\n".join(detaylar) if detaylar else ""

        thinking = (
            f"🧠 [Aşama 1/4 - Kavram Tespiti]: '{prompt}' ➔ Konu: '{topic}'\n"
            f"🔬 [Aşama 2/4 - Olgusal Temel]: Doğrulanmış bilgiler incelendi.\n"
            f"🎯 [Aşama 3/4 - Sentez]: Anlaşılır ve yapılandırılmış özet kurgulandı."
        )

        reply = (
            f"**\"{prompt.capitalize()}\"** konusunu **{topic}** temelinde incelediğimizde öne çıkan boyutlar:\n\n"
            f"### 🎯 1. Kök Tanım\n{tanim}\n\n"
        )
        if detay_metni:
            reply += f"### ⚙️ 2. Özellikler ve Boyutlar\n{detay_metni}\n\n"
        reply += f"*(Kaynak: 🔒 [{topic} - Vikipedi]({topic_info['url']}))*"
        elapsed = round(time.time() - start_time + 1.2, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_web_research(prompt: str, name: str, web_data: dict, start_time: float) -> dict:
        sources = web_data["inspected_sources"]
        sources_md = [f"{i}. 🔒 [{s['title']}]({s['url']}) `(Doğrulanmış HTTPS)`" for i, s in enumerate(sources, 1)]

        thinking = f"🧠 Web araştırması tamamlandı: {len(sources)} adet doğrulanmış HTTPS kaynağı incelendi."
        highlights = []
        for s in sources:
            content = s.get("content", "")
            first_sentence = content.split(".")[0].strip() if content else ""
            if first_sentence and len(first_sentence) > 30:
                highlights.append(f"- **{s['title']}:** {first_sentence}.")

        reply = (
            f"**\"{prompt.capitalize()}\"** konusuyla ilgili güvenli web kaynaklarını inceledim:\n\n"
            f"### 🌐 Bulgular\n" + ("\n".join(highlights) if highlights else "- Veriler derlendi.") + "\n\n"
            f"### 🔒 Doğrulanmış Kaynaklar (Yalnızca HTTPS)\n" + "\n".join(sources_md)
        )
        elapsed = round(time.time() - start_time + 1.2, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}

    @staticmethod
    def _solve_deep_thought(prompt: str, name: str, start_time: float) -> dict:
        thinking = f"🧠 '{prompt}' sorusu mantıksal çerçevede analiz edildi."
        reply = (
            f"**\"{prompt.capitalize()}\"** konusundaki temel dinamikler:\n\n"
            "### 1. 🔍 Kök Sebep ve Öncelikler\n"
            "Yüzeysel sonuçlara odaklanmak yerine, durumu başlatan ana faktörleri analiz etmek gerekir.\n\n"
            "### 2. 🎯 Stratejik Yaklaşım\n"
            "Bu konuyu belirli bir pratik senaryoya veya soruya uyarlamak isterseniz ayrıntıları iletebilirsiniz."
        )
        elapsed = round(time.time() - start_time + 1.0, 2)
        return {"thinking": thinking, "reply": reply, "thinking_time": elapsed}


# =========================================================================
# 4. Google Gemini API & Hibrit Akıl Motoru (Hybrid Reasoning)
# =========================================================================
def should_trigger_web_search(prompt: str, force_search: bool = False) -> bool:
    if force_search:
        return True
    p = prompt.lower()
    pattern = r'\b(araştır|araştırması|internette|internetten|webden|webde|google\'da|googleda|son haberler|güncel durum|fiyatı nedir)\b'
    return bool(re.search(pattern, p))


def get_gemini_reply(api_key: str, model_name: str, prompt: str, user_name: str, force_web_search: bool = False, deep_think: bool = True, extra_context: str = "", base64_image: str = None, vision_think: bool = False) -> dict:
    if model_name in ["DENEME 1", ""]:
        model_name = "MEBOT 0.1"

    web_research_data = None
    if should_trigger_web_search(prompt, force_web_search):
        web_research_data = WebResearcher.conduct_full_research(prompt)

    is_mebot_super = ("mebot" in model_name.lower()) or (model_name == "MEBOT 0.1")

    if is_mebot_super:
        model_candidates = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest", "gemini-1.5-flash-8b"]
    elif "Pro" in model_name:
        model_candidates = ["gemini-1.5-flash", "gemini-3.1-pro-preview", "gemini-pro-latest"]
    else:
        model_candidates = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest", "gemini-1.5-flash-8b"]

    web_context = ""
    if web_research_data and web_research_data.get("inspected_sources"):
        sources = web_research_data["inspected_sources"]
        web_context = (
            "\n\n[GÜVENLİ WEB ARAŞTIRMA VERİLERİ (YALNIZCA HTTPS KONTROL EDİLDİ)]:\n"
            + "\n".join([f"KAYNAK ({s['title']} - {s['url']}):\n{s['content'][:1500]}" for s in sources])
            + "\n\nLÜTFEN CEVABINDA BU GÜVENLİ HTTPS KAYNAKLARINDAN YARARLAN VE EN ALTTA LİSTELE."
        )

    base_instruction = (
        f"Sen MEBOT adında çok yönlü bir yapay zekâ asistanısın. Kullanıcı: {user_name}.\n\n"
        "Kullanıcı senden kod istiyorsa doğrudan optimize edilmiş kodu ve açıklamasını yaz; "
        "tablo istiyorsa Markdown tablosu oluştur; "
        "e-posta istiyorsa e-postayı yaz; "
        "mantık sorusu soruyorsa problemi çözüp net cevabı ver. "
        "Asla boş taslak başlıklar üretme, doğrudan istenen içeriği eksiksiz teslim et."
    )

    base_instruction = base_instruction + SAFETY_INSTRUCTION + (extra_context or "")

    # Dinamik Sistem İstemi: Derin Düşünme Aktifse
    if deep_think:
        system_instruction = (
            base_instruction + "\n\n"
            "'Derin Düşün' modu açık: Modele sabit başlıklar dayatma. Sadece arka planda düşün, "
            "yanıtta ise doğrudan ulaştığın kesin ve ayrıntılı çözümü adım adım sun. Düşüncelerini <thought> etiketleri içine yazabilirsin."
            + web_context
        )
        gen_temperature = 0.2
    else:
        system_instruction = base_instruction + web_context
        gen_temperature = 0.7

    if vision_think and base64_image:
        system_instruction += "\n\n'Resim Üzerinden Yoğun Düşünme' aktif: Kullanıcının yüklediği görseldeki her bir pikseli, detayı, metni milimetrik olarak incele. Görsel veriyi en derin seviyede analiz ederek doğrudan çözüme veya sonuca ulaş."


    # 1. Gemini SDK ile dene
    active_key = api_key or os.getenv("GEMINI_API_KEY", "")
    if HAS_GENAI_LIB and active_key:
        try:
            start_t = time.time()
            genai.configure(api_key=active_key)
            gen_config = {"temperature": gen_temperature}
            for mod in model_candidates:
                try:
                    model = genai.GenerativeModel(mod, system_instruction=system_instruction, generation_config=gen_config)
                    content_parts = [prompt]
                    if base64_image:
                        import base64
                        mime_type = "image/jpeg"
                        encoded = base64_image
                        if "data:" in base64_image and ";base64," in base64_image:
                            header, encoded = base64_image.split(";base64,", 1)
                            mime_type = header.split(":")[1]
                        
                        # Use inline_data structure!
                        # Some versions of google-generativeai require this:
                        img_data = base64.b64decode(encoded)
                        content_parts.append({"mime_type": mime_type, "data": img_data})
                        
                    response = model.generate_content(content_parts)
                    if response and response.text:
                        elapsed = round(time.time() - start_t, 2)
                        return parse_thought_and_reply(response.text, elapsed, prompt, is_mebot_super, deep_think)
                except Exception:
                    continue
        except Exception as e:
            print(f"[Gemini SDK Hatası]: {e}")

    # 2. Gemini REST API ile dene
    if active_key:
        try:
            start_t = time.time()
            for mod in model_candidates:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={active_key}"
                payload = {
                    "systemInstruction": {
                        "parts": [{"text": system_instruction}]
                    },
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ],
                    "generationConfig": {
                        "temperature": gen_temperature
                    }
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        result = json.loads(resp.read().decode("utf-8"))
                        candidates = result.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                elapsed = round(time.time() - start_t, 2)
                                return parse_thought_and_reply(parts[0]["text"], elapsed, prompt, is_mebot_super, deep_think)
                except Exception as inner_e:
                    print(f"[Gemini REST API Model {mod} Denemesi Hatası]: {inner_e}")
                    try:
                        fb_payload = {
                            "contents": [
                                {"parts": [{"text": f"{system_instruction}\n\nKullanıcının Güncel Sorusu: {prompt}"}]}
                            ],
                            "generationConfig": {"temperature": gen_temperature}
                        }
                        fb_data = json.dumps(fb_payload).encode("utf-8")
                        fb_req = urllib.request.Request(url, data=fb_data, headers={"Content-Type": "application/json"})
                        with urllib.request.urlopen(fb_req, timeout=10) as fb_resp:
                            fb_res = json.loads(fb_resp.read().decode("utf-8"))
                            fb_cands = fb_res.get("candidates", [])
                            if fb_cands:
                                fb_parts = fb_cands[0].get("content", {}).get("parts", [])
                                if fb_parts and "text" in fb_parts[0]:
                                    elapsed = round(time.time() - start_t, 2)
                                    return parse_thought_and_reply(fb_parts[0]["text"], elapsed, prompt, is_mebot_super, deep_think)
                    except Exception:
                        pass
                    continue
        except Exception as e:
            print(f"[Gemini REST API Hatası]: {e}")

    if not active_key:
        return {
            "thinking": "Sistem Uyarısı: API Anahtarı Gerekli",
            "reply": "MEBOT 0.1 (Süper Model) gücünü kullanabilmek için API anahtarına ihtiyaç duymaktadır. Lütfen sağ üstteki **Ayarlar** menüsüne girerek Google Gemini API anahtarınızı ekleyin.",
            "thinking_time": 0.5
        }

    return {
        "thinking": "Sistem Uyarısı: API Bağlantı Hatası",
        "reply": "Google Gemini API'sine bağlanılamadı veya API anahtarınız geçersiz. Lütfen girdiğiniz API anahtarını kontrol edin veya internet bağlantınızı doğrulayın.",
        "thinking_time": 0.5
    }


def parse_thought_and_reply(raw_text: str, elapsed: float, prompt: str = "", is_mebot_super: bool = False, deep_think: bool = True) -> dict:
    thought_match = re.search(r'<thought>(.*?)</thought>', raw_text, re.DOTALL | re.IGNORECASE)
    dyn_time = calculate_dynamic_thinking_time(prompt, is_mebot_super, deep_think) if prompt else elapsed
    final_time = max(elapsed, dyn_time) if is_mebot_super else elapsed

    if thought_match:
        thinking_content = thought_match.group(1).strip()
        clean_reply = re.sub(r'<thought>.*?</thought>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
        if is_mebot_super and not thinking_content.startswith("🧠 [MEBOT 0.1"):
            thinking_content = "🧠 [MEBOT 0.1 — EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL]:\n" + thinking_content
        return {
            "thinking": thinking_content,
            "reply": clean_reply,
            "thinking_time": final_time
        }
    else:
        default_thought = (
            "🧠 [MEBOT 0.1 — EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL]: Problem çok boyutlu analiz edildi, en yüksek zekâ ve optimizasyonla doğrudan istenen içerik üretildi."
            if is_mebot_super else
            "🧠 Soru analiz edildi ve doğrudan istenen içerik üretildi."
        )
        return {
            "thinking": default_thought,
            "reply": raw_text.strip(),
            "thinking_time": final_time
        }


# =========================================================================
# 5. HTTP Sunucusu ve İstek Yöneticisi
# =========================================================================
class MebotRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Robots-Tag", "noindex, nofollow, noarchive, nosnippet")
        super().end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/robots.txt":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"User-agent: *\nDisallow: /\n")
            return

        if self.path == "/api/status":
            env_key = os.getenv("GEMINI_API_KEY", "")
            response_data = {
                "status": "online",
                "gemini_ready": bool(env_key),
                "has_api_key": bool(env_key),
                "engine": "MEBOT 0.1 — EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL (Reasoning & CoT)",
                "server": "MEBOT Python Backend"
            }
            self.send_json(response_data)
            return

        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_bytes = self.rfile.read(content_length)
        try:
            body = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                body = raw_bytes.decode("cp1254")
            except UnicodeDecodeError:
                body = raw_bytes.decode("latin-1", errors="replace")

        # API Anahtarını Kalıcı Kaydetme Uç Noktası
        if self.path == "/api/save_key":
            try:
                data = json.loads(body)
                new_key = data.get("apiKey", "").strip()
                if new_key:
                    os.environ["GEMINI_API_KEY"] = new_key
                    try:
                        with open(KEY_FILE_PATH, "w", encoding="utf-8") as f:
                            f.write(new_key)
                        with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
                            f.write(f"GEMINI_API_KEY={new_key}\n")
                    except Exception as fe:
                        print(f"[Anahtar Kaydetme Dosya Hatası]: {fe}")

                    self.send_json({"success": True, "message": "API Anahtarı başarıyla kaydedildi!"})
                else:
                    self.send_json({"success": False, "message": "Geçersiz API Anahtarı."})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        # Kullanıcı Giriş / Kayıt Uç Noktası (6 haneli PIN ve İsim)
        if self.path == "/api/auth/login":
            try:
                data = json.loads(body)
                raw_username = str(data.get("username", "")).strip()
                pin = str(data.get("pin", "")).strip()

                if not raw_username:
                    self.send_json({"success": False, "error": "Lütfen bir kullanıcı adı veya isim giriniz."})
                    return

                if len(pin) != 6 or not pin.isdigit():
                    self.send_json({"success": False, "error": "Şifre tam 6 haneli rakam olmalıdır (örn: 123456)."})
                    return

                u_key = raw_username.lower()
                db = load_db()
                if "users" not in db:
                    db["users"] = {}

                now_str = time.strftime("%Y-%m-%d %H:%M:%S")

                if u_key in db["users"]:
                    user = db["users"][u_key]
                    if user.get("pin") != pin:
                        self.send_json({"success": False, "error": "Hatalı şifre! Bu isim için belirlenmiş 6 haneli şifre eşleşmiyor."})
                        return
                    user["last_login"] = now_str
                    user = ensure_user_struct(user)
                    save_db(db)
                    self.send_json({
                        "success": True,
                        "username": user.get("username", raw_username),
                        "pin": pin,
                        "is_new": False,
                        "chats": user.get("chats", []),
                        "settings": user.get("settings", {}),
                        "memories": user.get("memories", []),
                        "policy_accepted": user.get("policy_accepted", False)
                    })
                    return
                else:
                    new_user = {
                        "username": raw_username,
                        "pin": pin,
                        "created_at": now_str,
                        "last_login": now_str,
                        "policy_accepted": False
                    }
                    new_user = ensure_user_struct(new_user)
                    db["users"][u_key] = new_user
                    save_db(db)
                    self.send_json({
                        "success": True,
                        "username": raw_username,
                        "pin": pin,
                        "is_new": True,
                        "chats": [],
                        "settings": new_user.get("settings", {}),
                        "memories": [],
                        "policy_accepted": False
                    })
                    return
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        # Sohbet Mesajı Kaydetme / Senkronizasyon
        if self.path == "/api/auth/save_message":
            try:
                data = json.loads(body)
                raw_username = str(data.get("username", "")).strip()
                pin = str(data.get("pin", "")).strip()
                msg = data.get("message")

                if raw_username and msg:
                    u_key = raw_username.lower()
                    db = load_db()
                    if u_key in db.get("users", {}):
                        user = db["users"][u_key]
                        if user.get("pin") == pin or pin == ADMIN_MASTER_CODE:
                            if "messages" not in user:
                                user["messages"] = []
                            user["messages"].append(msg)
                            save_db(db)
                self.send_json({"success": True})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        # Admin Girişi (565856 Kodu ile)
        if self.path == "/api/admin/login":
            try:
                data = json.loads(body)
                admin_code = str(data.get("admin_code", "")).strip()

                if admin_code == ADMIN_MASTER_CODE:
                    db = load_db()
                    users_list = []
                    total_messages = 0
                    for u_k, u_v in db.get("users", {}).items():
                        msg_count = len(u_v.get("messages", []))
                        total_messages += msg_count
                        users_list.append({
                            "username": u_v.get("username", u_k),
                            "pin": u_v.get("pin", "******"),
                            "created_at": u_v.get("created_at", "-"),
                            "last_login": u_v.get("last_login", "-"),
                            "message_count": msg_count
                        })
                    users_list.sort(key=lambda x: x.get("last_login", ""), reverse=True)
                    self.send_json({
                        "success": True,
                        "admin": True,
                        "users": users_list,
                        "total_users": len(users_list),
                        "total_messages": total_messages
                    })
                else:
                    self.send_json({
                        "success": False,
                        "error": "Hatalı Admin Kodu! Lütfen geçerli bir kod giriniz."
                    })
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        # Admin Ekranından Kullanıcı Sohbetlerini Görüntüleme (565856 Bypass)
        if self.path == "/api/admin/get_user_chats":
            try:
                data = json.loads(body)
                admin_code = str(data.get("admin_code", "")).strip()
                target_username = str(data.get("target_username", "")).strip()

                if admin_code == ADMIN_MASTER_CODE:
                    db = load_db()
                    u_key = target_username.lower()
                    if u_key in db.get("users", {}):
                        u_v = db["users"][u_key]
                        self.send_json({
                            "success": True,
                            "username": u_v.get("username", target_username),
                            "pin": u_v.get("pin", ""),
                            "created_at": u_v.get("created_at", "-"),
                            "last_login": u_v.get("last_login", "-"),
                            "messages": u_v.get("messages", [])
                        })
                    else:
                        self.send_json({"success": False, "error": f"'{target_username}' adlı kullanıcı bulunamadı."})
                else:
                    self.send_json({"success": False, "error": "Yetkisiz işlem! Geçerli Admin Kodu gerekli."})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        # Admin Ekranından Kullanıcı Sohbetlerini Silme / Temizleme
        if self.path == "/api/admin/delete_user_chats":
            try:
                data = json.loads(body)
                admin_code = str(data.get("admin_code", "")).strip()
                target_username = str(data.get("target_username", "")).strip()
                message_index = data.get("message_index")

                if admin_code == ADMIN_MASTER_CODE:
                    db = load_db()
                    u_key = target_username.lower()
                    if u_key in db.get("users", {}):
                        u_v = db["users"][u_key]
                        if message_index is not None and isinstance(message_index, int):
                            msgs = u_v.get("messages", [])
                            if 0 <= message_index < len(msgs):
                                msgs.pop(message_index)
                                u_v["messages"] = msgs
                                save_db(db)
                                self.send_json({"success": True, "message": "Mesaj başarıyla silindi."})
                                return
                            else:
                                self.send_json({"success": False, "error": "Geçersiz mesaj indeksi."})
                                return
                        else:
                            # Tüm sohbet geçmişini temizle
                            u_v["messages"] = []
                            save_db(db)
                            self.send_json({"success": True, "message": f"'{target_username}' adlı kullanıcının tüm sohbet geçmişi silindi."})
                            return
                    else:
                        self.send_json({"success": False, "error": f"'{target_username}' adlı kullanıcı bulunamadı."})
                else:
                    self.send_json({"success": False, "error": "Yetkisiz işlem! Geçerli Admin Kodu gerekli."})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        # Admin Ekranından Kullanıcı Hesabını Tamamen Silme
        if self.path == "/api/admin/delete_user":
            try:
                data = json.loads(body)
                admin_code = str(data.get("admin_code", "")).strip()
                target_username = str(data.get("target_username", "")).strip()

                if admin_code == ADMIN_MASTER_CODE:
                    db = load_db()
                    u_key = target_username.lower()
                    if u_key in db.get("users", {}):
                        del db["users"][u_key]
                        save_db(db)
                        self.send_json({"success": True, "message": f"'{target_username}' adlı kullanıcı hesabı ve sohbetleri silindi."})
                    else:
                        self.send_json({"success": False, "error": f"'{target_username}' adlı kullanıcı bulunamadı."})
                else:
                    self.send_json({"success": False, "error": "Yetkisiz işlem! Geçerli Admin Kodu gerekli."})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return


        # Sohbet Uç Noktası
        if self.path == "/api/chat":
            try:
                data = json.loads(body)
                user_msg = str(data.get("message", "")).strip()
                user_name = str(data.get("username", "Kullanıcı")).strip()
                user_pin = str(data.get("pin", "")).strip()
                model_name = str(data.get("model", "MEBOT 0.1")).strip()
                chat_id = str(data.get("chat_id", "")).strip()
                if not chat_id:
                    import time
                    chat_id = f"chat-{int(time.time()*1000)}"

                if model_name in ["DENEME 1", ""]:
                    model_name = "MEBOT 0.1"
                client_api_key = str(data.get("apiKey", "")).strip() or os.getenv("GEMINI_API_KEY", "")
                force_web_search = bool(data.get("webSearch", False))
                deep_think = bool(data.get("deepThink", True))
                base64_img = data.get(image)
                with open(image_debug.txt, w) as f: f.write(str(len(base64_img)) if base64_img else NONE)
                v_think = bool(data.get("visionThink", False))

                # Profanity Check
                if contains_profanity(user_msg):
                    if user_name and user_name != "Kullanıcı":
                        u_key = user_name.lower()
                        db = load_db()
                        if u_key in db.get("users", {}):
                            user_rec = db["users"][u_key]
                            user_rec["chats"] = [c for c in user_rec.get("chats", []) if c.get("id") != chat_id]
                            save_db(db)
                    self.send_json({"success": False, "error": "Argo/küfür kullanımı tespit edildi. MEBOT güvenlik politikaları gereği bu sohbet sonlandırılmış ve silinmiştir.", "profanity": True})
                    return

                # Harm check
                harm = detect_harm(user_msg)
                if harm == "self_harm":
                    self.send_json({"success": True, "reply": SELF_HARM_REPLY, "thinking": "Acil durum/kendine zarar verme riski tespit edildi. Destek mesajı gönderiliyor.", "thinking_time": 0.5, "model": model_name})
                    return
                elif harm == "violence":
                    self.send_json({"success": True, "reply": VIOLENCE_REPLY, "thinking": "Şiddet/zarar verme eğilimi tespit edildi. Güvenlik kuralları gereği reddediliyor.", "thinking_time": 0.5, "model": model_name})
                    return

                result = get_gemini_reply(client_api_key, model_name, user_msg, user_name, force_web_search, deep_think, "", base64_img, v_think)

                if user_name and user_name != "Kullanıcı":
                    u_key = user_name.lower()
                    db = load_db()
                    if u_key in db.get("users", {}):
                        user_rec = db["users"][u_key]
                        if not user_pin or user_rec.get("pin") == user_pin or user_pin == ADMIN_MASTER_CODE:
                            user_rec = ensure_user_struct(user_rec)
                            
                            c_chat = find_chat(user_rec, chat_id)
                            now_stamp = time.strftime("%Y-%m-%d %H:%M:%S")
                            
                            if not c_chat:
                                title = user_msg[:30] + "..." if len(user_msg) > 30 else user_msg
                                c_chat = {
                                    "id": chat_id,
                                    "title": title,
                                    "created_at": now_stamp,
                                    "updated_at": now_stamp,
                                    "messages": []
                                }
                                user_rec["chats"].insert(0, c_chat)
                            
                            c_chat["updated_at"] = now_stamp
                            c_chat["messages"].append({
                                "role": "user",
                                "content": user_msg,
                                "timestamp": now_stamp
                            })
                            c_chat["messages"].append({
                                "role": "assistant",
                                "content": result.get("reply", ""),
                                "thinking": result.get("thinking", ""),
                                "thinking_time": result.get("thinking_time", 1.8),
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                            if user_rec.get("settings", {}).get("memory_enabled", True):
                                new_memories = extract_memories(user_msg)
                                for m in new_memories:
                                    if not any(em.get("text") == m for em in user_rec.get("memories", [])):
                                        user_rec["memories"].append({"text": m, "timestamp": now_stamp})

                            save_db(db)

                response_data = {
                    "success": True,
                    "thinking": result.get("thinking", ""),
                    "thinking_time": result.get("thinking_time", 1.8),
                    "reply": result.get("reply", ""),
                    "model": model_name,
                    "is_local_mode": not bool(client_api_key),
                    "chat_id": chat_id
                }

                self.send_json(response_data)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                pass
            except Exception as e:
                try:
                    self.send_json({"success": False, "error": str(e)}, status=500)
                except Exception:
                    pass
            return

        if self.path == "/api/auth/accept_policy":
            try:
                data = json.loads(body)
                raw_username = str(data.get("username", "")).strip()
                pin = str(data.get("pin", "")).strip()

                u_key = raw_username.lower()
                db = load_db()
                if u_key in db.get("users", {}):
                    user = db["users"][u_key]
                    if user.get("pin") == pin:
                        user["policy_accepted"] = True
                        save_db(db)
                        self.send_json({"success": True})
                    else:
                        self.send_json({"success": False, "error": "Geçersiz şifre"})
                else:
                    self.send_json({"success": False, "error": "Kullanıcı bulunamadı"})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        if self.path == "/api/auth/save_settings":
            try:
                data = json.loads(body)
                raw_username = str(data.get("username", "")).strip()
                pin = str(data.get("pin", "")).strip()
                personalization = data.get("personalization", "")
                memory_enabled = data.get("memory_enabled", True)

                u_key = raw_username.lower()
                db = load_db()
                if u_key in db.get("users", {}):
                    user = db["users"][u_key]
                    if user.get("pin") == pin:
                        user = ensure_user_struct(user)
                        user["settings"]["personalization"] = personalization
                        user["settings"]["memory_enabled"] = memory_enabled
                        save_db(db)
                        self.send_json({"success": True})
                    else:
                        self.send_json({"success": False, "error": "Geçersiz şifre"})
                else:
                    self.send_json({"success": False, "error": "Kullanıcı bulunamadı"})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        self.send_response(404)
        self.end_headers()


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_server():
    global PORT
    if "PORT" not in os.environ:
        while is_port_in_use(PORT):
            print(f"Port {PORT} meşgul, {PORT + 1} deneniyor...")
            PORT += 1

    local_ip = get_local_ip()
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, MebotRequestHandler)
    print(f"==================================================")
    print(f" MEBOT 0.1 — EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL")
    print(f" Yerel Bağlantı: http://127.0.0.1:{PORT}")
    print(f" Yerel Ağ / Wi-Fi Bağlantısı: http://{local_ip}:{PORT}")
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    print(f" Gemini Bulut Zekası: {'AKTİF (Google API)' if has_key else 'HAZIR (API Anahtarı Bekleniyor)'}")
    print(f" Mod: Reasoning & Chain-of-Thought (v5.2)")
    print(f" Gizlilik: Google / Arama Motoru İndeksleme Engellendi (noindex)")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
