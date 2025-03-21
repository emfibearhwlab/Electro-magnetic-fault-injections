import time
from ctypes import *

def enum(**enums):
    return type('Enum', (), enums)

RST_SRC = enum(CPU=0, EVCG=1, SW_RST=2)
EVCG_RST_POLARITY = enum(ACTIVE_LOW=0, ACTIVE_HIGH=1)
EVCG_TRIGGER_SRC = enum(TRIGGER_IN=0, TRIGGER_OUT=1, PWR_DWN_TRIGGER=2, SW_TRIGGER=3)
EVCG_TRIGGER_EDGE = enum(RISING=1, FALLING=0)
GLITCH_MODE = enum(VCC=0, CLK=1, LASER=2, EMBEDDED_VCC=3, EMBEDDED_LASER=4)
REG = enum(R0=0, R1=1, R2=2, R3=3)
WAIT = enum(TX_BUSY=0, TX_SIGNAL=1, TRIGGER=2)
SET = enum(CURRENT_LIM=4, TRIGGER_PWR_DOWN_EN=5, SW_PWR_DOWN=6, GLITCH_EN=7, TRIGGER_OUT=8, SC_RST=9, PATTERN_RST=10, LOGGER_EN=11)
GET = enum(TRIGGER_IN=12, TX_FIFO_EMPTY=13)
CLK = enum(SPEED_1MHZ=0, SPEED_2MHZ=1, SPEED_3MHZ=2, SPEED_4MHZ=3)

class VCGlitcherError(Exception):
   def __init__(self, value):
      self.value = value
   def __str__(self):
      return repr(self.value)

class vcg_version(Structure):
    _fields_ = [("pcb_version", c_uint),
                ("bitstream_version", c_ubyte * 16),
                ("firmware_version", c_ubyte)]

class vcg_device(Structure):
    _fields_ = [("locationId", c_ulong),
                ("serialNumber", c_ubyte * 16),
                ("description", c_ubyte * 64),
                ("version_info", vcg_version),
                ("handle", c_void_p),
                ("config_buffer", POINTER(c_ubyte))]

def check_error(status):
   if(status > 0):
      raise VCGlitcherError({
         1: "VC Glitcher could not be found.",
         2: "VC Glitcher version not compatible wth this SDK.",
         3: "USB communication error.",
         4: "An invalid mode was specified.",
         5: "An invalid memory address was specified.",
         6: "An smart card FIFO access with invalid length was specified.",
         7: "An invalid LCD line was specified.",
         8: "An invalid smart card clock speed was specified.",
         9: "An invalid pattern selection was specified.",
        10: "An invalid pattern length was specified.",
        11: "The Embedded Glitcher pattern buffer is full.",
        12: "Invalid Embedded VC Glitcher delay or duration.",
        13: "The accumulated delay overflows.",
        14: "The accumulated duration overflows.",
        15: "An invalid handle was specified.",
        16: "An invalid glitch voltage was specified.",
        17: "An invalid VCC voltage was specified.",
        18: "An invalid clock voltage was specified.",
        19: "An invalid clock high voltage was specified.",
        20: "An invalid clock low voltage was specified.",
        21: "An invalid laser voltage was specified.",
        22: "An invalid VCC and clock voltage was specified.",
        23: "An invalid offset voltage was specified.",
        24: "An incalid current limit voltage was specified.",
        25: "An invalid PWM channel was indexed.",
        26: "An invalid PWM voltage was specified.",
        27: "Operation failed.",
        28: "Cannot create dump file.",
        29: "Cannot create program array.",
        30: "An invalid index of CPU register was specified.",
        31: "An invalid shift length was specified.",
        32: "The label has already been used.",
        33: "An undefined label has been referred.",
        34: "'END' instruction is missing.",
        35: "An invalid immediate value was specified.",
        36: "An invalid memory address was specified.",
        37: "An invalid wait signal was specified.",
        38: "An invalid set signal was specified.",
        39: "An invalid get signal was specified.",
        40: "The user memory is larger than the memory capacity.",
        41: "The specified program is empty.",
        42: "A NULL pointer is passed as argument.",
        43: "VC Glitcher has already been opened.",
        44: "VC Glitcher has not been opened.",
        45: "Cannot add program while TVCG is active.",
        46: "Cannot remove program while TVCG is active.",
        47: "Timeout during TVCG operation.",
        }.get(status, "Unknown error"))
 
class VCGlitcher:
   """VC Glitcher python implementation"""

   wrapper_version = "2.0"

   def __init__(self):
      self.vcg_dll = CDLL(r"C:\Users\EMFI\Downloads\Riscure\Riscure\VC Glitcher SDK\lib\x64\vcglitcher.dll")
      self.device = vcg_device()
      #if self.__class__.wrapper_version > version_parts[0]:
      if self.__class__.wrapper_version > self.sdk_get_version():
      #if( self.__class__.wrapper_version > self.sdk_get_version()[0].split('-')[0] ):
         print '[WARNING]Wrapper version newer than the VC Glitcher SDK library'

   def check_version(self):
         version_raw = self.sdk_get_version()  # Make sure this is within the class
         version_string = version_raw.decode('utf-8')
         version_parts = version_string.split('-')
         if self.wrapper_version > version_raw:  # Comparison logic
             print("Version check passed.")
         else:
             print("Version check failed.")
             print(version_parts)

   def device_list(self):
      count = c_uint()
      check_error(self.vcg_dll.vcg_device_list(byref(count)))
      return count.value

   def device_get_info(self, index):
      assert isinstance(index, int)
      check_error(self.vcg_dll.vcg_device_get_info(byref(self.device), c_uint(index)))
      return 

   def set_read_timeout(self, timeout):
      assert isinstance(timeout, int)
      check_error(self.vcg_dll.vcg_set_read_timeout(byref(self.device), c_uint(timeout)))

   def set_write_timeout(self, timeout):
      assert isinstance(timeout, int)
      check_error(self.vcg_dll.vcg_set_write_timeout(byref(self.device), c_uint(timeout)))

   def open(self):
      check_error(self.vcg_dll.vcg_open(byref(self.device)))

   def get_version(self):
      version_buffer = c_char_p("xx.yy.zz")
      check_error(self.vcg_dll.vcg_get_version(byref(self.device), version_buffer, 9))
      return version_buffer.value.split('.')
      

   def get_serial_number(self):
      return str(bytearray(self.device.serialNumber)).split('\x00')[0]

   def set_mode(self, mode):
      assert isinstance(mode, int)
      check_error(self.vcg_dll.vcg_set_mode(byref(self.device), c_int(mode)))
      return mode

   def is_card_inserted(self):
      inserted = c_int()
      check_error(self.vcg_dll.vcg_is_card_inserted(byref(self.device), byref(inserted)))
      return bool(inserted.value)

   def set_offset(self, v_offset):
      assert (isinstance(v_offset, float) or isinstance(v_offset, int))
      check_error(self.vcg_dll.vcg_set_offset(byref(self.device), c_double(v_offset)))

   def set_current_limit(self, v_limit):
      assert (isinstance(v_limit, float) or isinstance(v_limit, int))
      check_error(self.vcg_dll.vcg_set_current_limit(byref(self.device), c_double(v_limit)))

   def set_vcc_glitch_parameter(self, v_vcc, v_clk, v_glitch):
      assert (isinstance(v_vcc, float) or isinstance(v_vcc, int))
      assert (isinstance(v_clk, float) or isinstance(v_clk, int))
      assert (isinstance(v_glitch, float) or isinstance(v_glitch, int))
      check_error(self.vcg_dll.vcg_set_vcc_voltage(byref(self.device), c_double(v_vcc), c_double(v_glitch), c_double(v_clk)))

   def set_clk_glitch_parameter(self, v_vcc, v_clk_hi, v_clk_lo, v_glitch):
      assert (isinstance(v_vcc, float) or isinstance(v_vcc, int))
      assert (isinstance(v_clk_hi, float) or isinstance(v_clk_hi, int))
      assert (isinstance(v_clk_lo, float) or isinstance(v_clk_lo, int))
      assert (isinstance(v_glitch, float) or isinstance(v_glitch, int))
      check_error(self.vcg_dll.vcg_set_clk_voltage(byref(self.device), c_double(v_clk_hi), c_double(v_clk_lo), c_double(v_glitch), c_double(v_vcc)))

   def set_laser_glitch_parameter(self, v_amplitude, v_vcc_clk):
      assert (isinstance(v_amplitude, float) or isinstance(v_amplitude, int))
      assert (isinstance(v_vcc_clk, float) or isinstance(v_vcc_clk, int))
      check_error(self.vcg_dll.vcg_set_laser_voltage(byref(self.device), c_double(v_amplitude), c_double(v_vcc_clk)))

   def set_program(self, vcg_program):
      assert (isinstance(vcg_program, VCGlitcherProgram))
      check_error(self.vcg_dll.vcg_set_program(byref(self.device), vcg_program.get_handle()))

   def cpu_get_speed(self):
      cpu_speed = c_uint()
      check_error(self.vcg_dll.vcg_get_cpu_frequency(byref(self.device),byref(cpu_speed)))
      return int(cpu_speed.value)

   def cpu_start(self):
      check_error(self.vcg_dll.vcg_start_cpu(byref(self.device)))

   def cpu_stop(self):
      check_error(self.vcg_dll.vcg_stop_cpu(byref(self.device)))

   def is_cpu_stopped(self):
      status = c_int()
      check_error(self.vcg_dll.vcg_get_cpu_status(byref(self.device), byref(status)))
      return bool(status.value)

   def memory_get_size(self):
      size = c_uint()
      check_error(self.vcg_dll.vcg_memory_get_size(byref(self.device), byref(size)))
      return size.value

   def memory_write(self, address, data):
      assert (isinstance(address, int))
      assert (isinstance(data, int))
      check_error(self.vcg_dll.vcg_memory_write(byref(self.device), c_uint(address), c_uint(data)))

   def memory_read(self, address):
      assert (isinstance(address, int))
      data = c_uint()
      check_error(self.vcg_dll.vcg_memory_read(byref(self.device), c_uint(address), byref(data)))
      return data.value

   def smartcard_fifo_write(self, data):
      assert (isinstance(data, list))
      assert (len(data) > 0)
      byte_array = bytearray(data)
      cbuff = c_char * len(data)
      address = cbuff.from_buffer(byte_array)
      check_error(self.vcg_dll.vcg_sc_write(byref(self.device), byref(address), c_uint(len(data))))

   def smartcard_fifo_read(self, n_read):
      assert (isinstance(n_read, int))
      n_readout = c_uint()
      if(n_read == 0):
         buffer_len = 2048
      else:
         buffer_len = n_read
      byte_array = bytearray(buffer_len)
      cbuff = c_char * buffer_len
      address = cbuff.from_buffer(byte_array)
      check_error(self.vcg_dll.vcg_sc_read(byref(self.device), byref(address), c_uint(n_read), byref(n_readout)))
      return list(byte_array[:n_readout.value])

   def smartcard_set_clock_speed(self, clk_speed):
      assert (isinstance(clk_speed, int))
      check_error(self.vcg_dll.vcg_set_sc_clock_speed(byref(self.device), c_int(clk_speed)))

   def pattern_load(self, pattern):
      assert (isinstance(pattern, list))
      assert (len(pattern) > 0 )
      byte_array = bytearray(pattern)
      cbuff = c_char * len(pattern)
      address = cbuff.from_buffer(byte_array)
      r = check_error(self.vcg_dll.vcg_pattern_set(byref(self.device), byref(address), c_uint(len(pattern))))
      if r == None:
         return "pattern loaded successfully"

   def pattern_enable(self):
      check_error(self.vcg_dll.vcg_pattern_enable(byref(self.device)))

   def pattern_disable(self):
      check_error(self.vcg_dll.vcg_pattern_disable(byref(self.device)))

   def smartcard_reset_config(self, src, polarity):
      check_error(self.vcg_dll.vcg_sc_reset_configuration(byref(self.device), c_uint(src), c_uint(polarity)))

   def set_smartcard_soft_reset(self, value):
      assert isinstance(value, int)
      check_error(self.vcg_dll.vcg_set_sc_soft_reset(byref(self.device), c_uint(value)))

   def sdk_get_version(self):
      #ret = c_char_p(self.vcg_dll.vcg_sdk_get_version())
      ret = self.vcg_dll.vcg_sdk_get_version()
      if isinstance(ret, int):
         return str(ret)  # Convert to string if it's an integer
      return ret.value


    # Your logic here    
      #return ret.value.split()
      #return ret

   def sdk_is_snapshot_version(self):
      ret = self.vcg_dll.vcg_sdk_is_snapshot_version()
      return bool(ret)

   def close(self):
      check_error(self.vcg_dll.vcg_close(byref(self.device)))

   '''
   >>>Transparent VC Glitcher API functions<<<
   '''
   def tvcg_sync_enable(self, enabled):
      assert isinstance(enabled, bool)
      check_error(self.vcg_dll.vcg_tvcg_enable_sync(byref(self.device), c_int(enabled)))

   def tvcg_add_program(self, vcg_program):
      assert isinstance(vcg_program, VCGlitcherProgram)
      check_error(self.vcg_dll.vcg_tvcg_add_perturbation_program(byref(self.device), vcg_program.get_handle()))

   def tvcg_execute_direct(self, vcg_program):
      assert isinstance(vcg_program, VCGlitcherProgram)
      check_error(self.vcg_dll.vcg_tvcg_execute_direct(byref(self.device), vcg_program.get_handle()))

   def tvcg_start(self):
      check_error(self.vcg_dll.vcg_tvcg_powerup(byref(self.device)))

   def tvcg_stop(self):
      check_error(self.vcg_dll.vcg_tvcg_powerdown(byref(self.device)))

   def tvcg_smartcard_baudrate_update(self, baudrate):
      assert isinstance(baudrate, int)
      check_error(self.vcg_dll.vcg_tvcg_update_baudrate(byref(self.device), c_uint(baudrate)))

   def tvcg_smartcard_reset(self):
      check_error(self.vcg_dll.vcg_tvcg_reset_sc(byref(self.device)))

   def tvcg_smartcard_reset_glitch(self, n_wait, vcg_program):
      assert isinstance(n_wait, int)
      assert isinstance(vcg_program, VCGlitcherProgram)
      check_error(self.vcg_dll.vcg_tvcg_reset_sc_glitch(byref(self.device), c_uint(n_wait), vcg_program.get_handle()))

   def tvcg_write(self, data, n_wait, vcg_program):
      assert isinstance(data, list)
      assert isinstance(n_wait, int)
      assert isinstance(vcg_program, VCGlitcherProgram)
      assert (len(data) > 0)
      byte_array = bytearray(data)
      cbuff = c_char * len(data)
      address = cbuff.from_buffer(byte_array)
      f = check_error(self.vcg_dll.vcg_tvcg_command(byref(self.device), byref(address), c_uint(len(data)), c_uint(n_wait), vcg_program.get_handle()))
      return f

   def tvcg_read(self, n_read):
      assert isinstance(n_read, int)
      if( n_read == 0 ):
         bufflen = 2048
      else:
         bufflen = n_read
      n_readout = c_uint()
      byte_array = bytearray(bufflen)
      cbuff = c_char * bufflen
      address = cbuff.from_buffer(byte_array)
      check_error(self.vcg_dll.vcg_tvcg_get_response(byref(self.device), byref(address), c_uint(n_read), byref(n_readout)))
      return list(byte_array[:n_readout.value])

   def tvcg_available(self):
      available = c_int()
      check_error(self.vcg_dll.vcg_tvcg_is_available(byref(self.device), byref(available)))
      return bool(available.value)

   '''
   >>>Embedded VC Glitcher API functions<<<
   '''
   def evcg_clear_pattern(self):
      check_error(self.vcg_dll.vcg_evcg_clear_pattern(byref(self.device)))

   def evcg_add_pattern(self, delay, duration):
      assert (isinstance(delay, int) and isinstance(duration, int))
      check_error(self.vcg_dll.vcg_evcg_add_pattern_pair(byref(self.device), c_uint(delay), c_uint(duration)))

   def evcg_set_pattern(self):
      check_error(self.vcg_dll.vcg_evcg_set_pattern(byref(self.device)))

   def evcg_set_arm(self, armed):
      assert isinstance(armed, bool)
      check_error(self.vcg_dll.vcg_evcg_set_arm(byref(self.device), c_int(armed)))

   def evcg_trigger_config(self, src, edge):
      stat = check_error(self.vcg_dll.vcg_evcg_trigger_configuration(byref(self.device), c_uint(src), c_uint(edge)))
      return src

   def evcg_soft_start(self):
      try:
         check_error(self.vcg_dll.vcg_evcg_soft_start(byref(self.device)))
         return True  # Success
      except Exception as e:
        print "Failed to start glitch:", e  
        return False  

   def evcg_power_down_en(self, enabled):
      assert isinstance(enabled, bool)
      check_error(self.vcg_dll.vcg_evcg_pd_en(byref(self.device), c_int(enabled)))

   def evcg_get_guaranteed_pattern_number(self):
      n_pattern = c_uint()
      check_error(self.vcg_dll.vcg_evcg_get_guaranteed_pattern_number(byref(self.device), byref(n_pattern)))
      return n_pattern.value

   def evcg_busy(self):
      busy = c_int()
      check_error(self.vcg_dll.vcg_evcg_busy(byref(self.device), byref(busy)))
      return bool(busy.value)

   def evcg_is_available(self):
      ret = c_int()
      check_error(self.vcg_dll.vcg_evcg_is_available(byref(self.device), byref(ret)))
      return bool(ret.value)

   def evcg_add_glitch(self, g_delay, g_length, g_repeat):
      check_error(self.vcg_dll.vcg_evcg_add_glitch(byref(self.device), c_uint(g_delay), c_uint(g_length), c_uint(g_repeat)))
      return [g_delay, g_length, g_repeat]

class VCGlitcherProgram:
   """VC Glitcher program implementation"""

   def __init__(self):
      self.vcg_dll = CDLL(r"C:\Users\EMFI\Downloads\Riscure\Riscure\VC Glitcher SDK\lib\x64\vcglitcher.dll")
      self.handle = c_void_p(self.vcg_dll.vcg_as_create_program())

   def renew(self):
      check_error(self.vcg_dll.vcg_as_destroy_program(self.handle))
      self.handle = c_void_p(self.vcg_dll.vcg_as_create_program())

   def get_handle(self):
      return self.handle

   def print_program(self):
      check_error(self.vcg_dll.vcg_as_print_program(self.handle))

   def assemble_program(self):
      check_error(self.vcg_dll.vcg_as_check_program(self.handle))

   def add_label(self, label):
      assert isinstance(label,str)
      cbuff = create_string_buffer(label)
      check_error(self.vcg_dll.vcg_as_add_label(self.handle, byref(cbuff)))

   def nop(self):
      check_error(self.vcg_dll.vcg_as_nop(self.handle))

   def jmpr(self, rj):
      check_error(self.vcg_dll.vcg_as_jmpr(self.handle, c_int(rj)))

   def ret(self):
      check_error(self.vcg_dll.vcg_as_ret(self.handle))

   def loadi(self, rd, data):
      assert isinstance(rd, int)
      assert isinstance(data, int)
      check_error(self.vcg_dll.vcg_as_loadi(self.handle, c_int(rd), c_uint(data)))

   def loadm(self, rd, address):
      assert isinstance(rd, int)
      assert isinstance(address, int)
      check_error(self.vcg_dll.vcg_as_loadm(self.handle, c_int(rd), c_uint(address)))

   def storem(self, address, rs):
      assert isinstance(address, int)
      assert isinstance(rs, int)
      check_error(self.vcg_dll.vcg_as_storem(self.handle, c_uint(address), c_int(rs)))

   def loadr(self, rd, rs):
      assert isinstance(rd, int)
      assert isinstance(rs, int)
      check_error(self.vcg_dll.vcg_as_loadr(self.handle, c_int(rd), c_int(rs)))

   def loadf(self, rd):
      assert isinstance(rd, int)
      check_error(self.vcg_dll.vcg_as_loadf(self.handle, c_int(rd)))

   def storer(self, rd, rs):
      assert isinstance(rd, int)
      assert isinstance(rs, int)
      check_error(self.vcg_dll.vcg_as_storer(self.handle, c_int(rd), c_int(rs)))

   def addi(self, rd, data):
      assert isinstance(rd, int)
      assert isinstance(data, int)
      check_error(self.vcg_dll.vcg_as_addi(self.handle, c_int(rd), c_uint(data)))

   def subi(self, rd, data):
      assert isinstance(rd, int)
      assert isinstance(data, int)
      check_error(self.vcg_dll.vcg_as_subi(self.handle, c_int(rd), c_uint(data)))

   def shiftl(self, rd, shift):
      assert isinstance(rd, int)
      assert isinstance(shift, int)
      check_error(self.vcg_dll.vcg_as_shiftl(self.handle, c_int(rd), c_uint(shift)))

   def shiftr(self, rd, shift):
      assert isinstance(rd, int)
      assert isinstance(shift, int)
      check_error(self.vcg_dll.vcg_as_shiftr(self.handle, c_int(rd), c_uint(shift)))

   def jmp(self, label):
      assert isinstance(label, str)
      cbuff = create_string_buffer(label)
      check_error(self.vcg_dll.vcg_as_jmp(self.handle, byref(cbuff)))

   def cmpeq(self, ra, rb):
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_cmpeq(self.handle, c_int(ra), c_int(rb)))

   def cmpgt(self, ra, rb):
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_cmpgt(self.handle, c_int(ra), c_int(rb)))

   def cmplt(self, ra, rb):
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_cmplt(self.handle, c_int(ra), c_int(rb)))

   def cmpgte(self, ra, rb):
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_cmpgte(self.handle, c_int(ra), c_int(rb)))

   def cmplte(self, ra, rb):
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_cmplte(self.handle, c_int(ra), c_int(rb)))

   def cmpz(self, ra):
      assert isinstance(ra, int)
      check_error(self.vcg_dll.vcg_as_cmpz(self.handle, c_int(ra)))

   def branch0(self, label):
      assert isinstance(label, str)
      cbuff = create_string_buffer(label)
      check_error(self.vcg_dll.vcg_as_branch0(self.handle, byref(cbuff)))

   def branch1(self, label):
      assert isinstance(label, str)
      cbuff = create_string_buffer(label)
      check_error(self.vcg_dll.vcg_as_branch1(self.handle, byref(cbuff)))

   def wait_signal(self, signal, val):
      assert isinstance(signal, int)
      assert isinstance(val, int)
      check_error(self.vcg_dll.vcg_as_waitsignal(self.handle, c_int(signal), c_byte(val)))

   def waittime(self, rt):
      assert isinstance(rt, int)
      check_error(self.vcg_dll.vcg_as_waittime(self.handle, c_int(rt)))

   def counter_rst(self):
      check_error(self.vcg_dll.vcg_as_counter_rst(self.handle))

   def addr(self, rd, ra, rb):
      assert isinstance(rd, int)
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_addr(self.handle, c_int(ra), c_int(rb), c_int(rd)))

   def subr(self, rd, ra, rb):
      assert isinstance(rd, int)
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_subr(self.handle, c_int(ra), c_int(rb), c_int(rd)))
      
   def notr(self, rd, ra):
      assert isinstance(rd, int)
      assert isinstance(ra, int)
      check_error(self.vcg_dll.vcg_as_notr(self.handle, c_int(ra), c_int(rd)))

   def xorr(self, rd, ra, rb):
      assert isinstance(rd, int)
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_xorr(self.handle, c_int(rd), c_int(ra), c_int(rb)))

   def andr(self, rd, ra, rb):
      assert isinstance(rd, int)
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_andr(self.handle, c_int(rd), c_int(ra), c_int(rb)))

   def orr(self, rd, ra, rb):
      assert isinstance(rd, int)
      assert isinstance(ra, int)
      assert isinstance(rb, int)
      check_error(self.vcg_dll.vcg_as_orr(self.handle, c_int(rd), c_int(ra), c_int(rb)))

   def backup(self):
      check_error(self.vcg_dll.vcg_as_backup(self.handle))

   def restore(self):
      check_error(self.vcg_dll.vcg_as_restore(self.handle))

   def counter_move(self, rd):
      assert isinstance(rd, int)
      check_error(self.vcg_dll.vcg_as_counter_move(self.handle, c_int(rd)))

   def end(self):
      check_error(self.vcg_dll.vcg_as_end(self.handle))

   def set_signal(self, signal, val):
      assert isinstance(signal, int)
      assert isinstance(val, int)
      check_error(self.vcg_dll.vcg_as_set_signal(self.handle, c_int(signal), c_byte(val&0xff)))

   def get_signal(self, rd, signal):
      assert isinstance(rd, int)
      assert isinstance(signal, int)
      check_error(self.vcg_dll.vcg_as_get_signal(self.handle, c_int(rd), c_int(signal)))

   def recvr(self, rd):
      assert isinstance(rd, int)
      check_error(self.vcg_dll.vcg_as_recvr(self.handle, c_int(rd)))
      
   def sendi(self, data):
      assert isinstance(data, int)
      check_error(self.vcg_dll.vcg_as_sendi(self.handle, c_byte(data)))

   def sendq(self):
      check_error(self.vcg_dll.vcg_as_sendq(self.handle))

   def sendr(self, rs):
      assert isinstance(rs, int)
      check_error(self.vcg_dll.vcg_as_sendr(self.handle, c_int(rs)))

   def sync(self):
      check_error(self.vcg_dll.vcg_as_sync(self.handle))
      
   def txconfig(self, rs, i, dp):
      assert isinstance(rs, int)
      assert isinstance(i, int)
      assert isinstance(dp, int)
      check_error(self.vcg_dll.vcg_as_txconfig(self.handle, c_int(rs), c_byte(i), c_byte(dp)))

   def rxconfig(self, rs, i, dp):
      assert isinstance(rs, int)
      assert isinstance(i, int)
      assert isinstance(dp, int)
      check_error(self.vcg_dll.vcg_as_rxconfig(self.handle, c_int(rs), c_byte(i), c_byte(dp)))

   def get_tx_inc(self, baudrate):
      return c_int(self.vcg_dll.vcg_as_get_tx_incremental_value(c_int(baudrate))).value

   def get_rx_inc(self, baudrate):
      return c_int(self.vcg_dll.vcg_as_get_rx_incremental_value(c_int(baudrate))).value

if __name__ == "__main__":
    vcg = VCGlitcher()




