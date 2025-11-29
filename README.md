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
```

## GitHub Pages (frontend only)

- The frontend for this project is deployed to GitHub Pages at:

   https://ram0770.github.io/Smart_Task_Analyzer/

   NOTE: The Pages site may take a few minutes to become available after the first deploy.

- GitHub Pages can only serve static files — this means the Django backend is NOT hosted on Pages. If you want to host the backend, consider a service such as Render, Heroku, Azure App Service, or DigitalOcean App Platform.

- To update the Pages deployment automatically, push changes to `main`. The repository contains a GitHub Actions workflow that copies the `frontend/` folder and publishes it to Pages on every push to `main`.
