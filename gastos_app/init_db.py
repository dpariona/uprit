import sqlite3

conn = sqlite3.connect("gastos.db")
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        monto REAL NOT NULL
    )
    """
)
conn.commit()
conn.close()
print("Base de datos creada: gastos.db")