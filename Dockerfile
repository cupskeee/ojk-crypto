# Gunakan image Python resmi sebagai base
FROM python:3.11-slim

# Set environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Salin requirements.txt (jika ada) ke dalam container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Salin source code aplikasi ke dalam container
COPY . /app/

# Expose port Flask (misal default 5000)
EXPOSE 5000

# Jalankan aplikasi Flask
# Jika file utama Anda misalnya app.py, gunakan baris berikut:
CMD ["flask", "run", "--host=0.0.0.0"]

# Jika Anda menggunakan entrypoint lain (misal gunicorn), bisa diganti seperti:
# CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]