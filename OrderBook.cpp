#include "OrderBook.h"
#include <cmath>

OrderBook::OrderBook() : total_processed(0), successful_matches(0), system_errors(0) {}

void OrderBook::process_order(const Order& order) {
    total_processed++;

    // Simulate potential stability hiccups (e.g., handling invalid data)
    if (order.price <= 0 || order.quantity <= 0) {
        system_errors++;
        return; 
    }

    // Basic matching logic simulation
    if (order.side == "BUY") {
        buy_orders.push_back(order);
    } else {
        sell_orders.push_back(order);
    }

    // If we have both sides, simulate a match
    if (!buy_orders.empty() && !sell_orders.empty()) {
        auto& buy = buy_orders.back();
        auto& sell = sell_orders.back();

        // Algorithmic Accuracy Check: Did the contestant match valid prices?
        if (buy.price >= sell.price) {
            successful_matches++;
            buy_orders.pop_back();
            sell_orders.pop_back();
        } else {
            // Mismatched prices count against accuracy
            system_errors++; 
        }
    }
}

double OrderBook::get_accuracy() const {
    if (total_processed == 0) return 100.0;
    // Accuracy drops if system errors occur
    return ((double)(total_processed - system_errors) / total_processed) * 100.0;
}

double OrderBook::get_stability() const {
    if (total_processed == 0) return 100.0;
    // Stability drops based on processing failures
    return ((double)(total_processed - system_errors) / total_processed) * 100.0;
}

int OrderBook::get_speed(double elapsed_seconds) const {
    if (elapsed_seconds <= 0) return 0;
    return static_cast<int>(total_processed / elapsed_seconds);
}

void OrderBook::reset_metrics() {
    total_processed = 0;
    successful_matches = 0;
    system_errors = 0;
    buy_orders.clear();
    sell_orders.clear();
}