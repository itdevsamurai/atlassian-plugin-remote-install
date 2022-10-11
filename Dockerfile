FROM python:3.10-alpine

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "src/main.py" ]

CMD [ "--help" ]
