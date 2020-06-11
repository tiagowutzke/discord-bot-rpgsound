class Query:
    def __init__(
            self,
            conn=None,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.connection = conn

    @staticmethod
    def get_cols_param(columns):
        # Casting list to words comma separated
        is_more_one_column = len(columns) > 1
        return ', '.join(columns) if is_more_one_column else columns[0], is_more_one_column

    def query_all(self, table, column, where_col=None, value=None, use_where=True, where_type='text'):
        """ Query generic table and columns

        :param table:
        :param column:
        :param where_col:
        :param value:
        :param use_where: bool to indicate if query use where
        :param where_type: int, text, bigger than (int)
        :return:
        """
        try:
            select = f"""
                SELECT
                    {column}
                FROM   
                    {table}
                """

            if use_where:

                if where_type == 'text':
                    comparison = f"ilike '%{value}%'"
                elif where_type == 'int':
                    comparison = f"= {value}"
                else:
                    comparison = f'>= {value}'

                where = f"""
                    WHERE
                        {where_col} {comparison}
                """
            else:
                where = ""

            order = """
                ORDER BY
                    created_at desc
            """

            sql = select + where + order
            self.connection.cursor.execute(sql)

            return self.connection.cursor.fetchall()

        except Exception as e:
            print(f'Error on query:\n{e}')
            return False

    def query_audio_by_tag(self, table, validation):
        try:
            sql = f"""
                SELECT
                    validation
                FROM   
                    {table}
                WHERE
                    tag ilike '%{validation}%'
            """

            self.connection.cursor.execute(sql)

            return self.connection.cursor.fetchall()

        except Exception as e:
            print(f'Error on query:\n{e}')
            return False

    def query_config(self):
        try:
            sql = f"""
                SELECT
                    channel_voice_id,
                    channel_text_id,
                    valid_score_single_pred,
                    valid_score_multiple_pred,
                    valid_score_suggestions
                FROM   
                    config
            """

            self.connection.cursor.execute(sql)

            return self.connection.cursor.fetchall()[0]

        except Exception as e:
            print(f'Error on query:\n{e}')
            return False
