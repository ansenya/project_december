# December Project
## Structure

```
├── api
│   ├── Dockerfile
│   ├── __init__.py
│   ├── config.py
│   ├── data
│   ├── database
│   ├── main.py
│   ├── model.pkl
│   ├── models
│   └── requirements.txt
├── data
│   ├── download_data.sh
│   └── switrs2.sqlite
├── deploy
│   └── docker-compose.yml
├── jupyter
│   ├── main.ipynb
│   ├── model.pkl
│   └── requirements.txt
├── readme.md
└── slt
    ├── Dockerfile
    ├── data
    ├── main.py
    └── requirements.txt
```

- api: FastAPI backend service
- slt: Streamlit application
- data: The database's place (should be downloaded using the script `download_data.sh`)
- deploy: docker-compose file to start the applications
- jupyter: jupyter notebook


---
database should be downloaded via the script `download_data.sh`. otherwise, the apps won't work properly.