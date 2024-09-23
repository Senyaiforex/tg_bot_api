from tinkoff_acquiring_api import TinkoffAcquiring

req = TinkoffAcquiring(terminal="1706544854516DEMO", secret_key="uae9ewzltfbrwv0y")


async def get_url_payment(order_id: int, amount: int, description: str):
    preload = {"Description": description,
               "Amount": amount * 100, "OrderId": order_id,
               "NotificationURL": "https://2128-188-68-160-86.ngrok-free.app/payment"}
    link = req.init(payload=preload)
    return link.get('PaymentURL')
