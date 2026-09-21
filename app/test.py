##  database id 001
# from app.database import get_db
# def test_database_session():
#     db_generator = get_db()
#     db = next(db_generator)
#     assert db is not None
#     db_generator.close()

# from sqlalchemy import text
# from app.database import get_db
# def test_database_session():
#     db_generator = get_db()
#     db = next(db_generator)
#     result = db.execute(text("SELECT 1"))
#     value = result.scalar()
#     assert value == 1
#     db_generator.close()