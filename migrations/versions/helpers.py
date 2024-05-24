import sqlalchemy as sa


def update_price_with_shop_ids(conn: sa.engine.Connection, shop_ids: list[str], price_id: str) -> None:
    conn.execute(
        sa.text(
            """
            UPDATE prices 
            SET shop_ids = :shop_ids
            WHERE id = :price_id
        """
        ),
        {"shop_ids": shop_ids, "price_id": price_id},
    )
