import logging

from database.query import Query

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Persistence:
    def __init__(
            self,
            conn=None,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.connection = conn
        self.query = Query()

    def insert(self, table, **cols_values):

        columns, _ = self.query.get_cols_param(cols_values.keys())
        values, _ = self.query.get_cols_param(cols_values.values())

        try:
            sql = f"""
                INSERT INTO {table} ({columns})
                VALUES ({values});
            """
            self.connection.commit_transaction(sql)
            return True

        except Exception as e:
            message = f'Error on insert values:\n{e}'
            logging.info(message)
            return False

    def update_by_col(self, table, column, value, where_col, col_value, value_type='text'):
        try:
            value = f"'{value}'" if value_type is 'text' else value

            sql = f"""
                UPDATE {table}
                SET {column} = {value}
                WHERE {where_col} = {col_value}
            """
            self.connection.commit_transaction(sql)
            return True

        except Exception as e:
            message = f'Error on update:\n{e}'
            print(message)
            return False

    def update_config(self, **cols_values):
        try:
            columns, _ = self.query.get_cols_param(cols_values.keys())
            values, _ = self.query.get_cols_param(cols_values.values())

            sql = f"""
                UPDATE config
                SET ({columns}) = ({values})                    
            """

            self.connection.commit_transaction(sql)
            return True
        except Exception as e:
            message = f'Error on update config:\n{e}'
            print(message)
            return False

    def delete_by_id(self, table, id):
        try:
            sql = f"""
                DELETE FROM {table}
                WHERE id = {id}
            """
            self.connection.commit_transaction(sql)
        except Exception as e:
            message = f'Error on delete:\n{e}'
            print(message)

    def delete_all(self, table):
        try:
            sql = f"""
                TRUNCATE TABLE {table};
            """
            self.connection.commit_transaction(sql)
        except Exception as e:
            message = f'Error on delete:\n{e}'
            print(message)

    def update_timed_out_train_status(self):
        try:
            sql = """
                UPDATE
                    train_status
                SET
                    status = 'ERROR',
                    message = 'Timed out'
                WHERE
                    created_at >= now() - '30 minutes'::INTERVAL
                    AND status = 'WAITING'
            """
            self.connection.commit_transaction(sql)
        except Exception as e:
            message = f'Error on update timed out status:\n{e}'
            print(message)