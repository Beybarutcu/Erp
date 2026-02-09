# Plastik Kalıp Üretim ERP Sistemi - Hızlı Başlangıç
# Plastic Mold Manufacturing ERP System - Quick Start

## 🎯 Sistem Özellikleri / System Features

### Türkçe
✅ **Tam Türkçe Arayüz** - Tüm menüler ve formlar Türkçe  
✅ **Kalıp Yönetimi** - Kalıp kodları, gözlü sayısı, çevrim süreleri  
✅ **Hammadde Takibi** - Plastik reçine ve malzeme stok kontrolü  
✅ **Üretim Emirleri** - Detaylı üretim planlaması ve takibi  
✅ **Fire Takibi** - Üretim fire ve kayıp analizi  
✅ **Kalite Kontrol** - Numune bazlı kalite izleme  
✅ **Makine Ataması** - Makine ve operatör takibi  
✅ **Detaylı Raporlar** - Üretim verimliliği, kalıp kullanımı  

### English
✅ **Full Turkish Interface** - All menus and forms in Turkish  
✅ **Mold Management** - Mold codes, cavity count, cycle times  
✅ **Raw Material Tracking** - Plastic resin and material stock control  
✅ **Production Orders** - Detailed production planning and tracking  
✅ **Scrap Tracking** - Production waste and loss analysis  
✅ **Quality Control** - Sample-based quality monitoring  
✅ **Machine Assignment** - Machine and operator tracking  
✅ **Detailed Reports** - Production efficiency, mold utilization  

## 📦 Kurulum / Installation

### Adım 1: Dosyaları İndirin / Step 1: Download Files
```bash
# ZIP dosyasını açın / Extract the ZIP file
unzip manufacturing-erp-turkish.zip
cd manufacturing-erp-turkish
```

### Adım 2: Bağımlılıkları Yükleyin / Step 2: Install Dependencies
```bash
pip install Flask==3.0.0 Werkzeug==3.0.1
```

### Adım 3: Uygulamayı Başlatın / Step 3: Start Application
```bash
python app.py
```

### Adım 4: Tarayıcıda Açın / Step 4: Open in Browser
```
http://localhost:5000
```

### Adım 5: Giriş Yapın / Step 5: Login
```
Kullanıcı Adı / Username: admin
Şifre / Password: admin123
```

## 🏭 Plastik Üretim İçin Kullanım / Usage for Plastic Manufacturing

### 1. Kalıpları Ekleyin / Add Molds

**Türkçe:**
1. Yan menüden "Kalıplar" seçin
2. "+ Kalıp Ekle" butonuna tıklayın
3. Kalıp bilgilerini girin:
   - Kalıp Kodu: Ö unique kod (ör: K-001)
   - Kalıp Adı: Tanımlayıcı isim
   - Gözlü Sayısı: Kaç gözlü (ör: 4, 8, 16)
   - Malzeme Tipi: PP, PE, ABS, vb.
   - Tonaj: Gerekli makine tonajı
   - Çevrim Süresi: Saniye cinsinden
   - Durum: Aktif/Bakımda/Pasif
   - Konum: Depo konumu

**English:**
1. Select "Molds" from sidebar
2. Click "+ Add Mold"
3. Enter mold information:
   - Mold Code: Unique code (e.g., K-001)
   - Mold Name: Descriptive name
   - Cavity Count: Number of cavities (e.g., 4, 8, 16)
   - Material Type: PP, PE, ABS, etc.
   - Tonnage: Required machine tonnage
   - Cycle Time: In seconds
   - Status: Active/Maintenance/Inactive
   - Location: Storage location

### 2. Hammaddeleri Tanımlayın / Define Raw Materials

**Türkçe:**
1. "Hammaddeler" menüsüne gidin
2. "+ Hammadde Ekle" tıklayın
3. Bilgileri doldurun:
   - Malzeme Kodu: Ö kod (ör: PP-001)
   - Malzeme Adı: Tam isim
   - Tip: Polipropilen, Polietilen, vb.
   - Kalite: Virgin, Recycled, vb.
   - Tedarikçi: Listeden seçin
   - Stok Miktarı: kg cinsinden
   - Birim Fiyat: kg başı fiyat
   - Yeniden Sipariş Seviyesi: Minimum stok

**English:**
1. Go to "Raw Materials" menu
2. Click "+ Add Raw Material"
3. Fill information:
   - Material Code: Unique code (e.g., PP-001)
   - Material Name: Full name
   - Type: Polypropylene, Polyethylene, etc.
   - Grade: Virgin, Recycled, etc.
   - Supplier: Select from list
   - Stock Quantity: in kg
   - Unit Price: price per kg
   - Reorder Level: minimum stock

### 3. Ürünleri Kaydedin / Register Products

**Türkçe:**
1. "Envanter" sayfasına gidin
2. Ürün eklerken:
   - Ürün Tipi: Mamul Ürün
   - Kalıp: Hangi kalıpla üretildiğini seçin
   - Malzeme Kalitesi: Kullanılan malzeme
   - Renk: Ürün rengi
   - Ağırlık: Gram cinsinden
   - Ölçüler: Boyutlar
   - Teknik Resim No: Varsa

**English:**
1. Go to "Inventory" page
2. When adding product:
   - Product Type: Finished Good
   - Mold: Select which mold produces it
   - Material Grade: Material used
   - Color: Product color
   - Weight: in grams
   - Dimensions: Measurements
   - Drawing Number: If available

### 4. Üretim Emri Oluşturun / Create Production Order

**Türkçe:**
1. "Üretim" menüsünden "+ Yeni Üretim"
2. Formu doldurun:
   - Ürün: Üretilecek ürünü seçin
   - Kalıp: Kullanılacak kalıbı seçin
   - Planlanan Miktar: Hedef adet
   - Üretim Tarihi: İş tarihi
   - Operatör: İşi yapacak kişi
   - Makine: Makine numarası
   - Hammadde: Kullanılacak malzeme
   - Durum: Bekliyor/Devam Ediyor/Tamamlandı

**English:**
1. From "Production" menu select "+ New Production"
2. Fill the form:
   - Product: Select product to produce
   - Mold: Select mold to use
   - Planned Quantity: Target pieces
   - Production Date: Work date
   - Operator: Person doing the work
   - Machine: Machine number
   - Raw Material: Material to use
   - Status: Pending/In Progress/Completed

### 5. Üretim Tamamlama / Complete Production

**Türkçe:**
Üretim tamamlandığında:
- Üretilen Miktar: Gerçek üretim adedi
- Fire Miktarı: Hatalı/atık parça sayısı
- Kullanılan Malzeme: kg cinsinden gerçek kullanım
- Gerçek Çevrim Süresi: Ortalama süre
- Durum: "Tamamlandı" olarak işaretleyin

**English:**
When production is completed:
- Produced Quantity: Actual production count
- Scrap Quantity: Defective/waste piece count
- Material Used: Actual usage in kg
- Actual Cycle Time: Average time
- Status: Mark as "Completed"

### 6. Kalite Kontrolü / Quality Control

**Türkçe:**
1. Tamamlanan üretim emri için
2. Kalite kontrolü ekleyin:
   - Numune Boyutu: Kontrol edilen parça sayısı
   - Geçen Sayısı: Başarılı parçalar
   - Kalan Sayısı: Hatalı parçalar
   - Hata Tipleri: Çizik, hava kabarcığı, vb.
   - Sonuç: Geçti/Kaldı
   - Düzeltici Faaliyet: Yapılan aksiyonlar

**English:**
1. For completed production order
2. Add quality control:
   - Sample Size: Number of pieces checked
   - Passed Count: Successful pieces
   - Failed Count: Defective pieces
   - Defect Types: Scratch, air bubble, etc.
   - Result: Passed/Failed
   - Corrective Action: Actions taken

## 📊 Raporlar / Reports

### Üretim Verimliliği / Production Efficiency
- Toplam üretim / Total production
- Toplam fire / Total scrap
- Ortalama verimlilik % / Average efficiency %

### Kalıp Kullanımı / Mold Utilization
- En çok kullanılan kalıplar / Most used molds
- Toplam atış sayıları / Total shot counts
- Bakım gereksinimi / Maintenance needs

### Hammadde Tüketimi / Material Consumption
- Malzeme bazında kullanım / Usage by material
- Stok seviyeleri / Stock levels
- Yeniden sipariş uyarıları / Reorder alerts

### Fire Analizi / Scrap Analysis
- Ürün bazında fire oranı / Scrap rate by product
- Kalıp bazında fire / Scrap by mold
- Fire nedenleri / Scrap reasons

## 🎨 Dil Değiştirme / Change Language

Sağ üst köşeden TR/EN butonları ile dil değiştirebilirsiniz.
Use TR/EN buttons in top right corner to change language.

## 💾 Veri Yedekleme / Data Backup

**Önemli / Important:**
```bash
# Veritabanını yedekleyin / Backup database
cp database/erp.db database/erp_backup_$(date +%Y%m%d).db
```

Haftalık yedekleme önerilir / Weekly backup recommended

## 🔧 Özelleştirme / Customization

### Şirket Logosu Eklemek / Add Company Logo
1. Logonuzu `static/images/logo.png` olarak kaydedin
2. `templates/base.html` dosyasında logo bölümünü güncelleyin

### Ek Alanlar Eklemek / Add Custom Fields
1. Veritabanına sütun ekleyin
2. Formları güncelleyin
3. Gösterim sayfalarını düzenleyin

### Rapor Şablonları / Report Templates
`templates/reports.html` dosyasını düzenleyerek özelleştirebilirsiniz

## 📞 Destek / Support

### Sık Sorulan Sorular / FAQ

**S: Kalıp bakım tarihleri otomatik hesaplanıyor mu?**  
C: Şu anda manuel girilmeli. Gelecek versiyonda atış sayısına göre otomatik hesaplanacak.

**Q: Are mold maintenance dates calculated automatically?**  
A: Currently manual entry. Future version will calculate based on shot count.

**S: Fire oranı %5'i geçerse uyarı veriyor mu?**  
C: Raporlarda görülebilir, otomatik uyarı özelliği eklenebilir.

**Q: Does it alert if scrap rate exceeds 5%?**  
A: Visible in reports, automatic alerts can be added.

**S: Hangi hammadde tipleri destekleniyor?**  
C: Tüm plastik türleri eklenebilir: PP, PE, PET, ABS, PC, vb.

**Q: Which material types are supported?**  
A: All plastic types can be added: PP, PE, PET, ABS, PC, etc.

## 🚀 Gelişmiş Özellikler / Advanced Features

### Planlanan Geliştirmeler / Planned Enhancements
- [ ] Barkod entegrasyonu / Barcode integration
- [ ] Otomatik bakım planlaması / Automatic maintenance scheduling
- [ ] Mobil uygulama / Mobile app
- [ ] E-posta bildirimleri / Email notifications
- [ ] Gelişmiş grafikler / Advanced charts
- [ ] Excel export / Excel export
- [ ] Çoklu lokasyon / Multi-location support

## 📈 Başarı Metrikleri / Success Metrics

Sistem ile takip edebilecekleriniz:
- ✅ Günlük üretim miktarları
- ✅ Kalıp performansları
- ✅ Fire oranları
- ✅ Operatör verimliliği
- ✅ Malzeme tüketimi
- ✅ Üretim maliyetleri
- ✅ Teslimat performansı

What you can track with the system:
- ✅ Daily production quantities
- ✅ Mold performances
- ✅ Scrap rates
- ✅ Operator efficiency
- ✅ Material consumption
- ✅ Production costs
- ✅ Delivery performance

---

**Başarılar dileriz! / Good luck!**

Plastik Kalıp ve Ürün Üretimi için özel olarak tasarlanmış ERP sisteminiz hazır!
Your ERP system specifically designed for Plastic Mold and Product Manufacturing is ready!
