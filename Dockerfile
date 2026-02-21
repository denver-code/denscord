FROM python:3.11-slim

# System dependencies for Pillow and building C extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry 2.0+
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=2.0.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Copy only the dependency files first
COPY pyproject.toml poetry.lock* ./

# Install dependencies only
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Ensure storage directories exist
RUN mkdir -p static/sessions static/cars

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]