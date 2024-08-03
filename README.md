<p align="center">
  <a href="https://github.com/TabarakoAkula/ChtoZadano">
    <img width="300px" height="300px" alt="AChtoZadano" src="https://github.com/user-attachments/assets/559b5c28-5df0-45ba-9c1c-dc9d0a49f516">
  </a>
<h1 align="center">
  AChtoZadano
</h1>
<div align="center">  
  
  [![master CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/master.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/master.yml)
  [![server CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/server.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/server.yml)
  [![bot CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/bot.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/bot.yml)  
  [![python - 3.10 | 3.11 | 3.12](https://img.shields.io/badge/python-3.10_|_3.11_|_3.12-4b4de3)](https://)
  [![Django - 5.0.6](https://img.shields.io/badge/Django-5.0-4b4de3)](https://)  
  [![Issues](https://img.shields.io/github/license/mashape/apistatus.svg)](https://)
</div>

## Launch
+ #### First launch
  + ```bash
    docker compose up --build -d
    ```
+ #### Base launch:
  + ```bash
    docker compose up -d
    ```

### Install initial data fixture:
+ #### Launch docker
+ #### Exec in terminal:
  + ```bash
    docker exec -it chtozadano-web-1 bash
    cd chtozadano && python3 manage.py createsuperuser
    ```
<h2>Документация по API назодится в файле <a href="https://github.com/TabarakoAkula/ChtoZadano/blob/814ed9a3d8940f272863eeaae8cc39a04b7fda7c/API.md">API.md</a></h2>
