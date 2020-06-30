# docker_apuntes

Para las imagenes si se decea modificar datos los datos del archivo que acompaña al docker file simplemente se puede modificar 

## Para subir una imagen a un respositorio en docker hub
### 1. Si no existe la imagen o repositorio en docker hub se debe hacer un tag
#### - Ojo esto crea un nombre  usuarioDockerHub/nombre_repo en las imagenes locales de docker
docker tag nombre_imagen usuarioDockerHub/nombre_repo

### 2. luego se pude subir la imagen que se encuentre en las imagenes de docker local con
docker push usuarioDockerHub/nombre repo


