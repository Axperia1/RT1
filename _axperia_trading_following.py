class TrailingStop:
    def __init__(self, trailing_percentage):
        self.trailing_percentage = trailing_percentage
        self.entry_price = None
        self.trail_price = None

    def enter_position(self, price):
        self.entry_price = price
        self.trail_price = price * (1 - self.trailing_percentage / 100)
        print(f"Entered position at {price}. Initial trail price set at {self.trail_price}.")

    def update_price(self, current_price):
        if self.entry_price is None:
            print("No position entered.")
            return
        
        # Calculate new trailing stop price
        new_trail_price = current_price * (1 - self.trailing_percentage / 100)

        # Update trail price if the current price has increased
        if current_price > self.entry_price and new_trail_price > self.trail_price:
            self.trail_price = new_trail_price
            print(f"Updated trail price to {self.trail_price} based on current price {current_price}.")

    def exit_position(self, current_price):
        if self.trail_price is not None and current_price <= self.trail_price:
            print(f"Exited position at {current_price}.")
            self.entry_price = None
            self.trail_price = None
        elif self.entry_price is None:
            print("No position to exit.")

# Example of how to use the TrailingStop class
if __name__ == "__main__":
    trailing_stop = TrailingStop(trailing_percentage=3)
    trailing_stop.enter_position(price=100)

    # Simulating price updates
    price_updates = [102, 104, 103, 105, 100, 98]
    for price in price_updates:
        trailing_stop.update_price(current_price=price)
        trailing_stop.exit_position(current_price=price)