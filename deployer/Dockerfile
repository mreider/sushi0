FROM python:3.9-slim
WORKDIR /usr/src/app
COPY . .
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "deployer.py"]