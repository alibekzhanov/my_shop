import random
from .payment_gateaway import PaymentSystem

class FakePaymentSystem(PaymentSystem):
    
    VALID_CARDS = {
        "4242424242424242" :
        {
            "cvc" : "666",
            "expired_date" : "1212",
        }
    }

    def create_payment(self, amount, card_number, cvc, expired_date):
        validation = self.valid_card(card_number, cvc, expired_date)
        if validation["status"] == "success":
            validation["message"] = f"C карты <b>{card_number}</b> снялось {amount} тенге"
            
        return validation
    
    def valid_card(self, card_number, cvc, expired_date):
        try:
            card = self.VALID_CARDS[card_number]

            if card:
                if card['cvc'] == cvc and card['expired_date'] == expired_date:
                    return {
                    "status": "success",
                    "transaction_id": random.randint(100000, 999999),
                    "message": "Транзанкция прошла"
                    }
                    pass
                else:
                    return {
                    "status": "failed",
                    "transaction_id": random.randint(100000, 999999),
                    "message": "Данные карты введены не верно"
                    }
            else:
                return {
                    "status": "failed",
                    "transaction_id": random.randint(100000, 999999),
                    "message": "Такой карты нет"
                }
        except:
                return {
                    "status": "failed",
                    "transaction_id": random.randint(100000, 999999),
                    "message": "Такой карты нет"
                }

        