/**
 * Resmi Gazete Keyword Tracker
 * Google Apps Script
 * * Bu script her sabah Resmi Gazete'yi tarar, belirlenen anahtar kelimeler
 * geçiyorsa kullanıcıya e-posta gönderir.
 * * Özellikler:
 * - Proxy desteği (CodeTabs) ile IP engellerini aşar.
 * - Windows-1254 karakter kodlamasını düzelterek Türkçe karakterleri korur.
 * - Dinamik tarih hesabı yapar.
 */

function resmiGazeteTara() {
  // --- AYARLAR / SETTINGS ---
  const emailAddress = Session.getActiveUser().getEmail();
  
  // Aranacak kelimeler listesi (Küçük harf kullanın)
  // List of keywords to search for (Use lowercase)
  const keywords = [
    "hastane", 
    "sağlık", 
    "acil", 
    "doktor", 
    "hekim", 
    "tabip", 
    "yoğun bakım"
  ];

  // --- TARİH VE URL / DATE & URL SETUP ---
  const now = new Date();
  const year = now.getFullYear();
  const month = (now.getMonth() + 1).toString().padStart(2, '0');
  const day = now.getDate().toString().padStart(2, '0');
  
  // Doğrudan HTML dosyasına giden yol / Direct path to the HTML file
  const targetUrl = `https://www.resmigazete.gov.tr/eskiler/${year}/${month}/${year}${month}${day}.htm`;
  
  // Proxy servisi (CORS ve IP engelini aşmak için)
  // Using CodeTabs proxy to bypass CORS and IP restrictions
  const proxyUrl = "https://api.codetabs.com/v1/proxy?quest=" + encodeURIComponent(targetUrl);

  console.log(`Hedef/Target: ${targetUrl}`);

  try {
    const response = UrlFetchApp.fetch(proxyUrl, {
      muteHttpExceptions: true,
      headers: { 'User-Agent': 'Mozilla/5.0' }
    });

    if (response.getResponseCode() !== 200) {
      console.log(`Gazete henüz yayınlanmamış veya erişilemiyor. Kod: ${response.getResponseCode()}`);
      return;
    }

    // --- ENCODING FIX ---
    // Resmi Gazete uses 'windows-1254'. We must decode the blob manually.
    const blob = response.getBlob();
    const html = blob.getDataAsString("windows-1254");
    
    // --- PARSING ---
    // Regex to find links and titles in the specific format of the site
    const regex = /<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi;
    
    let match;
    let foundItems = [];
    let addedTitles = [];

    while ((match = regex.exec(html)) !== null) {
      let rawLink = match[1];
      let rawTitle = match[2];
      
      // Clean HTML tags and special entities
      let title = rawTitle
        .replace(/<[^>]+>/g, '') 
        .replace(/&nbsp;/g, ' ')
        .replace(/–/g, '')
        .replace(/-/g, '')
        .trim();

      if (title.length < 5) continue; 

      // Fix relative links
      let finalLink = rawLink;
      if (finalLink.indexOf("http") === -1) {
         finalLink = `https://www.resmigazete.gov.tr/eskiler/${year}/${month}/${finalLink}`;
      }

      // Check keywords
      if (icerikUygunMu(title, keywords) && !addedTitles.includes(title)) {
        foundItems.push({ title: title, link: finalLink });
        addedTitles.push(title);
      }
    }
    
    // --- NOTIFICATION ---
    if (foundItems.length > 0) {
      sendNotificationEmail(emailAddress, foundItems, targetUrl);
    } else {
      console.log("Tarama tamamlandı. Eşleşen içerik bulunamadı.");
    }

  } catch (e) {
    console.error("Script Hatası: " + e.toString());
  }
}

function icerikUygunMu(title, keywords) {
  const lowerTitle = title.toLocaleLowerCase('tr-TR');
  // Ignore menu items
  if(lowerTitle.includes("yargı ilanları") || lowerTitle.includes("ihale") || lowerTitle.includes("döviz")) return false;
  
  return keywords.some(keyword => lowerTitle.includes(keyword.toLocaleLowerCase('tr-TR')));
}

function sendNotificationEmail(email, items, mainUrl) {
  const today = new Date().toLocaleDateString('tr-TR');
  let subject = `📢 Resmi Gazete (${today}) - İlgili İçerikler Bulundu`;
  
  let htmlBody = `<p>Bugünkü <a href="${mainUrl}">Resmi Gazete</a> içerisinde ilgini çekebilecek başlıklar:</p><ul>`;
  items.forEach(item => {
    htmlBody += `<li style="margin-bottom:10px;"><a href="${item.link}"><b>${item.title}</b></a></li>`;
  });
  htmlBody += "</ul><br><p><small>Bu e-posta Google Apps Script tarafından gönderilmiştir.</small></p>";
  
  MailApp.sendEmail({to: email, subject: subject, htmlBody: htmlBody});
  console.log(`E-posta gönderildi: ${items.length} adet içerik.`);
}