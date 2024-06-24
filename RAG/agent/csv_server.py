from RAG.agent.sqlmapper import SqlMapper

from fastapi import FastAPI, Response
from starlette.responses import FileResponse

app = FastAPI()


@app.get("/table/test", response_class=Response)
async def read_table():
    with SqlMapper() as mapper:
        res = mapper.query("SELECT * FROM ai_use.dw_s_employment limit 50")
        csv = res.to_csv(encoding="utf-16")
    return Response(content=csv, media_type='text/csv; charset=utf-16')


@app.get("/table/test2", response_class=FileResponse)
async def read_table2():
    with SqlMapper() as mapper:
        res = mapper.query("SELECT * FROM ai_use.dw_s_employment limit 50")
        res.to_csv("test.csv", encoding="utf-16")
    return FileResponse("test.csv", media_type="text/csv", filename="test.csv")


@app.get("/table/test3", response_class=FileResponse)
async def read_table3():
    return FileResponse("test.csv", media_type="text/csv", filename="test.csv")
