#pragma once
#include <esphome/core/component.h>
namespace esphome { namespace uart {
constexpr int UART_CONFIG_PARITY_NONE=0, UART_DIRECTION_RX=0;
class UARTDevice { public:
 std::deque<uint8_t> input; std::vector<uint8_t> output;
 size_t available() { return input.size(); }
 bool read_byte(uint8_t *b) { if(input.empty()) return false; *b=input.front(); input.pop_front(); return true; }
 void write_array(uint8_t *b, size_t n) { output.insert(output.end(),b,b+n); }
 void check_uart_settings(int,int,int,int) {}
};
}}
