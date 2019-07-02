FROM python:3
COPY . /app
WORKDIR /app
RUN pip install -r ./requirements.txt
CMD [ "flask", "run", "-h", "0.0.0.0"  ]
