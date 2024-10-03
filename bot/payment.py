from tinkoff_acquiring_api import TinkoffAcquiring
import os

req = TinkoffAcquiring(terminal=os.getenv("PAY_TERMINAL"), secret_key=os.getenv("PAY_SECRET"))


async def get_url_payment(order_id: int, amount: int, description: str):
    preload = {"Description": description,
               "Amount": amount * 100, "OrderId": order_id,
               "NotificationURL": os.getenv("PAY_NOTIFICATION")}
    link = req.init(payload=preload)
    return link.get('PaymentURL')
