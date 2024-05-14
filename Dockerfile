FROM python:3.9

EXPOSE 5000

WORKDIR /CBR_HW

COPY ../CBR_HW

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
