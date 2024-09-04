FROM python:3.12

WORKDIR /bot

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot_main.py"]