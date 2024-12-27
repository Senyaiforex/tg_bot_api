from tinkoff_acquiring_api import TinkoffAcquiring
import os

terminal = str(os.getenv("PAY_TERMINAL"))
secret = os.getenv("PAY_SECRET")
req = TinkoffAcquiring(terminal=terminal, secret_key=secret)

async def get_url_payment(order_id: int, amount: int, description: str,
                          pay_notification: str):
    preload = {"Description": description,
               "Amount": amount * 100, "OrderId": order_id,
               "NotificationURL": pay_notification}
    link = req.init(payload=preload)
    return link.get('PaymentURL')
