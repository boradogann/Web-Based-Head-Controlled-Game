# 🍌 Minion 3D Runner (TensorFlow.js & Streamlit)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)
![TensorFlow.js](https://img.shields.io/badge/TensorFlow.js-BlazeFace-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Minion 3D Runner**, tarayıcı üzerinden web kamerasını kullanarak **yüz hareketleriyle (kafa eğme)** kontrol edilen, TensorFlow.js (BlazeFace) ve HTML5 Canvas destekli 3D perspektifli bir sonsuz koşu oyunudur. 

Görüntü işleme ve yapay zeka modelleri **doğrudan istemci tarafında (tarayıcıda)** çalıştığı için kamera verileriniz hiçbir sunucuya aktarılmaz; tamamen gizli ve yüksek performanslıdır.

---

## 🎮 Oyun Özellikleri & Görsel Tasarım

- **Yüz Takibi ile Kontrol:** BlazeFace AI modeli sayesinde kafanızı sağa/sola eğip merkeze getirerek Minyonu şeritler arasında yönlendirin.
- **Pseudo-3D Derinlik Efekti:** Perspektif yol tasarımı ve Z-ekseni üzerinde yaklaşan engeller ile Subway Surfers tarzı oynanış.
- **Dinamik Vektörel Minyon:** Harici görsel yükleme sorunlarına (CORS) takılmayan, Canvas üzerinde canlı çizilen ikonik Minyon karakteri.
- **Zengin Engeller & Paralaks Arka Plan:** Trenler (🚆), barikatlar (🚧), çöp kovaları (🗑️) ve yol kenarında kayan paralaks gece şehri ile ağaç/lamba efektleri.
- **Yumuşak Geçiş (Lerp):** Şerit değişimlerinde anında ışınlanma yerine yumuşatılmış akıcı animasyonlar.

---

## 🛠️ Teknolojiler ve Kütüphaneler

- **Frontend & Game Engine:** HTML5 Canvas, JavaScript (ES6)
- **Computer Vision & AI:** [TensorFlow.js](https://www.tensorflow.org/js), [BlazeFace Model](https://github.com/tensorflow/tfjs-models/tree/master/blazeface)
- **Web Framework:** [Streamlit](https://streamlit.io/)

---

## 🚀 Yerel Bilgisayarda Çalıştırma (Local Setup)

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

1. **Depoyu klonlayın:**
   ```bash
   git clone [https://github.com/KULLANICI_ADI/minion-runner.git](https://github.com/KULLANICI_ADI/minion-runner.git)
   cd minion-runner
