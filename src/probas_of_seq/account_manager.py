import os
from uuid import uuid4
from tinkoff.invest import Client, OrderDirection, OrderType


class AccountManager:

    def __init__(self, figi: str, id_acc: str) -> None:
        self.figi = figi
        self.id_acc = id_acc
        self.state = None

    def manage_orders(self, signal: str, quantity: int) -> None:

        order_id = str(uuid4())
        if (signal is None or signal == '0') and self.state is not None:
            if self.state == 'long':
                with Client(os.getenv('TOKEN')) as cli:
                    cli.orders.post_order(
                        figi=self.figi,
                        quantity=quantity,
                        direction=OrderDirection.ORDER_DIRECTION_SELL,
                        account_id=self.id_acc,
                        order_type=OrderType.ORDER_TYPE_MARKET,
                        order_id=order_id
                    )
                self.state = None
                print('[Long side closed]')
            if self.state == 'short':
                with Client(os.getenv('TOKEN')) as cli:
                    cli.orders.post_order(
                        figi=self.figi,
                        quantity=quantity,
                        direction=OrderDirection.ORDER_DIRECTION_BUY,
                        account_id=self.id_acc,
                        order_type=OrderType.ORDER_TYPE_MARKET,
                        order_id=order_id
                    )
                self.state = None
                print('[Short side closed]')
            return None

        # open initial order
        order_id = str(uuid4())
        if self.state is None and signal == '1':
            with Client(os.getenv('TOKEN')) as cli:
                cli.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    account_id=self.id_acc,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                    order_id=order_id
                )
            self.state = 'long'
            print('[Long side opened]')
            return None
        if self.state is None and signal == '-1':
            with Client(os.getenv('TOKEN')) as cli:
                cli.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    account_id=self.id_acc,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                    order_id=order_id
                )
            self.state = 'short'
            print('[Short side opened]')
            return None

        # close the previous deal
        order_id = str(uuid4())
        if self.state == 'long':
            with Client(os.getenv('TOKEN')) as cli:
                cli.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    account_id=self.id_acc,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                    order_id=order_id
                )
            self.state = None
            print('[Long side closed]')
        if self.state == 'short':
            with Client(os.getenv('TOKEN')) as cli:
                cli.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    account_id=self.id_acc,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                    order_id=order_id
                )
            self.state = None
            print('[Short side closed]')
        # open next order
        order_id = str(uuid4())
        if signal == '1':
            with Client(os.getenv('TOKEN')) as cli:
                cli.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    account_id=self.id_acc,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                    order_id=order_id
                )
            self.state = 'long'
            print('[Long side opened]')
            return None
        if signal == '-1':
            with Client(os.getenv('TOKEN')) as cli:
                cli.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    account_id=self.id_acc,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                    order_id=order_id
                )
            self.state = 'short'
            print('[Short side opened]')
            return None
