# 📰 Resmi Gazete Anahtar Kelime Takip Botu

Bu proje her sabah **T.C. Resmi Gazete** web sitesini (resmigazete.gov.tr) tarar, belirlenen anahtar kelimeleri içeren maddeleri bulur, Gemini API ile kısa bir özet çıkarır ve e-posta ile bildirir.

> **Not:** Proje ilk sürümünde Google Apps Script üzerinde çalışıyordu (bkz. `legacy/code.gs`). resmigazete.gov.tr, Google sunucularının IP aralıklarından gelen istekleri engellemeye başladığından, proje **kendi sunucunuzda (self-hosted) Docker ile çalışan bir Python servisine** taşındı.

## 🚀 Özellikler

- Anahtar kelime bazlı filtreleme (hastane, sağlık, doktor, yoğun bakım vb.)
- Gemini ile branşa özel (anestezi/reanimasyon odaklı) otomatik özet
- Türkçe karakter/encoding (Windows-1254) düzeltmesi
- Docker ile kendi sunucunuzda 7/24 çalışır, harici bir servise bağımlı değildir
- Her gün saat 08:00'da otomatik tarama + container başlangıcında bir kerelik test taraması

## 🛠️ Kurulum (Docker ile self-hosted)

1. **Repoyu klonla:**
```bash
   git clone https://github.com/mcelilaslan/resmi-gazete-takip-botu.git
   cd resmi-gazete-takip-botu
```

2. **.env dosyasını oluştur:**
```bash
   cp .env.example .env
   nano .env
```
   İçine kendi Gemini API key'ini ve Gmail bilgilerini yaz:

GEMINI_API_KEY=...
GMAIL_USER=...
GMAIL_APP_PASSWORD=...

   Gmail için normal şifreniz değil, [Uygulama Şifresi](https://myaccount.google.com/apppasswords) kullanmanız gerekir.

3. **Anahtar kelimeleri düzenle (opsiyonel):**
   `main.py` içindeki `KEYWORDS` listesini kendine göre değiştir.

4. **Başlat:**
```bash
   docker compose up -d --build
```

5. **Logları izle:**
```bash
   docker compose logs -f
```

## ⚠️ Güvenlik Notu

`.env` dosyanızı **asla** git'e eklemeyin — `.gitignore` bunu zaten engelliyor. API key'lerinizi kod içine hardcode etmeyin.

## ⚠️ Yasal Uyarı

Bu proje açık kaynaklı bir kişisel/eğitim projesidir. **resmigazete.gov.tr** ile resmi bir bağlantısı yoktur. Site yapısında yapılacak değişiklikler botun çalışmasını durdurabilir. Sorumluluk kullanıcıya aittir.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE.txt) ile lisanslanmıştır.
