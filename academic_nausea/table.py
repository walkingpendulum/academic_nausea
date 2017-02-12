import contextlib
import os
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

    def __init__(self, database=None, table_name=None):
        self.db_name = database or 'test'
        self.conn = sqlite3.connect(database=self.db_name)
        self.table_name = table_name or 'results'
        self.fraud_words_table = '%s__fraud_matching' % self.table_name

        self.create_results_table_if_not_exist()
        self.create_fraud_words_table_if_not_exists()

    def create_results_table_if_not_exist(self):
        create_table_statement = (
            'CREATE TABLE IF NOT EXISTS "{}" ('
            'document_name text'
            ', rate real'
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

    def create_fraud_words_table_if_not_exists(self):
        create_table_statement = (
            'CREATE TABLE IF NOT EXISTS "{}" ('
            'document_name text'
            ', fraud_word text'
            ')'
        ).format(self.fraud_words_table)

        with autocommit_and_autoclose(self.conn) as cursor:
            cursor.execute(create_table_statement)

    def insert_one(self, document):
        values_to_insert = '("{document[document_name]}", {document[rate]})'.format(document=document)

        fraud_words_values_to_insert = ' ,'.join([
            '("{document}", "{fraud_word}")'.format(
                document=document['document_name'],
                fraud_word=word
            ) for word in document['fraud_words']
        ])

        insert_results_statement = 'insert or replace into {table} values {values}'.format(
            table=self.table_name, values=values_to_insert,
        )

        insert_fraud_statement = 'insert into {table} values {values}'.format(
            table=self.fraud_words_table, values=fraud_words_values_to_insert,
        )

        with autocommit_and_autoclose(self.conn) as cursor:
            cursor.execute(insert_results_statement)

            cursor.execute('delete from {table} where document_name="{document_name}"'.format(
                table=self.fraud_words_table, document_name=document['document_name']
            ))
            if fraud_words_values_to_insert:
                cursor.execute(insert_fraud_statement)

    def insert(self, document_list):
        print('Results table name: %s, fraud table name: %s' % (self.table_name, self.fraud_words_table))
        print('Saving to database located in %s' % os.path.join(os.path.dirname(__file__), self.db_name))

        for doc in document_list:
            self.insert_one(doc)

    def list_table(self, document_name=None):
        """ Extract document data from db. If document_name is None, extract all data.

        :param document_name: str or None
        :return: list with dict objects with structure {'document_name': str, 'rate': str, 'fraud_words': list}
        """
        inner_select_statement = (
            'select '
                'a.document_name as document_name'
                ', a.rate as rate'
                ", group_concat(b.fraud_word) as fraud_words "
            'from '
                '{results_table} as a '
            'left join '
                '{fraud_table} as b '
            'on '
                'a.document_name = b.document_name '
            'group by '
                'a.document_name '
        ).format(
            results_table=self.table_name, fraud_table=self.fraud_words_table
        )

        if document_name:
            select_statement = (
                'select '
                    't.document_name '
                    ', t.rate '
                    ', t.fraud_words '
                'from '
                    '({inner_select}) as t '
                'where '
                    't.document_name = "{document_name}"'
            ).format(inner_select=inner_select_statement, document_name=document_name)
        else:
            select_statement = inner_select_statement

        result = []
        with autocommit_and_autoclose(self.conn) as cursor:
            it = cursor.execute(select_statement)
            for doc_name, rate, fraud_words in it:
                result.append({
                    'document_name': doc_name,
                    'rate': '%.2f' % rate,
                    'fraud_words': fraud_words
                })

        return result
