#include "../components/pkt4_mcu/pkt4_mcu.cpp"
#include <cassert>
#include <iostream>
using namespace esphome;
std::vector<uint8_t> frame(uint8_t pid, std::vector<uint8_t> payload) {
 std::vector<uint8_t> b{0x5a,0xa5,uint8_t(payload.size()+8),pid,0,0xff};
 b.insert(b.end(),payload.begin(),payload.end()); auto crc=crc16be(b.data(),b.size(),0xffff);
 b.push_back(crc&255);b.push_back(crc>>8);return b;
}
void feed(pkt4_mcu::PKT4MCUComponent &m, const std::vector<uint8_t> &b) {
 m.input.insert(m.input.end(),b.begin(),b.end());m.loop();
}
class ExposedMCU : public pkt4_mcu::PKT4MCUComponent {
 public: using PKT4MCUComponent::send_;
};
int main() {
 { ExposedMCU m; uint8_t data[249]{};
   m.send_(1,data,247); assert(m.output.size()==255);
   m.send_(1,data,248); assert(m.output.size()==255);
   m.send_(1,data,249); assert(m.output.size()==255);
 }

 pkt4_mcu::PKT4MCUComponent m; sensor::Sensor w; m.set_weight_sensor(&w);
 auto good=frame(7,{0,1,0x00,0x00,0x78,0x00});
 for(auto c:good) feed(m,{c});
 assert(w.count==1 && w.state==0x780000);
 auto bad=good;bad.back()^=1;feed(m,bad);assert(w.count==1);
 feed(m,frame(7,{0,255}));assert(w.count==1);
 for(int len=0;len<8;++len) feed(m,{0x5a,0xa5,uint8_t(len)});
 feed(m,good);assert(w.count==2);
 feed(m,{0x5a,0xa5,255,7});test_now+=201;feed(m,good);assert(w.count==3);
 for(auto pid:{1,7,9}) for(int n=0;n<14;++n) feed(m,frame(pid,std::vector<uint8_t>(n,0)));
 m.motor(0,3,1,100,0,1000);assert(m.motors_idle());
 bool allowed=true;m.set_movement_allowed([&](){return allowed;});
 m.motor(0,3,1,100,0,1000);assert(!m.motors_idle());
 allowed=false;m.loop();assert(m.motors_idle());
 allowed=true;m.motor(1,3,1,100,0,1000);test_now+=120001;m.loop();assert(m.motors_idle());
 // Interlock stop is resent 3 more times (100 ms apart) in case a frame is lost.
 {for(int i=0;i<5;++i){test_now+=101;m.loop();}
  allowed=true;m.motor(0,3,1,100,0,1000);allowed=false;m.output.clear();m.loop();
  size_t one=m.output.size();assert(one>0);
  for(int i=0;i<10;++i){test_now+=101;m.loop();}
  assert(m.output.size()==one*4);allowed=true;}
 // An MCU reset clears motor state and the partial frame buffer.
 {m.motor(0,3,1,100,0,1000);assert(!m.motors_idle());m.deinit();assert(m.motors_idle());}
 // MCU stop event (0x3, 0xA0|motor, state 3) marks the motor idle but keeps the
 // safety watchdog armed: losing the interlock still sends a stop.
 {allowed=true;m.motor(1,3,1,100,0,1000);assert(!m.motors_idle());
  feed(m,frame(3,{0x81,2,0,1,100,7}));assert(!m.motors_idle());       // progress report
  feed(m,frame(3,{0xA1,3,1,1,100,7}));assert(m.motors_idle());       // stopped event
  allowed=false;m.output.clear();m.loop();assert(!m.output.empty());allowed=true;
  m.motor(1,3,1,100,0,1000);assert(!m.motors_idle());}              // new run re-arms
 // A CRC error must not drop the remaining bytes of the same UART read.
 {auto b=good;b.back()^=1;b.insert(b.end(),good.begin(),good.end());size_t c=w.count;feed(m,b);assert(w.count==c+1);}
 // Exercise arbitrary and truncated traffic under ASan/UBSan.
 uint32_t r=12345;
 for(int i=0;i<10000;++i) {r=r*1664525+1013904223;feed(m,{uint8_t(r>>24)});}
 test_now+=201;feed(m,good);assert(w.state==0x780000);
 std::cout<<"MCU framing and motor interlock regression tests passed\n";
}
