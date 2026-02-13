# Grayjay Export Converter

Converts YouTube data from [Grayjay](https://grayjay.app/) exports into Google Takeout format, so you can import it into other YouTube clients.

## Use Online

No install needed — use the web version at:\
**[joetul.github.io/GrayjayExportConverter](https://joetul.github.io/GrayjayExportConverter)**

Drop your Grayjay export ZIP and download the converted files. Everything runs locally in your browser.

You can also download `index.html` and open it directly on your computer.

## What Gets Converted

| Grayjay | Output |
|---------|--------|
| Watch history | `watch-history.json` |
| Subscriptions | `subscriptions.csv` (with channel names) |
| Playlists | Individual CSV files in `playlists/` |
| Watch Later | `playlists/Watch later.csv` |

Only YouTube data is converted. Other platforms (Spotify, etc.) are skipped.

## Tested With

- **LibreTube** — subscriptions, watch history, playlists
- **FreeTube** — subscriptions, watch history

## Note on LibreTube

LibreTube uses Piped by default. Since Piped can sometimes be unstable, you may want to disable the Piped proxy in the Instance settings within the app.
