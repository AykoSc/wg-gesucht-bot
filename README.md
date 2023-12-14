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
- Uses Firefox instead of Chrome, as Chrome as gave errors trying to make 
it run on Ubuntu via console only.
- Added tutorial on how to make it work in the Oracle Cloud, 
to let the script run 24/7 without any cost.
- The paths to geckodriver and firefox can now be specified in the config.

## Getting Started

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

### Linux

An Ubuntu instance on Oracle Cloud (free tier) with VM.Standard.A1.Flex (aarch64)
is a great way to let the script run constantly without any cost, or it needing any attention.

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
apt install firefox-geckodriver # Install geckodriver
```

Perhaps some other commands will be necessary, look at the output after potential error messages. For example, 
`lxml` required me to `apt install libxml2` and `apt install libxslt`. 
`playwright` also needed some extra installation that will show in the error message.

### 3 Setup config file
Rename `config_template.yaml` to `config.yaml`, enter your email and password.

```yaml
message_file: "message.txt"
wg_gesucht_credentials:
  email: "my-email@email.com"
  password: "password1234"
url: ""
run_headless: true
min_listing_length_months: 6
attach_schufa: false
custom_condition: "user_name not in 'John Doe'"

# Optional (should work without these in most cases)
geckodriver_path: ""
firefox_path: ""
```

You need to enter the `url`. Just go to `wg-gesucht.de`, enter all your filter requirements, apply filter and simply copy the url you get.

### 4 Write message into `message.txt`

Make sure you use the format of `Hello recipient`. Since the code automatically replaces `recipient` with the first name of the user.

### 5 Finally, simply run the .sh (Linux) or .bat (Windows).

## Acknowledgements

Thanks to the code by [nickirk](https://github.com/nickirk/immo), which served as a starting point for this project.

Note: Most of the code has been completely rewritten for simplicity and speed improvements.
