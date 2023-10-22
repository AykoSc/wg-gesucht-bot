Based on [jonasdieker/wg-gesucht-bot](https://github.com/jonasdieker/wg-gesucht-bot)

# WG-Gesucht Bot 
*Let's face it, looking for a new WG is a pain, so why not just automate the process?*

## Changes from [jonasdieker/wg-gesucht-bot](https://github.com/jonasdieker/wg-gesucht-bot)
- The script attaches the "SCHUFA-BonitaetsCheck.pdf" to every single message, 
as most people want that (and the others don't mind). 
The file needs to be uploaded using this exact name.

- When there is a reCAPTCHA blocking the website, it gets shown in the log. 
Usually the reCAPTCHA disappears after a couple of minutes, so there's no need 
to do anything.

- I've also added a run.bat that enables the script to work on Windows.

- As the script (both the original and new one) crashes occasionally, 
it automatically restarts after 60s of crashing.

- The script now uses Firefox instead of Chrome, as Chrome as gave errors 
when I was trying to make it run on Ubuntu via console only.

- Added tutorial on how to make it work in the Oracle Cloud, to let the script run 24/7 without any cost.

- The script now also work on Windows, using its own .bat starting script.

- The paths to geckodriver and firefox can now be specified in the config.

- If there are any errors (which occur occasionally), the script now restarts automatically.

## Getting Started

### Linux (not tested)

#### 1 Create virtual environment and install Python packages

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
playwright install
```

#### 2 Ensure `firefox` is installed
Running `which firefox` should return a path like `/usr/bin/firefox`.

If not simply run `apt install firefox`. If that doesn't work, follow instructions for Ubuntu instance from below.

### Windows

#### 1 Create virtual environment and install Python packages
```bat
python -m venv env
venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

#### 2 Ensure `firefox` is installed
If you haven't yet installed `firefox`, simply download it at https://www.mozilla.org/de/firefox/windows/.

### Ubuntu instance on Oracle Cloud (free tier) with VM.Standard.A1.Flex (aarch64)

A great way to let the script run constantly without any cost, or it needing any attention.

#### 1 Create virtual environment and install Python packages
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
playwright install
playwright install-deps
```

#### 2 Install functional Firefox (as snap installed Firefox currently doesn't work with Selenium) and geckodriver
```bash
sudo snap remove firefox
sudo add-apt-repository ppa:mozillateam/ppa
echo '
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
' | sudo tee /etc/apt/preferences.d/mozilla-firefox
echo 'Unattended-Upgrade::Allowed-Origins:: "LP-PPA-mozillateam:${distro_codename}";' # Let Firefox upgrades install automatically
sudo apt install firefox

# Install geckodriver
apt install firefox-geckodriver
```

Perhaps some other commands will be necessary, look at the output after potential error messages. For example, 
`lxml` required me to `apt install libxml2` and `apt install libxslt`. 
`playwright` also needed some extra installation that will show in the error message.

### 3 Setup config file
Rename `config_template.yaml` to `config.yaml`, enter your email and password for wg-gesucht.de and your token for OpenAI (optional).

```yaml
messages:
  message_de: "message_de.txt"
  message_en: "message_en.txt"
wg_gesucht_credentials:
  email: "my-email@email.com"
  password: "password1234"
url: ""
openai_credentials:
  api_key: ""
run_headless: false
min_listing_length_months: 6
```

If you wish to send messages in e.g. english ONLY, simply delete `german: "message_de.txt` from the `messages` list in `config.yaml` file.

If no OpenAI token is provided, the bot will simply pick the first element from the `messages` list.

You also need to enter the `url`. Just go to `wg-gesucht.de`, enter all your filter requirements, apply filter and simply copy the url you get.


### 4 Write message into `message_de.txt`

Make sure you use the format of `Hello recipient`. Since the code automatically replaces `recipient` with the name of the user.

### 5 Finally, simply run the .sh (Linux) or .bat (Windows).


## Note on GPT use:

Option to use OpenAI GPT model to create more personalised messages!

So far, only language classification and keyword detection are supported.

You can easily add more functionality. Simply process the listing text (`config['listing_text']`) with GPT by writing a function which uses the `OpenAIHelper` class. Look at the `gpt_get_language` function inside the `src/submit_wg.py` file to get an idea.


## Acknowledgements

Thanks to the code by [nickirk](https://github.com/nickirk/immo), which served as a starting point for this project.

Note: Most of the code has been completely rewritten for simplicity and speed improvements.
