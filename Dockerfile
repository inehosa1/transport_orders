# syntax=docker/dockerfile:1
FROM python:3.10.4-alpine3.15
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN  apk update \
	&& apk add --no-cache gcc musl-dev postgresql-dev python3-dev libffi-dev \
	&& pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
