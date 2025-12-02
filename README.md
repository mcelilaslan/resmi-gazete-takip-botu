# 📰 Resmi Gazete Anahtar Kelime Takip Botu

Bu Google Apps Script projesi, her sabah **T.C. Resmi Gazete** web sitesini (resmigazete.gov.tr) tarar ve belirlediğiniz anahtar kelimeleri (örneğin: *sağlık, doktor, yönetmelik*) içeren bir madde yayınlandığında size otomatik olarak **e-posta** gönderir.

## 🚀 Özellikler

* **Akıllı Proxy Kullanımı:** Resmi Gazete'nin güvenlik duvarlarını ve IP kısıtlamalarını aşmak için Proxy altyapısı kullanır.
* **Karakter Seti Düzeltme:** Sitenin eski kodlamasından (Windows-1254) kaynaklanan Türkçe karakter sorunlarını (ş, ğ, ı vb.) otomatik düzeltir.
* **Tam Otomatik:** Google sunucularında çalışır, bilgisayarınızın açık olmasına gerek yoktur.
* **Doğrudan Linkleme:** E-postada gelen başlıklara tıkladığınızda direkt ilgili yönetmeliğe/karara gidersiniz.

## 🛠️ Kurulum

Bu botu kullanmak için herhangi bir yazılım indirmene gerek yok. Sadece bir Google hesabına ihtiyacın var.

1.  **Google Apps Script'e Git:**
    * [script.google.com](https://script.google.com/) adresine git.
    * Sol üstten **"Yeni Proje"** (New Project) butonuna tıkla.

2.  **Kodu Yapıştır:**
    * Açılan editördeki varsayılan kodları sil.
    * Bu repodaki `code.gs` dosyasının içeriğini kopyala ve editöre yapıştır.
    * Projeye bir isim ver (Örn: *Resmi Gazete Botu*).

3.  **Kelimeleri Düzenle:**
    * Kodun başındaki `keywords` listesini kendine göre düzenle:
    ```javascript
    const keywords = ["hastane", "sağlık", "ihale", "enerji"];
    ```

4.  **Test Et:**
    * Editörde **"Çalıştır"** (Run) butonuna bas.
    * İlk seferde Google senden "İzin" isteyecektir. İzinleri ver (Gelişmiş -> Güvenli Değil Git diyerek onayla).

5.  **Otomatikleştir (Zamanlayıcı Kur):**
    * Sol menüden **Saat Simgesine** (Tetikleyiciler / Triggers) tıkla.
    * **Tetikleyici Ekle** butonuna bas.
    * **Etkinlik Kaynağı:** `Zaman Odaklı`
    * **Tetikleyici Türü:** `Gün Zamanlayıcısı`
    * **Saat:** `07:00 ile 08:00` arasını seç.
    * **Kaydet** de.

Artık script her sabah Resmi Gazete'yi senin için okuyacak! ☕

## ⚠️ Yasal Uyarı

Bu script açık kaynaklı bir eğitim projesidir. **resmigazete.gov.tr** ile resmi bir bağlantısı yoktur. Site yapısında (HTML DOM) yapılacak değişiklikler botun çalışmasını durdurabilir. Sorumluluk kullanıcıya aittir.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.