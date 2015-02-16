FROM python:2.7
MAINTAINER James Piechota <james@yellowpay.co>
EXPOSE 8000

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app/
RUN pip install -r /usr/src/app/requirements.txt
 
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
