
class Checkout:
    class Discount:
        def __init__(self, item_num, price):
            self.item_num = item_num
            self.price = price

    def __init__(self):
        self.prices = {}
        self.discounts = {}
        # self.total = 0
        self.items = {}

    def addDiscount(self, item, numb_of_items, price):
        discount = self.Discount(numb_of_items, price)
        self.discounts[item] = discount

    def addItemPrice(self, item, price):
        self.prices[item] = price

    def addItem(self, item):
        if item not in self.prices:
            raise Exception("Wrong Item!")
        if item in self.items:
            self.items[item] += 1
        else:
            self.items[item] = 1

    def calculateTotal(self):
        total = 0
        for item, quantity in self.items.items():
            total += self.calculateItemTotal(item, quantity)
        return total

    def calculateItemTotal(self, item, quantity):
        total = 0
        if item in self.discounts:
            discount = self.discounts[item]
            if quantity >= discount.item_num:
                total += self.calculateDiscountedItemTotal(item, quantity, discount)
            else:
                total += self.prices[item] * quantity
        else:
            total += self.prices[item] * quantity
        return total

    def calculateDiscountedItemTotal(self, item, quantity, discount):
        total = 0
        num_of_discounts = quantity / discount.item_num
        total += num_of_discounts * discount.price
        remaining = quantity % discount.item_num
        total += remaining * self.prices[item]
        return total
