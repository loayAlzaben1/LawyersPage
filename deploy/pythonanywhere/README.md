PythonAnywhere deployment guide — quick steps

This guide assumes you already have a PythonAnywhere account and a web app created.
It explains how to update the site from your GitHub repository and restart the web app.

1) On PythonAnywhere – open a Bash console (or use the web "Consoles" tab).

2) Pull latest code (replace <your-repo> if you used a fork or different origin):

   git fetch origin
   git checkout feature/add-static-root
   git pull origin feature/add-static-root

3) Create / update virtualenv (if needed):

   # example: use Python 3.11
   python3.11 -m venv ~/venvs/lawyerspage
   source ~/venvs/lawyerspage/bin/activate
   pip install --upgrade pip
   pip install -r ~/yourproject/requirements.txt

   # if you already have a venv, just activate and pip install -r requirements.txt

4) Environment variables

   Set environment variables in the Web -> Configuration -> Environment variables section on PythonAnywhere.
   Important variables to set (examples):
     DJANGO_DEBUG=0
     DJANGO_ALLOWED_HOSTS=loayalzaben.pythonanywhere.com 127.0.0.1 localhost
     DJANGO_SECRET_KEY=YOUR_SECRET_KEY
     SITE_NAME="المحامية إيمان النجار"
     VAPID_PUBLIC_KEY=...
     VAPID_PRIVATE_KEY=...

5) Static files & media

   On PythonAnywhere, set the Static files mappings (Web tab):
     /static/ -> /home/yourusername/yourproject/staticfiles
     /media/  -> /home/yourusername/yourproject/media

   Then run:

   source ~/venvs/lawyerspage/bin/activate
   cd ~/yourproject
   python manage.py collectstatic --noinput

6) Migrations & DB

   source ~/venvs/lawyerspage/bin/activate
   cd ~/yourproject
   python manage.py migrate --noinput

7) Restart the web app

   On the PythonAnywhere Web tab click the "Reload" button for your web app, or from the console run:

   pa_reload_webapp YOUR_USERNAME.pythonanywhere.com

   (The console command pa_reload_webapp is available on PythonAnywhere accounts when you run via the Bash console.)

8) Logs

   If something goes wrong, check the error log on the Web tab (Error log) and also access the server console to see stack traces.

Notes and tips
- Ensure `STATIC_ROOT` and `MEDIA_ROOT` in settings.py point to the deployed paths. In this project they default to `staticfiles` and `media` under the repo root.
- If you serve media via PythonAnywhere, upload your `media/` folder or configure an external storage bucket (S3) for production.
- If you want me to create a GitHub Action that deploys automatically to PythonAnywhere, I can add a workflow, but it requires storing your PythonAnywhere API token as a GitHub secret.

If you want, I can create a simple `deploy.sh` you can run on the PythonAnywhere console to automate steps 2-6 (git pull, pip install, migrate, collectstatic). Let me know and I will add it.