FROM python:3.12-alpine AS base

# Install Poetry
RUN pip install poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
ENV PATH="$PATH:$POETRY_HOME/bin"

FROM base AS build
WORKDIR /app
COPY pyproject.toml .
RUN poetry lock --no-update && poetry install --only=main
COPY . .

# Runtime stage
FROM base AS runtime
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"
RUN echo "source /app/.venv/bin/activate" >>/etc/profile.d/venv.sh

# Install Hypercorn
RUN pip install hypercorn

# Expose port
EXPOSE 5000

# Run Hypercorn with app
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:5000", "--reload"]