import os
import time
import requests
import smtplib
import schedule
import pytz
from datetime import datetime
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai

# --- AYARLAR ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

if not all([GEMINI_API_KEY, GMAIL_USER, GMAIL_APP_PASSWORD]):
    raise SystemExit("Eksik ortam değişkeni: GEMINI_API_KEY, GMAIL_USER, GMAIL_APP_PASSWORD .env dosyasında tanımlı olmalı.")
HEDEF_EMAIL = "muhammedcelilaslan@gmail.com"

GEMINI_MODEL = "gemini-flash-latest"

KEYWORDS = ["hastane", "sağlık", "acil", "tıp", "doktor", "hekim", "tabip", "yoğun bakım", "tedavi", "tıpta uzmanlık"]
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
}


def icerik_uygun_mu(title):
    lower_title = title.lower().replace('İ', 'i').replace('I', 'ı')
    if any(x in lower_title for x in ["yargı ilanları", "ihale", "döviz", "kur karar"]):
        return False
    return any(keyword.lower() in lower_title for keyword in KEYWORDS)


def call_gemini_api(text, title):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""Sen uzman doktorlar için Resmi Gazete tarayan kıdemli bir Tıbbi Mevzuat Danışmanısın.
        Hedef kitlen: Kamuda veya Üniversitede çalışan bir Anestezi Uzmanı.

        ELEME GÖREVİ: Aşağıdaki metni oku. Eğer bu metin doktorların özlük hakları, hastane işleyişi, tıbbi uygulamalar, ilaç/cihaz yönetimi veya sağlık personeli ile ilgili DEĞİLSE (Örneğin: Tarım, İnşaat, Veterinerlik, Turizm, Çevre Düzenlemesi vb. ise), çıktı olarak SADECE tek kelime yaz: "ALAKASIZ". Başka hiçbir şey yazma.

        ASIL GÖREV:
        Aşağıdaki metni analiz et ve şu kurallara SIKI SIKIYA uy:
        1. METNE SADIK KAL: Metinde yazmayan bir şeyi varmış gibi uydurma.
        2. ANESTEZİ FİLTRESİ: Eğer metinde doğrudan "Anestezi", "Reanimasyon" veya "Yoğun Bakım" geçmiyorsa, "Anesteziye özel bir madde yoktur" diyerek genel doktorları ilgilendiren kısımları anlat.
        3. ODAK NOKTALARI: Şu soruların cevabını ara: Ek ödeme, döner sermaye veya maaş etkileniyor mu? Nöbet, çalışma saatleri veya görev yeri değişimi var mı? Yasal sorumluluk değişiyor mu?
        4. ÜSLUP: Somut verileri çek ("Usul belirlendi" yerine "Ek ödemeden %50 pay verilecek" gibi).

        Çıktıyı şu formatta ver (Maksimum 3 madde):
        - <b>[Özet]:</b> Konunun ne olduğu (Tek cümle).<br>
        - <b>[Etki]:</b> Doktorun cebine veya çalışma hayatına somut etkisi (Varsa).<br>
        - <b>[Anestezi]:</b> Branşa özel bir durum var mı?<br>

        Başlık: {title}
        Metin: {text}"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        cevap = response.text.strip()
        if "ALAKASIZ" in cevap:
            return None
        return cevap
    except Exception as e:
        print(f"❌ Gemini Hatası ({title[:40]}...): {e}")
        return None


def get_page_content(url):
    try:
        res = fetch_with_ssl_retry(url)
        if res is None:
            return ""
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator=' ')
        clean_text = ' '.join(text.split())
        return clean_text[:15000]
    except Exception as e:
        print(f"❌ İçerik çekilemedi ({url}): {e}")
        return ""


def fetch_with_ssl_retry(url, timeout=15):
    try:
        return requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.exceptions.SSLError as e:
        print(f"⚠️ SSL doğrulama hatası, doğrulamasız tekrar deneniyor ({url}): {e}")
        try:
            return requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        except Exception as e2:
            print(f"❌ Doğrulamasız deneme de başarısız ({url}): {e2}")
            return None
    except Exception as e:
        print(f"❌ Genel Hata ({url}): {e}")
        return None


def send_email(items, target_url, gazete_tarihi):
    if not items:
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📢 Resmi Gazete ({gazete_tarihi}) - Sizi İlgilendiren {len(items)} Karar"
    msg['From'] = f"Resmi Gazete Botu <{GMAIL_USER}>"
    msg['To'] = HEDEF_EMAIL

    html_body = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
      <h3 style="color: #d32f2f; border-bottom: 2px solid #d32f2f; padding-bottom: 10px;">Bugünün Resmi Gazetesi Özetleri</h3>
      <ul style="padding-left: 0; list-style-type: none;">
    """

    for item in items:
        html_body += f"""
        <li style="margin-bottom: 25px; border: 1px solid #ddd; padding: 15px; border-radius: 8px;">
          <a href="{item['link']}" style="font-size: 16px; font-weight: bold; text-decoration: none; color: #1a73e8; display: block; margin-bottom: 10px;">
            {item['title']}
          </a>
          <div style="background-color: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 4px solid #1a73e8; font-size: 14px; line-height: 1.5;">
            {item['summary']}
          </div>
        </li>
        """

    html_body += f"""
      </ul>
      <p style="font-size: 12px; color: #666; text-align: center; margin-top: 30px;">
        Bu özet <b>Gemini</b> ile ev sunucunuz üzerinden otomatik oluşturulmuştur.<br>
        <a href="{target_url}" style="color: #1a73e8;">Resmi Gazete Tüm Fihrist</a>
      </p>
    </div>
    """

    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, HEDEF_EMAIL, msg.as_string())
        server.quit()
        print(f"✅ E-posta {HEDEF_EMAIL} adresine gönderildi!")
    except Exception as e:
        print(f"❌ E-posta gönderim hatası: {e}")


def resmi_gazete_tara():
    tz = pytz.timezone('Europe/Istanbul')
    now = datetime.now(tz)
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    date_str = now.strftime('%d.%m.%Y')

    target_url = f"https://www.resmigazete.gov.tr/eskiler/{year}/{month}/{year}{month}{day}.htm"
    print(f"\n[{now.strftime('%H:%M:%S')}] Hedef URL taranıyor: {target_url}")

    try:
        response = fetch_with_ssl_retry(target_url)
        if response is None:
            print("⚠️ Sayfa hiç açılamadı (SSL/bağlantı hatası).")
            return
        if response.status_code != 200:
            print(f"⚠️ Sayfa açılamadı. Kod: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='windows-1254')
        links = soup.find_all('a', href=True)

        found_items = []

        for link in links:
            raw_title = link.text.strip().replace('\n', ' ').replace('\r', '')
            title = ' '.join(raw_title.split())
            href = link['href']

            if len(title) < 5:
                continue

            if icerik_uygun_mu(title):
                final_link = href if href.startswith('http') else f"https://www.resmigazete.gov.tr/eskiler/{year}/{month}/{href}"
                print(f"🔍 İnceleniyor: {title[:50]}...")

                content_text = get_page_content(final_link)
                if content_text:
                    ai_summary = call_gemini_api(content_text, title)
                    if ai_summary:
                        print("✨ AI Eşleşmesi Bulundu!")
                        found_items.append({
                            'title': title,
                            'link': final_link,
                            'summary': ai_summary
                        })

        if found_items:
            send_email(found_items, target_url, date_str)
        else:
            print("📭 Bugünkü gazetede ilgili içerik bulunamadı.")

    except Exception as e:
        print(f"❌ Genel Hata: {e}")


if __name__ == "__main__":
    print("🤖 Resmi Gazete Botu Başlatıldı. Her sabah 08:00'da tarama yapacak.")

    resmi_gazete_tara()

    schedule.every().day.at("08:00").do(resmi_gazete_tara)

    while True:
        schedule.run_pending()
        time.sleep(60)
