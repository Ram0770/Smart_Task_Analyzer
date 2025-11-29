# Smart Task Analyzer

A full working Django backend + simple frontend to analyze and prioritize tasks based on due date, importance, estimated effort, and dependencies.

## Quick setup (local development)

1. Create & activate virtualenv
   python3 -m venv venv
   source venv/bin/activate

2. Install requirements
   pip install -r requirements.txt

3. Run migrations
   python manage.py migrate

4. Start server
   python manage.py runserver 127.0.0.1:8000

5. Serve frontend (optional)
   cd frontend
   python -m http.server 8080

Open http://127.0.0.1:8080/index.html
