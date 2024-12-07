import csv
import logging
import os
from io import StringIO

import pandas as pd
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.responses import FileResponse
import joblib

from api import config, database, models
from api.models.pyd import PartyData

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

if not config.check():
    logging.error('bad initialization')
    exit(1)

app = FastAPI()
model = joblib.load('model.pkl')
tables_len_cash = {}


@app.get(path='/data_info', response_model=list[models.pyd.TableInfo])
def datainfo():
    info: list[models.TableInfo] = [
        models.pyd.TableInfo(
            table_name="case_ids",
            description="Contains basic information about cases, including the year they occurred.",
        ),
        models.pyd.TableInfo(
            table_name="collisions",
            description="Stores details about collisions, including jurisdiction, location, and other related data.",
        ),
        models.pyd.TableInfo(
            table_name="parties",
            description="Provides information about individuals involved in accidents, such as drivers, pedestrians, and cyclists.",
        ),
        models.pyd.TableInfo(
            table_name="victims",
            description="Stores data about victims, including their role, gender, age, and other relevant details.",
        ),
    ]
    return info


@app.get("/head")
def head(table_name: str, page: int = 0, page_size: int = 10, db: Session = Depends(database.get_db)):
    query = text(f"SELECT * FROM {table_name} LIMIT :page_size OFFSET :offset")
    results = db.execute(query, {"page_size": page_size, "offset": page * page_size}).fetchall()

    column_names = [col[1] for col in db.execute(text(f'PRAGMA table_info({table_name})'))]

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(column_names)
    writer.writerows(results)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={table_name}_head.csv"}
    )


@app.get('/data.csv')
def vehicle_distribution_data(db: Session = Depends(database.get_db)):
    data_folder = "./data"
    os.makedirs(data_folder, exist_ok=True)

    csv_file_path = os.path.join(data_folder, "parties.csv")
    files = [f for f in os.listdir(data_folder) if os.path.isfile(os.path.join(data_folder, f))]

    if "parties.csv" in files:
        return FileResponse(
            path=csv_file_path,
            media_type="text/csv",
            filename="vehicle_data.csv"
        )
    else:
        query = text(
            "SELECT case_id, vehicle_year, party_sex, party_age, cellphone_in_use, party_race FROM parties "
            "WHERE at_fault = 1"
        )
        result = db.execute(query)

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(result.keys())

        writer.writerows(result.fetchall())

        with open(csv_file_path, "w", newline='', encoding="utf-8") as file:
            file.write(output.getvalue())

        return FileResponse(
            path=csv_file_path,
            media_type="text/csv",
            filename="vehicle_data.csv"
        )


@app.get("/traumas.csv")
def get_traumas(db: Session = Depends(database.get_db)):
    data_folder = "./data"
    os.makedirs(data_folder, exist_ok=True)
    file_path = os.path.join(data_folder, "traumas.csv")
    files = [f for f in os.listdir(data_folder) if os.path.isfile(os.path.join(data_folder, f))]
    if "traumas.csv" in files:
        return FileResponse(
            path=file_path,
            media_type="text/csv",
            filename="vehicle_data.csv"
        )
    else:
        sql_request = '''
            SELECT CASE
                       WHEN party_age >= 18 AND party_age <= 30 THEN 'youngs'
                       WHEN party_age > 30 THEN 'adults'
                       ELSE 'unknown'
                       END                   AS age_group,
                   COUNT(*)                  AS total_people,
                   SUM(party_number_killed)  AS total_killed,
                   SUM(party_number_injured) AS total_injured
            FROM parties
            WHERE party_age >= 18 and at_fault == 1
            GROUP BY age_group;
            '''
        result = db.execute(text(sql_request))
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(result.keys())

        writer.writerows(result.fetchall())

        with open(file_path, "w", newline='', encoding="utf-8") as file:
            file.write(output.getvalue())

        return FileResponse(
            path=file_path,
            media_type="text/csv",
            filename="vehicle_data.csv"
        )


@app.get('/theory')
def theory():
    theory = '''I believe young people are more dangerous on the road; they are responsible for more collisions and are more likely to cause injuries or fatalities. To test this theory, I plan to analyze cases where individuals were at fault for collisions. That is why I will only look and analyze cases of people that were at fault, because if the person is not guilty of the collision, then there is no correlation with his age/sex/race etc.'''
    return theory


@app.get('/preview_message')
def preview_message():
    preview_message = '''Lets analyze `parties` table.  
This table has a lot of numeric fields. The most essential fields are `vehicle_year`,`party_type`, `at_fault`, `party_sex`, `party_age`, `party_sobriety` (can be a numeric field), `party_number_killed` (injured), `party_race`.  
`vehicle_year` says what year the vehicle is.  
`party_age` says the age of a victim.  
`party_sex` and `party_race` says about the person in general.  '''
    return preview_message


@app.post("/predict")
async def predict(data: PartyData):
    input_data = pd.DataFrame([[data.age, data.sex, data.race]],
                              columns=["party_age", "party_sex", "party_race"])
    input_data_encoded = input_data.copy()
    try:
        prediction = model.predict(input_data_encoded)
    except:
        return {"message": "well... i can't accept this data. sry"}, 400

    return {"at_fault": int(prediction[0])}
