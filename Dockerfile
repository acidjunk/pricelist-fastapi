FROM python:3.8-slim

COPY ./requirements /tmp/requirements
RUN pip install -r /tmp/requirements/deploy.txt
RUN pip install -e git+https://github.com/workfloworchestrator/pydantic-forms.git@3454c8444b31405cb589426c05cae1a5dde4e03a#egg=pydantic-forms

EXPOSE 8080

COPY ./server /server

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
