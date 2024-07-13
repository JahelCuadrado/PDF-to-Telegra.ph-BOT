## Iniciar bot con Docker


Construye el contenedor

```python
docker build --tag pdf-to-telegraph-bot:1.0.0 . 
```


Una vez construido modifica el archivo example.config.py a config.py, con tu token de telegram bot y tu token de telegra.ph, despues añade este archivo config.py como un volumen a la hora de lanzar el contenedor


```bash
docker run -d -v E:\Escritorio\Trabajo\Python\Bots\PDFtoTelegraphBot\config.py:/app/config.py c11   
```