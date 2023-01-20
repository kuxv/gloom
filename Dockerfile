FROM python:3.11.1-slim-bullseye
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 80
CMD [ "python", "-m", "flask", "--app", "server", "run", "--host", "0.0.0.0:80"]