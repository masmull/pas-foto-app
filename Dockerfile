# Gunakan base image Python 3.10 slim
FROM python:3.10-slim

# Set working directory di container
WORKDIR /app

# Copy semua file project ke container
COPY . /app

# Install dependency
RUN pip install --upgrade pip
RUN pip install flask pillow rembg[cpu]

# Ekspos port 5000 untuk Flask
EXPOSE 5000

# Jalankan app.py
CMD ["python", "app.py"]
