import requests
import json

from settings import qiwi_token, qiwi_account

class qiwi:
    def __init__(self):
        pass

    def get_payments(self, count=50):
        session = requests.Session()
        session.headers['authorization'] = 'Bearer ' + qiwi_token
        parameters = {'rows': str(count)}
        response = session.get(f"https://edge.qiwi.com/payment-history/v1/persons/{qiwi_account}/payments", params = parameters)
        req = json.loads(response.text)
        return req['data']

    def check_payment(self, code, sum):
        """
        Status:
        0 - not found
        1 - found, but error
        2 - found and all right
        """
        status = 0
        for payment in self.get_payments():
            if(payment['comment'] == str(code)):
                status = 1
                if(payment['status'] == 'SUCCESS' and payment['sum']['amount'] >= sum):
                    return 2
        return status

if __name__ == "__main__":
    pay = qiwi()
    print(pay.check_payment('96171', 3))

