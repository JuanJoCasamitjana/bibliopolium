# Bibliopolium

Bibliopolium es una aplicación de recomendación de libros que utiliza técnicas de scraping, búsqueda y sistemas de recomendación. La plataforma ofrece a los usuarios sugerencias personalizadas, acceso rápido a información detallada sobre libros y una interfaz de usuario intuitiva desarrollada con Django.

## Características Principales

- **Scraping con Beautifulsoup:** La aplicación realiza scraping de diversas fuentes para obtener información detallada sobre libros, incluyendo reseñas y sinopsis.

- **Búsqueda Eficiente con Whoosh:** Se utiliza Whoosh para proporcionar a los usuarios una búsqueda rápida y precisa de libros basada en diferentes criterios.

- **Sistema de Recomendación Personalizado:** Bibliopolium implementa un sistema de recomendación basado en contenido para sugerir libros relacionados según las preferencias del usuario.

- **Interfaz Web Atractiva con Django:** La interfaz de usuario es desarrollada con Django, utilizando modelos, plantillas y formularios para una experiencia de usuario fluida.

## Instalación

1. Clona el repositorio:

    ```bash
    git clone https://github.com/tuusuario/bibliopolium.git
    cd bibliopolium
    ```

2. Crea y activa un entorno virtual:

    ```bash
    python -m venv venv
    source venv/bin/activate  # en sistemas basados en Unix
    ```

3. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4. Ejecuta las migraciones de la base de datos:

    ```bash
    python manage.py migrate
    ```

5. Inicia la aplicación:

    ```bash
    python manage.py runserver
    ```

Visita `http://localhost:8000/` en tu navegador para acceder a Bibliopolium.

## Manual de Uso

Asegúrate de consultar el manual de uso (`docs/manual.pdf`) para obtener instrucciones detalladas sobre cómo utilizar Bibliopolium.

---

¡Gracias por explorar y recomendar libros con Bibliopolium! Si tienes alguna pregunta o problema, no dudes en comunicarte con nosotros.
