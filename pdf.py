import fitz
from PIL import Image
from telegraph import Telegraph, TelegraphException
import tempfile
import asyncio
import os
from config import ACCESS_TOKEN

telegraph = Telegraph(access_token=ACCESS_TOKEN)


# Convertir el nombre a camel case
def to_camel_case(file_name):
    # Eliminar la extensión y reemplazar caracteres no permitidos
    name = os.path.splitext(file_name)[0]
    # Reemplazar guiones y espacios por espacios
    name = name.replace('-', ' ').replace('_', ' ')
    # Convertir a camel case
    parts = name.split()
    camel_case_name = parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
    return camel_case_name


def pdf_to_images(pdf_path):
    pdf_document = fitz.open(pdf_path)
    
    image_files = []
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        
                # Use a matrix to increase the resolution
        matrix = fitz.Matrix(5.0, 5.0)
        image_list = page.get_pixmap(matrix=matrix)
        
        img = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)
        
        # Guardar la imagen en un archivo temporal
        temp_image = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_image.name, "PNG")
        
        # Abrir el archivo de imagen en modo de lectura binaria y guardar el objeto de archivo en la lista
        image_file = open(temp_image.name, "rb")
        image_files.append(image_file)
    
    return image_files


def upload_images_to_telegraph(images_list):
    uploaded_urls = []
    for image in images_list:
        response = telegraph.upload_file(image)
        uploaded_urls.append(response[0]['src'])  # Asumiendo que la respuesta es una lista de diccionarios con la clave 'src'
    return uploaded_urls


async def main(path):

    pdf_path = path
    images = pdf_to_images(pdf_path)
    
    # Extraer el nombre del archivo PDF y convertirlo a camel case
    pdf_name = os.path.basename(pdf_path)
    camel_case_name = to_camel_case(pdf_name)

    # Llamada a la función para subir las imágenes del PDF
    uploaded_image_urls = upload_images_to_telegraph(images)
    
    # Crear el contenido HTML con las URL de las imágenes
    html_content = ""
    for url in uploaded_image_urls:
        html_content += f'<img src="https://telegra.ph/{url}"><br>'
    
    response = telegraph.create_page(
        camel_case_name,
        html_content=html_content,
    )
    return response['url']


def borrar_pagina(url):
    # Obtener el path de la URL
    path = url.split('telegra.ph/')[-1]
    print(path)

    try:
        # Editar la página para dejarla vacía
        response = telegraph.edit_page(
            path=path,
            title='(Eliminado)',
            author_name='Anónimo',
            content=['(Eliminado)']
        )
        print(f'Página editada: {response["url"]}')
    except TelegraphException as e:
        print(f'Error al editar la página: {str(e)}')
  
    
def pdf_to_telegraph(path):
    return asyncio.run(main(path))