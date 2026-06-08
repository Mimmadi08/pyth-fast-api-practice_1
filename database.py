import oracledb

def get_connection():
    """
    Creates and returns a connection to the
    Oracle OMS database.
    Always close connection after use.
    """
    conn = oracledb.connect(
        user="apps",
        password="apps",
        dsn="omsddb.cswg.com:1521/omsd_app"
    )
    return conn