# Python 3.10 bazo'viy obrazidan foydalanamiz
FROM python:3.10-slim

# Konteyner ichidagi ishchi papkani belgilaymiz
WORKDIR /app

# Avval kutubxonalar ro'yxatini ko'chirib o'tkazamiz va o'rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Qolgan barcha fayllarni (app.py, scheduler.py, va h.k.) ko'chiramiz
COPY . .

# Ilova ishlaydigan portni ochiq deb belgilaymiz (odatda Flask uchun 5000)
EXPOSE 5000

# Dasturni ishga tushirish buyrug'i
CMD ["python", "app.py"]
