FROM python:3.12.2-slim-bullseye
WORKDIR /app
EXPOSE 55582
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8001
CMD [ "python", "run.py" ]