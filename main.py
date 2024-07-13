#importaciones
import json
import telebot
from config import TELEGRAM_TOKEN
import os

import constanst
from pdf import borrar_pagina, pdf_to_telegraph


#instanciamos nuestro bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)
procesando_comando = False


os.makedirs(constanst.DOWNLOAD_FOLDER, exist_ok=True)
path_pdf = []


@bot.message_handler(commands=['start'])
def inicio_bot(message):
	bot.reply_to(message, "Hola!!, 🤖 Convierte tus PDF en enlaces de telegra.ph al instante. ¡Comparte fácilmente tus documentos! 📄✨, para poder empezar, manda un documento en formato PDF")
 

@bot.message_handler(commands=['help'])
def ayuda_bot(message):
	bot.reply_to(message, "Para poder convertir un PDF en un enlace Telegra.ph debes mandarme el archivo que quieras en formato PDF, si te has arrepentido y lo deseas borrar, mandame el enlace de vuelta y lo borraré")


@bot.message_handler(content_types=['document'])
def entrada_documento_pdf(message):
    global procesando_comando
    
    if not procesando_comando:
    
        document = message.document
        
        if document.mime_type == 'application/pdf':
            
            procesando_comando = True
            
            # Iniciar "escribiendo..."
            bot.send_chat_action(message.chat.id, 'typing')
            
            # Descargando el archivo
            file_info = bot.get_file(document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Ruta para guardar el archivo PDF
            file_path = os.path.join(constanst.DOWNLOAD_FOLDER, document.file_name)
            
            # Guardando el archivo PDF
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)
                
            path_pdf.append(file_path)
            
            bot.reply_to(message, "Manda el comando /confirmar si estás segurx de que quieres convertir este PDF en un pagina de Telegra.ph")
            
            procesando_comando = False

 
@bot.message_handler(func=lambda message: message.entities is not None and any(entity.type == 'url' for entity in message.entities))
def entrada_peticion_eliminacion(message):
    urls = [entity for entity in message.entities if entity.type == 'url']

    for url_entity in urls:
        url = message.text[url_entity.offset : url_entity.offset + url_entity.length]
        
        if not url.startswith(constanst.START_WITH_TELEGRAPH) :
            bot.reply_to(message, f"Lo siento, eso no es un enlace de Telegra.ph")
        
        else:
            if comprobar_usuario(str(message.chat.id), str(message.text)):
                bot.reply_to(message, f"Borrando..., espera por favor.")
                borrar_pagina(url)
                with open(constanst.PATH_PROPIETARIOS_JSON, "r") as archivo:
                    datos = json.load(archivo)
                    
                datos[str(message.chat.id)].remove(url)
                
                with open(constanst.PATH_PROPIETARIOS_JSON, "w") as archivo: 
                    json.dump(datos, archivo, indent=4)
                            
            else:
                bot.reply_to(message, f"Lo siento, las paginas de Telegra.ph solo pueder ser borradas por su propietario")
        
        
@bot.message_handler(commands=['confirmar'])
def confirmar_conversion(message):
    global procesando_comando
    
    if not procesando_comando:
    
        if path_pdf and not procesando_comando:
            procesando_comando = True
            
            # Iniciar "escribiendo..."
            bot.send_chat_action(message.chat.id, 'typing')
                    
            urlTelegraph = pdf_to_telegraph(path_pdf[0]) 
            
            id_usuario = str(message.chat.id)
            
            guardar_propietario_url(id_usuario, urlTelegraph)
            
            os.remove(path_pdf[0])
            
            path_pdf.pop()
                    
            bot.reply_to(message, urlTelegraph)
            
            procesando_comando = False
                
        else: 
            
            bot.reply_to(message, "Para poder confirmar la conversión, antes debes mandar un archivo en formato PDF")


def guardar_propietario_url(id_usuario, url_pagina):
    
    if not os.path.exists(constanst.PATH_PROPIETARIOS_JSON,):
        with open(constanst.PATH_PROPIETARIOS_JSON, "w") as archivo: 
            datos = {
                id_usuario : [url_pagina]
            } 
            json.dump(datos, archivo, indent=4)
    
    else:
        with open(constanst.PATH_PROPIETARIOS_JSON, "r") as archivo: 
            try:
                datos_leidos = json.load(archivo)
            except: 
                datos_leidos = {}
                   
        if id_usuario not in datos_leidos:
            with open(constanst.PATH_PROPIETARIOS_JSON, "w") as archivo: 
                datos_leidos[id_usuario] = [url_pagina]
                json.dump(datos_leidos, archivo, indent=4)
                    
        else:  
            with open(constanst.PATH_PROPIETARIOS_JSON, "w") as archivo:   
                datos_leidos[id_usuario].append(url_pagina)
                json.dump(datos_leidos, archivo, indent=4)
 

def comprobar_usuario(id_usuario, url_pagina): 
    
    if not os.path.exists(constanst.PATH_PROPIETARIOS_JSON,):
        return False
    
    with open(constanst.PATH_PROPIETARIOS_JSON, "r") as archivo: 
        try:
            datos_leidos = json.load(archivo)
        except: 
            return False
    
    if id_usuario not in datos_leidos:
        return False
    
    if url_pagina not in datos_leidos[id_usuario]:
        return False
    
    return True      
 
 
bot.polling()