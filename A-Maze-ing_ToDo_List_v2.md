# A-Maze-ing Proje Planı ve İş Bölümü (v2.2)

Bu doküman, A-Maze-ing projesinin tüm gereksinimlerini eksiksiz yerine getirmek ve takım içi iş bölümünü organize etmek amacıyla güncellenmiştir. Proje, Python 3.10+ standartlarına, 42 müfredatına ve nesne yönelimli mimariye uygun olarak geliştirilmektedir. 

---

## 🏗️ Faz 1: Proje Kurulumu ve Araçlar
Projenin temel iskeletinin ve kalite kontrol mekanizmalarının kurulması.

- [ ] **Ortam İzolasyonu:** Python sanal ortamının (venv) oluşturulması.
- [ ] **Makefile Entegrasyonu:**
  - `install`: Bağımlılıkların yüklenmesi.
  - `run`: `python3 a_maze_ing.py config.txt` komutunun tetiklenmesi.
  - `debug`: `pdb` entegrasyonu ile debug modu.
  - `clean`: `__pycache__`, `.mypy_cache` temizliği.
  - `lint`: `flake8 .` ve `mypy .` komutlarının çalıştırılması (zorunlu kurallar: `--warn-return-any`, `--disallow-untyped-defs`, vb.).
- [ ] **Tip Kontrolü ve Linter:** Statik tip ipuçlarının (Type Hints) tüm modüllerde zorunlu kılınması.

---

## ⚙️ Faz 2: Yapılandırma (Config) Yönetimi — ✅ **[TAMAMLANDI]**
*Bu aşama başarıyla bitirildi. Takım, `config.txt` dosyasını okuyan ve ayrıştıran `ConfigParser` modülünü hazır hale getirdi.*

- [x] `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE` ve `PERFECT` değerlerinin okunması.
- [x] Yorum satırlarının (`#`) yoksayılması.
- [x] Hata yakalama (Dosya bulunamadı, eksik anahtar, geçersiz format).

---

## 🧠 Faz 3: Algoritma Mimarisi ve Harita Üretimi (Core Generation)
Harita üretimi (Generation) için 4 eksenli bölge mantığının uygulanması.

- [ ] **Bölgesel (Quadrant) Mimari:**
  - Haritanın yatay ve dikey eksenlerle dört ana bölgeye ayrılması (özellikle varsayılan `PERFECT=False` / Pac-Man modu için).
  - Bölgeler arası geçişi sağlamak üzere eksenler üzerinde "kapıların" (bağlantı noktalarının) rastgele belirlenmesi.
- [ ] **Oyun Alanı (Pac-Man) Kuralları (`PERFECT=False`):**
  - **Döngüler (Loops):** `maze_analyzer.py` analiz aracından geçecek şekilde minimum 2 bağımsız rotanın oluşturulması.
  - **Açık Alan Kısıtlaması:** Koridorların maksimum 2 hücre genişliğinde olması (3x3 açık alanların engellenmesi).
  - **Stratejik Noktalar:** 4 köşe ve haritanın merkez hücresinin **kesinlikle** açık koridor olarak ayarlanması.
- [ ] **Sabit "42" Deseni:**
  - Tamamen kapalı hücrelerden oluşan "42" deseninin, eksenlerin veya bölgesel kapıların üzerine denk gelmeyecek uygun bir koordinata yerleştirilmesi.
- [ ] **Akademik Mod (`PERFECT=True`):**
  - Labirentin sadece tek bir çözüm yolu olacak şekilde (döngüsüz) üretilmesi (Örn: Recursive Backtracker veya Prim algoritması ile).

---

## 🗺️ Faz 4: Arama Algoritması (Pathfinding) ve Çıktı
Oluşturulan labirentte giriş ve çıkış noktaları arasındaki en kısa yolun bulunması ve dosyaya işlenmesi.

- [ ] **Optimize Edilmiş Yol Bulma:**
  - Zaman karmaşıklığını düşürmek için tüm haritayı taramak yerine, **bölgesel kapıları düğüm (node) olarak kabul eden** BFS veya A* algoritmasının uygulanması.
- [ ] **Duvar Kodlaması (Hexadecimal Coherence):**
  - Her hücrenin duvar durumunun bitwise mantığıyla (Kuzey=1, Doğu=2, Güney=4, Batı=8) toplanarak tek bir onaltılık (0-F) basamağa çevrilmesi.
  - `maze_analyzer.py`'nin hata vermemesi için komşu hücrelerin duvarlarının tutarlı (coherent) olması (Örn: A'nın doğu duvarı kapalıysa, sağındaki B'nin batı duvarı da kapalı olmalı).
- [ ] **Çıktı (Output) Formatı:**
  - Haritanın hex formatında dosyaya yazdırılması.
  - Boş bir satırdan sonra `ENTRY` koordinatı, `EXIT` koordinatı ve `PATH` (N, E, S, W karakterleri) bilgilerinin eklenmesi.

---

## 🎨 Faz 5: Görselleştirme (UI/UX)
Kullanıcının labirenti görsel olarak inceleyebilmesi.

- [ ] **Arayüz Seçimi:** Terminal ASCII/ANSI render motoru veya MiniLibX (MLX) entegrasyonunun tamamlanması.
- [ ] **Etkileşimli Komutlar:**
  - Yeni labirent üretimi (Re-generate).
  - Çözüm yolunun gösterilmesi/gizlenmesi.
  - Duvar/Yol renklerinin isteğe bağlı değiştirilmesi.
  - "42" deseninin farklı bir renkle vurgulanması (Opsiyonel).

---

## 📦 Faz 6: Kod Kalitesi, Paketleme ve Dokümantasyon
Modülün yeniden kullanılabilir, standartlara uygun bir paket haline getirilmesi.

- [ ] **Nesne Yönelimli Tasarım & Hata Yönetimi:**
  - Mantığın `MazeGenerator` isimli bağımsız bir sınıf içinde kapsüllenmesi.
  - Olası çökmeleri önlemek için `try-except` bloklarının ve `with` (context manager) yapılarının kusursuz kullanımı.
- [ ] **Python Paketi (Reusability):**
  - Üretim modülünün `mazegen-*` adında, `pip` ile kurulabilir bir `.whl` veya `.tar.gz` paketi olarak yapılandırılması (örn: `pyproject.toml` ile).
- [ ] **Dokümantasyon (README & Lisans):**
  - 42 müfredatı standart tanıtım cümlesinin eklenmesi.
  - Sınıflar ve fonksiyonlar için Google/NumPy stili Docstring'lerin (PEP 257) yazılması.
  - `LICENSE.md` dosyasının oluşturulması ve proje açık kaynak lisansının belirlenmesi.
  - Algoritma seçimlerinin (bölgelere ayırma, kapı düğümleri vb.) nedenleriyle birlikte README'ye eklenmesi.
