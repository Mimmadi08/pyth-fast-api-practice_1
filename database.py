import oracledb

def get_connection():
    conn = oracledb.connect(
        user="apps",
        password="apps",
        dsn="omsddb.cswg.com:1521/omsd_app"
    )
    return conn