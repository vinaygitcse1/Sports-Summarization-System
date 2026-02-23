# 🏏 Match Summarizer: AI Cricket Commentary Assistant

An intelligent web application designed to process and analyze noisy sports commentary. It uses Advanced Audio Processing and Natural Language Processing (NLP) to convert audio to text, reduce stadium noise, extract match highlights, and generate highly accurate summaries.

## ✨ Key Features
* **🎙️ Audio to Text Transcription:** Converts raw cricket commentary audio into text using Google Speech API.
* **🔇 Advanced Noise Reduction:** Implements `scipy` and `noisereduce` to filter out high-pitch stadium crowd noise and boost commentator vocals (Bandpass Filter: 100Hz - 7500Hz).
* **📊 Visual Waveform Generation:** Automatically generates before/after audio waveform charts using `matplotlib`.
* **🧠 Entity Extraction (NER):** Custom NLP pipeline using `spaCy` to intelligently identify Teams, Venues, and Players (even handling cricket slangs and specific names).
* **🔥 Sentiment Analysis:** Analyzes the mood of the commentary (Exciting/Disappointing) using NLTK VADER.
* **📝 Generative AI Summarization:** Uses Hugging Face's `BART-large-cnn` model to generate concise, readable match summaries.
* **💾 Database Integration:** Saves user history and past summaries using MongoDB.

## 🛠️ Tech Stack
* **Backend:** Python, Flask
* **Audio Processing:** SciPy, NumPy, NoiseReduce, Wave
* **NLP & AI:** Hugging Face API (BART), SpaCy, NLTK (VADER), Google SpeechRecognition
* **Frontend:** HTML5, CSS3, Bootstrap, FontAwesome
* **Database:** MongoDB
* **Data Visualization:** Matplotlib

