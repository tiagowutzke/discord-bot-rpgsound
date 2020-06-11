def get_suggestion_by_id(query, id):
    return query.query_all(
        table='label_suggestions',
        column='suggested_table, suggested_label, validation',
        where_type='int',
        where_col='id',
        value=id
    )[0]


def update_suggestion(persistence, table, label, validation):
    return persistence.update_by_col(
        table=table,
        column='validation',
        value=f"validation || '; {validation}'",
        where_col='tag',
        value_type='not_text',
        col_value=f"'{label}'"
    )


def delete_suggestion(persistence, id):
    return persistence.delete_by_id(
        table='label_suggestions',
        id=id
    )
