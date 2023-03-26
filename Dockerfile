#FROM python:3.9
##FROM python:3-alpine
#ENV PYTHONUNBUFFERED=1
#WORKDIR /app
#COPY requirements.txt .
#
#RUN pip install -r requirements.txt
#
#COPY . .



FROM python:3.11

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY env.sample .env

COPY . .

RUN python manage.py makemigrations
RUN python manage.py makemigrations accounts
RUN python manage.py makemigrations authentication
RUN python manage.py migrate

# gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
