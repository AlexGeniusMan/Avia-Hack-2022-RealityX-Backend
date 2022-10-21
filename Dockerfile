FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /usr/src/project

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD sh -c "python3 manage.py collectstatic --noinput && python3 manage.py migrate && python3 manage.py createsuperuser --noinput ; gunicorn --bind 0.0.0.0:8080 --workers=9 --log-level debug --timeout 360 project.wsgi"
