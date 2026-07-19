# SE Week 01 SOLID Strategy Boundary Example

> Week 01 · Software Engineering Refresh. A small Strategy + Dependency Inversion example: domain pricing depends on a policy interface, not vendor/infrastructure code.

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Order:
    customer_tier: str
    subtotal_cents: int

class DiscountPolicy(Protocol):
    def discount_cents(self, order: Order) -> int: ...

class TierDiscount:
    def __init__(self, rates):
        self.rates = rates
    def discount_cents(self, order):
        return int(order.subtotal_cents * self.rates.get(order.customer_tier, 0.0))

class NoDiscount:
    def discount_cents(self, order):
        return 0

class Pricer:
    def __init__(self, policy: DiscountPolicy):
        self.policy = policy          # depends on abstraction, not concrete vendor logic
    def total_cents(self, order):
        discount = self.policy.discount_cents(order)
        if discount < 0 or discount > order.subtotal_cents:
            raise ValueError("invalid discount policy result")
        return order.subtotal_cents - discount

order = Order(customer_tier="gold", subtotal_cents=10_000)
print(Pricer(TierDiscount({"gold": 0.15})).total_cents(order))
print(Pricer(NoDiscount()).total_cents(order))
```


Related: [[03 Permanent Notes/SE Week 01 SOLID Principles Quick Reference]]
