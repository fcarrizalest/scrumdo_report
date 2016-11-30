FROM python:2.7-onbuild
RUN mkdir /app
WORKDIR /app


ENV DATABASE_URL  postgresql+psycopg2://postgres:mysecretpassword@db3:5432/postgres
ENV REDISTOGO_URL redis://redis:6379/

ENV SCRUMDO_USERNAME user
ENV SCRUMDO_PASSWORD pass

CMD [ "python", "./worker.py" ]
