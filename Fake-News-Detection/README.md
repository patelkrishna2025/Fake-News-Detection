# AI Fake News Detection Web Application

A complete, **100% offline** Fake News Detection system built with Flask and
classical Machine Learning (TF-IDF + scikit-learn). No OpenAI/Gemini/Claude/
Hugging Face APIs or any cloud service is used anywhere.

## Features
- Real/Fake prediction with confidence score and probabilities
- Explainable AI: shows the keywords that influenced the prediction
- Dashboard with live charts (Chart.js)
- Full prediction history with search (keyword / date / type)
- Analytics: word frequency, weekly trends, model metrics
- Admin panel: delete records, export CSV, view system logs
- PDF report generation per prediction (ReportLab)
- Dark mode, responsive Bootstrap 5 UI

## Project Structure
```
Fake-News-Detection/
├── app.py                  # Flask entry point
├── train_model.py          # ML training pipeline
├── requirements.txt
├── dataset/                # Fake.csv / True.csv (+ generator script)
├── database/               # SQLite DB + schema
├── routes/                 # Flask blueprints
├── utils/                  # preprocessing, inference, db helpers
├── saved_model/            # trained model.pkl, vectorizer.pkl, metadata.json
├── templates/               # Jinja2 HTML templates
└── static/                  # css, js, images
```

## Setup & Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) If you have the original Kaggle "Fake and Real News" dataset,
   place `Fake.csv` and `True.csv` inside `dataset/`. Otherwise generate a
   synthetic dataset offline:
   ```bash
   python dataset/generate_dataset.py
   ```

3. Train the model (creates `saved_model/model.pkl` etc.):
   ```bash
   python train_model.py
   ```

4. Initialize the database (also done automatically on app start):
   ```bash
   python database/init_db.py
   ```

5. Run the app:
   ```bash
   python app.py
   ```

6. Open **http://127.0.0.1:5000** in your browser.

## Routes
| Route | Description |
|---|---|
| `/` | Home / analyze page |
| `/predict` (POST) | Run prediction (form-encoded: title, article) |
| `/dashboard` | Stats dashboard |
| `/history` | Prediction history + search |
| `/analytics` | Word frequency & model metrics |
| `/admin` | Admin panel (delete, export, logs) |
| `/report/<id>` | Download PDF report |
| `/api/predict`, `/api/history`, `/api/stats` | JSON APIs used by frontend |

## Notes
- Using your own real dataset will give meaningful real-world accuracy.
  The bundled synthetic generator is only for demoing/testing the full
  pipeline end-to-end without internet access.
- Swap `LogisticRegression` etc. parameters in `train_model.py` and re-run
  to retrain with different settings.
