# app/services/notification.py
import datetime
from app import models

class NotificationService:
    @staticmethod
    def send_order_accepted_alert(order: models.Order, username: str):
        """
        Triggers an alert when the shopkeeper accepts the customer's order.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Real production systems would integrate Twilio, SendGrid, or WebSockets here
        print(f"\n==================================================")
        print(f"🔔 [NOTIFICATION TO CUSTOMER: @{username}]")
        print(f"Timestamp: {timestamp}")
        print(f"Status   : ✅ ORDER ACCEPTED")
        print(f"Order ID : #{order.id}")
        print(f"Total    : Rs. {order.total_amount}")
        print(f"Delivery : {order.delivery_date} to {order.delivery_location}")
        print(f"Message  : The shopkeeper has approved your schedule. Your items are on the way!")
        print(f"==================================================\n")

    @staticmethod
    def send_order_rejected_alert(order: models.Order, username: str):
        """
        Triggers an alert when the shopkeeper rejects the customer's order.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n==================================================")
        print(f"🔔 [NOTIFICATION TO CUSTOMER: @{username}]")
        print(f"Timestamp: {timestamp}")
        print(f"Status   : ❌ ORDER REJECTED")
        print(f"Order ID : #{order.id}")
        print(f"Message  : Sorry, the shopkeeper cannot fulfill your order due to scheduling conflicts.")
        print(f"Action   : Your items have been restocked, and payment holds released.")
        print(f"==================================================\n")
