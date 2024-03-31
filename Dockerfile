FROM python:3.11.8

# Create non-root group and user
RUN addgroup --system dash_app \
  && adduser --system --home /var/cache/dash_app --ingroup dash_app --uid 1001 dashuser

USER dashuser

WORKDIR /dash_app/

COPY --chown=dashuser requirements.txt /dash_app/

# Elegantly activating a venv in Dockerfile: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV VIRTUAL_ENV=/dash_app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install requirements
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY --chown=dashuser /klimainsights/ /dash_app/klimainsights/

WORKDIR /dash_app/klimainsights/

# set enviroment variables
# This prevent Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED=1

ENV ENV_FILE=".env"

EXPOSE 7000

ENTRYPOINT ["gunicorn", "index:server", "-b", "0.0.0.0:7860", "--workers=1"]