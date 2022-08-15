import psycopg2;

conn = psycopg2.connect('dbname = example');
cursor = conn.cursor();

# cursor.execute('DROP TABLE IF EXISTS table2;')
# cursor.execute('''
#     CREATE TABLE table2 (
#         id INTEGER PRIMARY KEY,
#         completed BOOLEAN NOT NULL DEFAULT False
#     );
# ''');

SQL = 'INSERT INTO table2 (id, completed) VALUES (%(id)s, %(completed)s);';
data = {
    'id': 3,
    'completed': True
}

# cursor.execute('INSERT INTO table2 (id, completed) VALUES (%s, %s);', (1, True));
cursor.execute(SQL, data);

conn.commit();
cursor.close();
conn.close();
