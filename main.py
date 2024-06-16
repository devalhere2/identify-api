from fastapi import FastAPI
import uvicorn
import psycopg2
from psycopg2.extras import DictCursor
import json
from typing import Optional,List,Union
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


class ContactModel(BaseModel):
    primaryContactId: int
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]

class ResponseModel(BaseModel):
    contact: ContactModel

class UserData(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


with open('./sample.json', 'r') as file:
    data = json.load(file)

# docker run --name demoapi -e POSTGRES_PASSWORD=1234 -p 5432:5432 -d postgres:alpine
# Database connection details
DB_HOST = "0.0.0.0"  
DB_USER = "postgres"
DB_PASSWORD = "1234"  

conn = psycopg2.connect(user=DB_USER,password=DB_PASSWORD,host=DB_HOST)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS entries")
cur.execute("""
CREATE TABLE entries (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    phone VARCHAR(20),
    linkedPrecedence VARCHAR(20),
    personId INT
);
""")


def Match(email,phone):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        query = "SELECT * FROM entries WHERE email = %s OR phone = %s"
        params = (email, phone)
        cur.execute(query, params)
        results = cur.fetchall()
        return [dict(result) for result in results]

def insertPrimary(email,phone):
    cur.execute("""
            INSERT INTO entries (email, phone, linkedPrecedence) 
            VALUES (%s, %s, 'primary') RETURNING id;
        """, (email, phone))
    id_of_new_row = cur.fetchone()[0]
    conn.commit()

    # Update the personID with the value of the generated id
    cur.execute("""
            UPDATE entries SET personID = %s WHERE id = %s;
        """, (id_of_new_row, id_of_new_row))
    conn.commit()
    return "Data inserted successfully"

def insertSecondary(email,phone,personId):
    cur.execute("INSERT INTO entries (email, phone, linkedPrecedence, personID) VALUES (%s, %s, 'secondary', %s)", (email, phone,personId))
    conn.commit()
    return "Data inserted successfully"

def getPersonId(id):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        query_sql = "SELECT * FROM entries WHERE personId = %s;"
        cur.execute(query_sql, (str(id)))
        results = cur.fetchall()
        return [dict(result) for result in results]
    

def Extract(email,phone):
    result = Match(email,phone)
    primar_id = None
    secondary_id = []
    emails = []
    phoneNumbers = []

    for i in range(len(result)):
        if result[i]['linkedprecedence'] == 'primary':
            res = getPersonId(result[i]['personid'])
            for i in res:
                if i['linkedprecedence'] == 'primary':
                    primar_id = i['personid']
                    if i['email'] not in emails:
                        emails.append(i['email'])
                    if i['phone'] not in phoneNumbers:
                        phoneNumbers.append(i['phone'])
                else:
                    if i['id'] not in secondary_id:
                        secondary_id.append(i['id'])
                    if i['email'] not in emails:
                        emails.append(i['email'])
                    if i['phone'] not in phoneNumbers:
                        phoneNumbers.append(i['phone'])

    return [primar_id,emails,phoneNumbers,secondary_id]

def changePrimarytoSecondary(email, phone):
    result = Match(email,phone)
    for i in range(1,len(result)):
        cur.execute("""
            UPDATE entries 
            SET personID = %s, linkedPrecedence = 'secondary' 
            WHERE email = %s OR phone = %s
            """, (result[0]['personid'], result[i]['email'], result[i]['phone']))
        conn.commit()
    pass



def changeToPrimary():
    update_sql = """
    UPDATE entries
    SET linkedPrecedence = 'primary'
    WHERE personId = id;
    """
    cur.execute(update_sql)
    conn.commit()

@app.get("/")
def read_root():
    return {"Welcome to the Identify API"}

@app.post("/identify",response_model=Union[ResponseModel,None,List])
def insert_user_data(user_data: UserData):
    email = user_data.email
    phone = user_data.phone
    if (email == None and phone == None):
        return "Enter some Value to Identify"
    result = Match(email,phone)
    if len(result) == 0:
        insertPrimary(email,phone)
        resultafter = Extract(email,phone)
     
        
        
    if len(result) == 1:
        if (result[0]['email'] == email and result[0]['phone'] == phone):
            resultafter = Extract(email,phone)
            
        
        elif (result[0]['email'] == email or result[0]['phone'] == phone):
            insertSecondary(email,phone,result[0]['personid'])
            resultafter = Extract(email,phone)

    if len(result) > 1:
        insertSecondary(email,phone,result[0]['personid'])
        changePrimarytoSecondary(email,phone)
        changeToPrimary()
        resultafter = Extract(email,phone)
        
    return {
            "contact": {
                "primaryContactId": resultafter[0],
                "emails": resultafter[1],
                "phoneNumbers": resultafter[2],
                "secondaryContactIds": resultafter[3]
            }
        }

        
        
@app.delete("/delete-all")
def delete_all_entries():
    try:
        cur.execute("DELETE FROM entries;")
        conn.commit()
        return {"message": "All entries deleted successfully."}
    except:
        pass

@app.get("/read-all")
def read_root():
    cur.execute("SELECT * FROM entries")
    return cur.fetchall()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
