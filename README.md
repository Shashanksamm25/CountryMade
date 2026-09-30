# Country Made (Streamlit + PostgreSQL)

```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

createdb jeans
psql -d jeans -f schema.sql
# edit .streamlit/secrets.toml with your DB password
python seed_admin.py

streamlit run app.py
```

Put slideshow images in `assets/slides/` and reviewer photos in `assets/reviewers/`.
