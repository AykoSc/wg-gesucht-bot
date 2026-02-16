# WG-Gesucht Bot 
*Let's face it, looking for a new WG is a pain, so why not just automate the process?*

## Changes from [jonasdieker/wg-gesucht-bot](https://github.com/jonasdieker/wg-gesucht-bot)
- Option to attach  "SCHUFA-BonitaetsCheck.pdf" to every single message). 
The file needs to be uploaded using this exact name.
- When there is a reCAPTCHA blocking the website, it gets shown in the log. 
Usually the reCAPTCHAs disappear by themselves after a couple of minutes.
- run-windows.bat and run-linux.sh to run the script on Windows and Linux.
- Restarts automatically if there are any exceptions.
- Option to create custom conditions for listings. 
For example, to only send messages to listings that don't have a 
certain name in the title.
- Simplified 2026-style Docker setup handles all dependencies (Firefox and Playwright) automatically.
- Uses Python 3.14-slim for a modern, efficient environment.
- No manual browser installation or complex Linux PPA setup required.

### 1 Setup config file
Rename `config_template.yaml` to `config.yaml`, enter your email and password, and customize the `message` field.

You also need to enter the `url`. Just go to `wg-gesucht.de`, enter all your filter requirements, apply filter and simply copy the url you get. An example `url` is provided.

### 2 Start the bot with Docker

Ensure you have Docker and Docker Compose installed, then simply run:

```bash
docker compose up -d
```

## Acknowledgements

Thanks to the code by [nickirk](https://github.com/nickirk/immo), which served as a starting point for this project.

Note: Most of the code has been completely rewritten for simplicity and speed improvements.
