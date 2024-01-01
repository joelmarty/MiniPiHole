FROM balenalib/raspberry-pi-alpine-python:3.12-build as build

WORKDIR /app

RUN python -m venv /app/venv
# Make sure we use the virtualenv:
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install -r requirements.txt

FROM balenalib/raspberry-pi-alpine-python:3.12-run AS run
WORKDIR /app

COPY --from=build /app/venv /app/venv
COPY ./minipadd ./
COPY ./main.py ./

# Make sure we use the virtualenv:
ENV PATH="/app/venv/bin:$PATH"
CMD ["/app/venv/bin/python", "/app/main.py"]