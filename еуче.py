import psycopg2

try:
    # попытка подключиться к базе данных
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5433/dev_rstp_scmo')
except Exception as e:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print(e)
    print('Can`t establish connection to database')