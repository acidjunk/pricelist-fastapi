from http import HTTPStatus

from server.utils.json import json_dumps


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
    print("Ow yeah baby")
    print(response.json())
    assert response.status_code == 201, response.json()
    # assert response.json["customer_order_id"] == 1, response.json
    # assert response.json["total"] == 24.0
