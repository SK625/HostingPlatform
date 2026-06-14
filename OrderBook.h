#ifndef ORDERBOOK_H
#define ORDERBOOK_H

#include <string>
#include <vector>

struct Order {
    std::string contestant_name;
    std::string side; // "BUY" or "SELL"
    double price;
    int quantity;
};

class OrderBook {
private:
    std::vector<Order> buy_orders;
    std::vector<Order> sell_orders;

    // Metrics tracking variables
    int total_processed;
    int successful_matches;
    int system_errors;

public:
    OrderBook();
    void process_order(const Order& order);
    
    // Getters for our three critical metrics
    double get_accuracy() const;
    double get_stability() const;
    int get_speed(double elapsed_seconds) const;
    
    void reset_metrics();
};

#endif