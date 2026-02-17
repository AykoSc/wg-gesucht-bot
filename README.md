# WG-Gesucht Bot 
*Let's face it, looking for a new WG is a pain, so why not just automate the process?*

## Key Features
- **Dockerized Setup**: Simplified 2026-style Docker setup handles all dependencies (Firefox and Playwright) automatically. No manual browser installation required.
- **Individualized Messages**: Option to use GPT to send more individualized messages based on listing descriptions.
- **Rental Filter**: Filter listings based on rental start date and duration.
- **Custom Conditions**: Option to create custom Python-expression based conditions for listings (e.g. skip specific users).
- **Attachments**: Option to attach "SCHUFA-BonitaetsCheck.pdf" to every message.
- **Resilience**: Restarts automatically if there are any exceptions and logs reCAPTCHA detections.

## Setup

### 1. Setup config file
Rename `config_template.yaml` to `config.yaml`.
- Enter your `wg_gesucht_credentials` (email and password).
- Customize the `message` field.
- Enter the `url` from `wg-gesucht.de` with all your filter requirements applied.
- (Optional) Enter your `openai_key` if you want to use GPT.
- (Optional) Set `rental_start` parameters and `min_listing_length_months`.

### 2. Attachments (Optional)
If you want to attach a Schufa check, ensure a file named `SCHUFA-BonitaetsCheck.pdf` is in the root directory and set `attach_schufa: true` in `config.yaml`.

### 3. Start the bot with Docker
Ensure you have Docker and Docker Compose installed, then simply run:

```bash
docker compose up -d
```

To view logs:
```bash
docker compose logs -f
```

## Acknowledgements
Thanks to the code by [nickirk](https://github.com/nickirk/immo), which served as a starting point for this project.

Note: This fork has been completely rewritten for Playwright and Docker for better stability and ease of use.
