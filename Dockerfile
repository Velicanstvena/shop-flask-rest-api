FROM python:3.13-rc
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN flask db upgrade
CMD ["flask", "run", "--host", "0.0.0.0"]
LABEL authors="teazmaj"