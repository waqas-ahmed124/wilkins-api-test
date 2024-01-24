# Base image
FROM public.ecr.aws/docker/library/python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /apps
ENV VENV /opt/venv
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH /app

ENV VENV /opt/venv
# Virtual environment
RUN python3 -m venv ${VENV}
ENV PATH="${VENV}/bin:$PATH"

WORKDIR /app

COPY ./src ./
# Copy Poetry file
COPY ./pyproject.toml ./
COPY ./poetry.lock ./

# Install Poetry with pinned version to avoid breaking changes
RUN pip install poetry==1.5.1
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 3001

CMD ["poetry", "run", "uvicorn", "apiserver.main:app", "--host", "0.0.0.0", "--port", "3001"]
