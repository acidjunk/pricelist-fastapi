from http import HTTPStatus

from server.crud.crud_order import order_crud


def test_create_order(test_client, price_1, price_2, kind_1, kind_2, shop_with_products):
    items = [
        {
            "description": "1 gram",
            "price": price_1.one,
            "kind_id": str(kind_1.id),
            "kind_name": kind_1.name,
            "internal_product_id": "01",
            "quantity": 2,
        },
        {
            "description": "1 joint",
            "price": price_2.joint,
            "kind_id": str(kind_2.id),
            "kind_name": kind_2.name,
            "internal_product_id": "02",
            "quantity": 1,
        },
    ]
    body = {
        "shop_id": str(shop_with_products.id),
        "total": 24.0,  # 2x 1 gram of 10,- + 1 joint of 4
        "notes": "Nice one",
        "order_info": items,
    }
    response = test_client.post(f"/api/orders", json=body)
    assert response.status_code == 201, response.json()
    response_json = response.json()
    assert response_json["customer_order_id"] == 1
    assert response_json["total"] == 24.0

    order = order_crud.get_order_by_shop_and_customer_order_id(customer_order_id=1, shop_id=str(shop_with_products.id))
    assert order.shop_id == shop_with_products.id
    assert order.total == 24.0
    assert order.customer_order_id == 1
    assert order.notes == "Nice one"
    assert order.status == "pending"
    assert order.order_info == items

    # test with a second order to also cover the automatic increase of `customer_order_id`
    response = test_client.post(f"/api/orders", json=body)
    response_json = response.json()
    assert response_json["customer_order_id"] == 2
    assert response_json["total"] == 24.0

    assert response.status_code == 201
    order = order_crud.get_order_by_shop_and_customer_order_id(customer_order_id=2, shop_id=str(shop_with_products.id))
    assert order.customer_order_id == 2
