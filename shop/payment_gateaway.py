from abc import ABC, abstractmethod


class PaymentSystem(ABC):

    @abstractmethod
    def create_payment(self, amount, card_number, cvc, expired_date):
        pass

    @abstractmethod
    def valid_card(self, card_number, cvc, expired_date):
        pass