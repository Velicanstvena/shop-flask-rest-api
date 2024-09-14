FROM python:3.13-rc
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
RUN flask db upgrade
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]
LABEL authors="teazmaj"