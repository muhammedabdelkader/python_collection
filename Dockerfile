#FROM python:latest
#RUN apt-get update -y && apt-get install -y python3-pip python3-dev
#WORKDIR /app
# We copy just the requirements.txt first to leverage Docker cache
#COPY ./requirements.txt /app/requirements.txt
#RUN pip install -r requirements.txt
#COPY ./app/ /app
#EXPOSE 80
#CMD ["python3" , "index.py"]
