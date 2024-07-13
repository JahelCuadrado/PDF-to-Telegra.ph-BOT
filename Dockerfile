# Utilizamos una imagen base de Python
FROM python:3.9.19-alpine3.20

# Establecemos el directorio de trabajo en /app
WORKDIR /app

# Copiamos el archivo de requisitos
COPY requirements.txt .

#instalamos dependencias que son necesarias y que no están disponibles en alpine por defecto
RUN apk update && apk add libstdc++

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente al contenedor
COPY . .

# Comando para ejecutar el bot
CMD ["python", "main.py"]
