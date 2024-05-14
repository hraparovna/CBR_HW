FROM python:3.9

EXPOSE 5000

WORKDIR /CBR_HW

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
