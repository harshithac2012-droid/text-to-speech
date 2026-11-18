# Epoch Reader

A text-to-speech reader that cleans up tricky text (numbers, currencies,
acronyms, URLs, names) before speaking it, and logs where speech fails.
Built by team Epoch for the Gradium × TensorTonic Voice Challenge.

## Why
Speech models often misread numbers, acronyms, names and symbols.
Epoch Reader normalizes text first, shows exactly what it changed,
and records how each result sounded so failures can be reported.

## Features
- Paste text or upload a `.txt` file
- Rule-based text normalization (numbers, money, percentages, URLs,
  emails, acronyms) with a visible change log
- Custom pronunciation dictionary (`pronunciations.json`)
- Long text split into sentence-aligned chunks
- Voice and speed selection, audio download
- In-app rating and notes saved to a feedback log
- Mock audio mode, so the app runs without an API key

## Quick start
```bash
git clone <your-repo-url>
cd epoch-reader
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
streamlit run app.py
```

## Using the Gradium API
1. Create a Gradium account and generate an API key.
2. `pip install gradium`
3. Copy `.env.example` to `.env` and set `GRADIUM_API_KEY`.
4. Restart the app. The mock-mode warning disappears.

## Testing
```bash
pytest                    # unit tests for the normalizer
python run_test_set.py    # batch-run data/test_sentences.csv
```

## Project layout
See the folder structure at the top of this repo; the key modules are
`normalizer.py` (text rules), `tts_client.py` (speech backend) and
`logger.py` (feedback log).

## Findings
Our report on where Gradium's speech held up and where it broke is in
[`docs/FEEDBACK.md`](docs/FEEDBACK.md).

## Team
Epoch: <names>

## License
MIT