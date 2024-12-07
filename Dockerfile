# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos y la app
COPY requirements.txt ./
COPY . . 

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que correrá la aplicación
EXPOSE 8000

# Usa un punto de entrada para Flask
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
