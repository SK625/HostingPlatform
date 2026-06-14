#include <iostream>
#include <chrono>
#include <thread>
#include <cstdlib>
#include "OrderBook.h"

void send_telemetry( double accuracy, double stability, int speed) {
    
    
    std::cout << "[METRICS_START]" << std::endl; 
    std::cout << "{" << std::endl; 
    std::cout << " Accuracy: " << accuracy << "%" << std::endl;
    std::cout << " Stability: " << stability << "%" << std::endl;
    std::cout << " Speed: " << speed << " orders/sec" << std::endl;
    std::cout << "}" << std::endl;
    std::cout << "[METRICS_END]" << std::endl;
}

int main() {
    OrderBook book;
    std::string contestant_name = "Contestant_Alpha";
    
    std::cout << "Starting stress test for " << contestant_name << std::endl;
    
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    
    int total_orders = 50000;
    for (int i = 0; i < total_orders; ++i) {
        Order order;
        order.contestant_name = contestant_name;
        order.side = (i % 2 == 0) ? "BUY" : "SELL";
        
        
        if (i % 1000 == 0) {
            order.price = -10.0; 
            order.quantity = 0;
        } else {
            order.price = 100.0 + (std::rand() % 10);
            order.quantity = 1 + (std::rand() % 5);
        }
        
        book.process_order(order);
    }
    
    // Stop the timer ⏱️
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;
    

    double final_accuracy = book.get_accuracy();
    double final_stability = book.get_stability();
    int final_speed = book.get_speed(elapsed.count());
    
    
    send_telemetry(contestant_name, final_accuracy, final_stability, final_speed);
    
    return 0;
}