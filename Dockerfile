FROM python:3.11

# Set the working directory
WORKDIR /app


COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . ./


EXPOSE 8000

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=favcription.settings
ENV PYTHONUNBUFFERED=1

# Collect static files
RUN python manage.py collectstatic --noinput

# Command to run the application
CMD ["python", "manage.py", "migrate"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "favcription.wsgi:application"]
# CMD ["python manage.py migrate && gunicorn --bind 0.0.0.0:8000 favcription.wsgi:application"]