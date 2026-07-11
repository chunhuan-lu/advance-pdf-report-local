# Advance Report Studio

A local-first Safety & Compliance report tool: fill in a web form → preview → export PDF
(Gas / Smoke Alarm). Legacy form-fillable PDFs can be imported and re-edited.
Photos, reports and the database all live on this machine under `local_store/`.

## Getting started (end user)

**Double-click `start.bat`.** It will automatically:

1. Find Python 3.10+ (if missing, install 3.12 via winget or the python.org installer)
2. Create a virtual environment and install dependencies (first run needs internet;
   falls back to the Tsinghua PyPI mirror if the default index fails)
3. Initialize the database, start the server and open `http://127.0.0.1:8000`

**Phone access:** join the same Wi-Fi as the PC, then open the
`http://<PC-IP>:8000` address shown in the launcher window.

## Features

- **New reports**: Gas (cover + certificate + service tables + photo pages),
  Smoke Alarm (cover + compliance certificate; unlimited alarms, grouped 3 per row
  with automatic pagination) and Electrical (cover + safety certificate + safety
  services + fittings/notes + photo report; unlimited photo items)
- **Photo upload**: one photo per slot; re-uploading replaces it
  (stored under a fixed `reportId/slotId` filename)
- **Preview → Download**: preview streams PDF bytes without writing to disk;
  confirming generates the final PDF into `local_store/media/reports/`
- **Report history**: every report's JSON is stored in SQLite — reopen, edit and
  re-export at any time
- **Import PDF**:
  - PDFs exported by this tool embed the full JSON (`report_data.json` attachment)
    and restore losslessly
  - Legacy Word-template PDFs (AcroForm) are parsed from their form fields, with
    embedded photos extracted (Gas, Smoke and Electrical templates are supported)

## Project layout

```
config/          Django config (settings/urls/wsgi)
reports/         API: report CRUD, photo upload, generate, parse
pdfgen/
  common/        cover, header, checkbox, font styles, image/time helpers
  gas/           Gas report drawing (certificate/service/appliance_report)
  smoke/         Smoke report drawing (dynamic alarm groups)
  generate.py    dispatch by baseInfo.type
  embed.py       embed/extract JSON inside PDFs
  parse.py       AcroForm template parsing (field-name normalization + photo extraction)
  storage.py     local/S3 storage switch
  constants.py   option dictionaries (extracted from the official Word templates)
statics/         frontend (vendored Vue3, no build chain) + app.js/app.css
templates/       index.html (SPA shell)
local_store/     runtime data (git-ignored): db.sqlite3, media/photos, media/reports
```

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/reports/` | report list (summaries) |
| POST | `/api/reports/` | save draft `{id, data}` |
| GET/PUT/DELETE | `/api/reports/<id>/` | detail / update / delete |
| POST | `/api/photos/` | multipart `file` + `key`; same key overwrites; returns URL |
| POST | `/api/generate/` | `{id, data, mode: preview\|final}`; preview returns PDF bytes, final saves and returns `{url}` |
| POST | `/api/parse-pdf/` | multipart `file`; returns `{data, source: embedded\|acroform}` |

The Gas report JSON contract is compatible with the old easy_make_pdf `/generate-pdf/`
endpoint (`baseInfo` + `gasCheckDetails`). Smoke is a new structure
(`baseInfo` + `smokeCheckDetails`).

## Optional: switch storage to S3

Local by default. To host on a server with S3:

```
pip install boto3
set STORAGE_MODE=s3
set S3_BUCKET=advance-essentials
set S3_REGION=ap-southeast-2
```

and configure AWS credentials (environment variables or `aws configure`).

## Development

```
.venv\Scripts\python manage.py runserver
```

Note: keep requirements.txt / start.bat pure ASCII — on Chinese-locale Windows
(GBK codepage) pip and cmd choke on UTF-8 non-ASCII bytes.

## Known limits

- Import only supports PDFs produced by this tool (embedded JSON) and the official
  Word-template AcroForm PDFs; scanned or flattened PDFs cannot be parsed
- The local server has no authentication — use on this machine / trusted LAN only
