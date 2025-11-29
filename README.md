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

## Deploying the backend (Django)

This project includes a template GitHub Actions workflow for deploying the Django backend to Render.com. The workflow will:

- Install dependencies
- Run collectstatic
- Trigger a Render deploy using the Render API (this requires `RENDER_API_KEY` and `RENDER_SERVICE_ID` to be set as repository secrets)

To deploy on Render:

1. Create a Web Service on Render with the GitHub repository connected (or create the service manually and note the `SERVICE ID`)
2. Add repo secrets in GitHub -> Settings -> Secrets & Variables:
   - `RENDER_API_KEY` — an API key from Render (read/write) that can trigger deploys
   - `RENDER_SERVICE_ID` — the ID of your Render service for the backend
3. Push to main. The GitHub Actions workflow `deploy-backend-render.yml` will run and attempt to trigger a deploy.

Note: If you prefer Azure App Service, Heroku or another cloud provider instead of Render, I can change the workflow to target that provider.

Environment variables (example):

- `DJANGO_SECRET_KEY` — a secure random secret
- `DJANGO_DEBUG` = `False` (set to False in production)
- `DJANGO_ALLOWED_HOSTS` = `your-app.onrender.com` (comma separated for multiple hosts)
- `DATABASE_URL` = `postgres://user:pass@host:port/dbname` (if using PostgreSQL)

Static files / Frontend configuration:

- The frontend is served by GitHub Pages and by staging the `frontend/` files into the Pages artifact.
- If the backend is deployed elsewhere, update the frontend code (e.g., `frontend/index.html`) to point to the new backend API base URL for saving/analyzing tasks (ex: `https://your-api.onrender.com/api/tasks/analyze/`).

