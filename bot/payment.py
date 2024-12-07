from tinkoff_acquiring_api import TinkoffAcquiring
import os

req = TinkoffAcquiring(terminal=os.getenv("PAY_TERMINAL"), secret_key=os.getenv("PAY_SECRET"))


async def get_url_payment(order_id: int, amount: int, description: str,
                          pay_notification: str):
    preload = {"Description": description,
               "Amount": amount * 100, "OrderId": order_id,
               "NotificationURL": pay_notification}
    link = req.init(payload=preload)
    return link.get('PaymentURL')
