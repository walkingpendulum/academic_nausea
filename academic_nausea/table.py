import contextlib
import sqlite3  # предпочитаю SQLAlchemy с его ORM, но к использованию рекомендовался sqlite3


@contextlib.contextmanager
def autocommit_and_autoclose(conn):
    cursor = conn.cursor()

    try:
        yield cursor
    except:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        cursor.close()


class DatabaseHandler(object):
    columns = ('document_name', 'rate', 'fraud_words')

    def __init__(self, db_name=None, table_name=None):
        self.conn = sqlite3.connect(database=db_name or 'test')
        self.table_name = table_name or 'results'

    def create_table_if_not_exist(self):
        create_table_statement = (
            'CREATE TABLE IF NOT EXISTS "{}" ('
            'document_name text'
            ', rate real'
            ', fraud_words blob'
            ')'
        ).format(self.table_name)
        create_idx_statement = 'CREATE UNIQUE INDEX {index_name} ON {table}({fields})'.format(
            index_name='document_name_idx', table=self.table_name, fields='document_name'
        )

        with autocommit_and_autoclose(self.conn) as cursor:
            cursor.execute(create_table_statement)
            try:
                cursor.execute(create_idx_statement)
            except sqlite3.OperationalError:
                # index already exists
                pass

    def format_document_for_insert_statement(self, document):
        values = [
            '"%s"' % document['document_name'],
            '{:.2f}'.format(document['rate']),
            '"%s"' % list(document['fraud_words']),
        ]

        return '(%s)' % ', '.join(values)

    def insert(self, document_list):
        values = map(self.format_document_for_insert_statement, document_list)

        insert_statement = 'INSERT OR REPLACE INTO {table} VALUES {values}'.format(
            table=self.table_name, values=', '.join(values),
        )

        with autocommit_and_autoclose(self.conn) as cursor:
            cursor.execute(insert_statement)

    def list_table(self):
        with autocommit_and_autoclose(self.conn) as cursor:
            it = cursor.execute('select * from {}'.format(self.table_name))
            result = [dict(zip(self.columns, chunk)) for chunk in it]

        return result