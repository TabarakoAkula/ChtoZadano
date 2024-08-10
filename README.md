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

## Make scripts
+ ``update``
  + git pull + restart docker a daemon
+ ``docker-rebuildup``
  + docker stop + build + up as daemon
+ ``docker-bash-web``
  + open bash in ``web`` container
+ ``docker-psql``
  + open psql in ``db`` container as user ``posgresql`` 
+ ``docker-clean-all``
  + prune **all** containers
+ ``docker-clean-old``
  + prune ``non-active`` containers
+ ``sort-req``
  + sort all requirements in ``requirements/`` :)
 
## Create superuser  
+ Open ``bash`` in ``web`` contsiner
+ ```bash
  cd chtozadano && python3 manage.py createsuperuser
  ```

<h2>Документация по API находится в файле <a href="https://github.com/TabarakoAkula/ChtoZadano/blob/814ed9a3d8940f272863eeaae8cc39a04b7fda7c/API.md">API.md</a></h2>
