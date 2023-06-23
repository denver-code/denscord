# Denscord API
Denscord is a Discord clone built as a pet project to test my skills and create a portfolio project. It allows users to create guilds, channels, and send messages in those channels. This README provides instructions on how to install and set up the Denscord API server.  

[Denscord Client](https://github.com/denver-code/denscord_fe)

## Actual Demo  
> [Note] Click on image.  

<a href="http://www.youtube.com/watch?feature=player_embedded&v=yRj2ogMNhtw
" target="_blank"><img src="http://img.youtube.com/vi/yRj2ogMNhtw/0.jpg" 
alt="yRj2ogMNhtw" width="240" height="180" border="10" /></a>

# ▹ Installation #
> [!NOTE]
> For start make sure you have python and docker installed on your machine.
``` Bash
git clone https://github.com/denver-code/denscord
cd denscord[Uploading requests.json…]()

```
Rename ```sample.env -> .env``` and don't forget to change the settings inside.  
Also you may import the Insomnia requests collection, that's file requests.json
# ▹ Run using docker #
> [!NOTE]
> For start make sure you have docker installed on your machine.
```bash
sh scripts/run.sh
```
or
``` bash
docker-compose up --build -d
```
# ▹ Run #
> [!NOTE] Make sure you have installed poetry on your machine (pip3 install poetry)
``` Bash
poetry install
poetry run uvicorn denscord.main:app
```

# Edit project in VS Code
``` bash
poetry install
poetry shell
code .
```

# Test
``` bash
pytest -r pF --disable-warnings
```
