import sys
import time
import os.path
from threading import Timer
from ethinst import EthernetInstrument

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EthernetAppliedMotionTCPMotor(EthernetInstrument):
    # motor commands - Specific for the Applied Motion SSM motor-drive combination.
    #  I used: ssm23q-2eg
    #  Definitions are based on "Host-Command-Reference_920-0002N.PDF"
    #  Only select commands are listed below, as I needed to test what I wanted to test.
    #  Add more as you see fit.
    commands = {
        'Acceleration': {
            'cmd': 'AC', 'units': 'rps/s', 'range_low': 0.167, 'range_high': 5461.167,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the acceleration rate used in point-to-point move commands in \
            rev/sec/sec.'
            },

        'Alarm_Code': {
            'cmd': 'AL', 'units': 'Binary', 'range_low': 0, 'range_high': 0,
            'type': 'int', 'read': True, 'write': False,
            'help': 'Reads back an equivalent hexadecimal value of the Alarm Codes 16-bit binary word.'
            },

        'Alarm_Reset_Immediate': {
            'cmd': 'AR', 'units': 'None', 'range_low': 0, 'range_high': 0,
            'type': 'none', 'read': False, 'write': True,
            'help': 'Clears Alarms and Drive Faults. If an Alarm or Drive Fault condition persists after \
            sending the AR command the Alarm is not cleared.'
            },

        'Deceleration': {
            'cmd': 'DE', 'units': 'rps/s', 'range_low': 0.167, 'range_high': 5461.167,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the deceleration rate used in point-to-point move commands in \
            rev/sec/sec.'
            },

        'Distance_Position': {
            'cmd': 'DI', 'units': 'steps', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'int', 'read': True, 'write': True,
            'help': 'Sets or requests the move distance in encoder counts (servo) or steps (stepper).'
            },

        'Encoder_Position': {
            'cmd': 'EP', 'units': 'steps', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'int', 'read': True, 'write': True,
            'help': 'The EP command allows the host to define the present encoder position.'
            },

        'Encoder_Resolution': {
            'cmd': 'ER', 'units': 'counts/rev', 'range_low': 200, 'range_high': 128000,
            'type': 'int', 'read': True, 'write': True,
            'help': 'Sets the encoder resolution in quadrature counts.'
            },

        'Feed_To_Position': {
            'cmd': 'FP', 'units': 'steps', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'int', 'read': False, 'write': True,
            'help': 'Executes an absolute move command.'
            },

        'Current_Command': {
            'cmd': 'GC', 'units': '0.01 Arms', 'range_low': -2000, 'range_high': 2000,
            'type': 'int', 'read': True, 'write': True,
            'help': 'Sets or requests the immediate current command for the servo motor.'
            },

        'Homing_Acceleration1': {
            'cmd': 'HA1', 'units': 'rps/s', 'range_low': 0.167, 'range_high': 5461.167,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the acceleration rate used in Extended Homing Mode and \
            Hard Stop Homing Mode'
            },

        'Homing_Acceleration2': {
            'cmd': 'HA2', 'units': 'rps/s', 'range_low': 0.167, 'range_high': 5461.167,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the acceleration rate used in Extended Homing Mode and \
            Hard Stop Homing Mode'
            },

        'Homing_Acceleration3': {
            'cmd': 'HA3', 'units': 'rps/s', 'range_low': 0.167, 'range_high': 5461.167,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the acceleration rate used in Extended Homing Mode and \
            Hard Stop Homing Mode'
            },

        'Hard_Stop_Current': {
            'cmd': 'HC', 'units': 'Amps', 'range_low': 0.01, 'range_high': 2000,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the threshold current to be used in Hard Stop Homing mode \
            (see HS command).'
            },

        'Home_Offset': {
            'cmd': 'DI', 'units': 'steps', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'int', 'read': True, 'write': True,
            'help': 'Sets or requests the move distance in steps after the home sensor has been \
            reached.  Sign determines homing direction.'
            },

        'Hard_Stop_Homing': {
            'cmd': 'HS', 'units': 'None', 'range_low': 0, 'range_high': 1,
            'type': 'int', 'read': False, 'write': True,
            'help': 'Executes the Hard Stop Homing. process, which may optionally search for the \
            first encoder index pulse after finding a rigid mechanical end stop in the chosen direction.'
            },

        'Homing_Velocity1': {
            'cmd': 'HV1', 'units': 'rps', 'range_low': 0.0042, 'range_high': 80.0000,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the shaft speed used in the Extended Homing (EF) and \
            Hard Stop Homing (HS) modes.'
            },

        'Homing_Velocity2': {
            'cmd': 'HV2', 'units': 'rps', 'range_low': 0.0042, 'range_high': 80.0000,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the shaft speed used in the Extended Homing (EF) and \
            Hard Stop Homing (HS) modes.'
            },

        'Homing_Velocity3': {
            'cmd': 'HV3', 'units': 'rps', 'range_low': 0.0042, 'range_high': 80.0000,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests the shaft speed used in the Extended Homing (EF) and \
            Hard Stop Homing (HS) modes.'
            },

        'Immediate_Position': {
            'cmd': 'IP', 'units': 'steps', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'int', 'read': True, 'write': False,
            'help': 'Requests present absolute position.'
            },

        'Immediate_Current_Actual': {
            'cmd': 'IQ', 'units': '0.01Amps', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'int', 'read': True, 'write': False,
            'help': 'Requests present actual current. This current reading is the actual current \
            measured by the drive.'
            },

        'Immediate_Velocity': {
            'cmd': 'IV', 'units': 'rpm', 'range_low': 0, 'range_high': 1,
            'type': 'int', 'read': True, 'write': True,
            'help': 'Requests present velocity of the motor in rpm. There are two different \
            velocities that can be read back: the motor actual velocity and the motor \
            target velocity.'
            },

        'Motor_Disable': {
            'cmd': 'MD', 'units': 'none', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'none', 'read': False, 'write': True,
            'help': 'Disables motor outputs (reduces motor current to zero).'
            },

        'Motor_Enable': {
            'cmd': 'ME', 'units': 'none', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'none', 'read': False, 'write': True,
            'help': 'Restores drive current to motor. If the drive cannot be enabled due to the \
            Enable Input (SI) state, the drive will respond with a &.'
            },

        'Restart_Or_Reset': {
            'cmd': 'RE', 'units': 'none', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'none', 'read': False, 'write': True,
            'help': 'Restarts the drive by resetting fault conditions and re-initializing the drive \
            with the startup parameters.'
            },

        'Request_Status': {
            'cmd': 'RS', 'units': 'none', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'string', 'read': True, 'write': False,
            'help': 'Asks the drive to respond with what it is doing.'
            },

        'Status_Code': {
            'cmd': 'SC', 'units': 'binary', 'range_low': 0x0, 'range_high': 0x8000,
            'type': 'hex', 'read': True, 'write': False,
            'help': 'Requests the current drive status as the Hexadecimal equivalent of a \
            binary word.'
            },

        'Set_Position': {
            'cmd': 'SP', 'units': 'steps', 'range_low': -2147483647, 'range_high': 2147483647,
            'type': 'int', 'read': True, 'write': True,
            'help': 'Sets or requests the motor absolute position. To ensure that the internal \
            position counter resets properly, use EP immediately prior to sending SP.'
            },

        'Velocity': {
            'cmd': 'VE', 'units': 'rps', 'range_low': 0.0042, 'range_high': 60.0,
            'type': 'float', 'read': True, 'write': True,
            'help': 'Sets or requests shaft speed for point-to-point move commands like \
            FL, FP, FS, FD, SH, etc.'
            }

    }

    def __init__(
            self, host, port=7776, my_name="default_motor", steps_per_mm=4000, min_mm=0.0,
            max_mm=100.0, home_mm=5.0, homed=False, loc_mm=0
    ):  # port 7776 is the fixed TCP port for these motors
        # Constants
        self.SCL_OPCODE = chr(0)+chr(7)
        
        # Variables
        self.properties = {
            'Name': my_name,
            'IP': host,
            'Port': port,
            'steps_per_mm': steps_per_mm,
            'min_mm': min_mm,
            'max_mm': max_mm,
            'home_mm': home_mm,
            'homed': homed,
            'loc_mm': loc_mm
        }
        # Results of the "Request_Status" command
        self.Status = {
            'Alarm': False,
            'Disabled': False,
            'Drive_Fault': False,
            'Motor_Moving': False,
            'Homing': False,
            'Jogging': False,
            'Motion_In_Progress': False,
            'In_Position': False,
            'Ready': False,
            'Stopping': False,
            'Wait_Time': False,
            'Wait_Input': False,
        }
        # Results of calling the defined commands.  Values may optionally be NOT updated (to save time).  When
        #  the parameter is written to, and the value is not updated, the 'updated' field is set to 'False'.
        self.parameters = {}
        for command in self.commands:
            self.parameters[command] = {'value': 0, 'updated': False}

        EthernetInstrument.__init__(self, host, port=port, term='\r')

        # Init the idle timer to keep the TCP socket alive (the motors will close any inactive
        # TCP sockets after ~20 seconds.  This idle timeout is not configurable on the drives.
        self._idle_timer = None
        self.idle_timer_interval = 10
        self.idle_timer_is_running = False
        # Start the idle_timer
        self.idle_timer_start()
        
    def send_scl_cmd(self, cmd, parse_char='=', strip=True, verbose=False):
        #  Applied Motion's SCL commands must all have the '\0x0\0x7' prefix opcode.
        if verbose:
            print("send_scl_cmd: cmd = %s" % str(cmd))

        # If there's any activity sent to the motor drives, then turn off the idle_timer.
        self.idle_timer_stop()

        resp = self.cmd(self.SCL_OPCODE + cmd, verbose=verbose)
        if verbose:
            print("send_scl_cmd: resp = %s" % str(resp))
        # Responses from the motors are like "<op-code>cmd=response<term>")
        
        # return the right-half of the resp, split on parse_char
        if parse_char:
            resp = resp.split(parse_char)[-1]
            
        # Remove op-code prefix from the response (if it exists)
        if resp[0:2] == self.SCL_OPCODE:
            resp = resp[2:]
            
        # remove any other whitespace (strip does not remove the leading op-code for some reason)
        if strip:
            resp = resp.strip()
        if verbose:
            print("send_scl_cmd: final resp = %s" % str(resp))

        # start the idle timer
        self.idle_timer_start()
        return resp

    def motor_read(self, command, verbose=False):
        resp = "Command not found."
        if command in self.commands:
            if self.commands[command]['read']:
                resp = self.send_scl_cmd(self.commands[command]['cmd'], verbose=verbose)
                self.parameters[command]['value'] = resp
                self.parameters[command]['updated'] = True
            else:
                resp = "Command <%s> is not readable." % command
        return resp

    def motor_write(self, command, params="", read_back=False, verbose=False):
        resp = "Command not found."
        if command in self.commands:
            my_cmd = self.commands[command]
            if my_cmd['write']:
                resp = self.send_scl_cmd(my_cmd['cmd'] + str(params), verbose=verbose)
                self.parameters[command]['updated'] = False

                if my_cmd['read'] and read_back:
                    resp = self.motor_read(command, verbose)
            else:
                resp = "Command <%s> is not writeable." % command
        return resp

    def update_motor_status(self, verbose=False):
        resp = self.motor_read("Request_Status", verbose=verbose)
        self.Status = dict()
        self.Status['Alarm'] = True if ('A' in resp) else False
        self.Status['Disabled'] = True if ('D' in resp) else False
        self.Status['Drive_Fault'] = True if ('E' in resp) else False
        self.Status['Motor_Moving'] = True if ('F' in resp) else False
        self.Status['Homing'] = True if ('H' in resp) else False
        self.Status['Jogging'] = True if ('J' in resp) else False
        self.Status['Motion_In_Progress'] = True if ('M' in resp) else False
        self.Status['In_Position'] = True if ('P' in resp) else False
        self.Status['Ready'] = True if ('R' in resp) else False
        self.Status['Stopping'] = True if ('S' in resp) else False
        self.Status['Wait_Time'] = True if ('T' in resp) else False
        self.Status['Wait_Input'] = True if ('W' in resp) else False
        self.get_alarm_code(verbose=verbose)
        return

    def get_alarm_code(self, verbose=False):
        outs = ""
        resp = "0x"+self.motor_read("Alarm_Code", verbose=verbose)
        bc = int(resp, 16)  # Convert hex-string to a hex number.

        if bc & 1:
            outs = outs + " >Position Limit"
        if bc & 2:
            outs = outs + " >CCW Limit"
        if bc & 4:
            outs = outs + " >CW Limit"
        if bc & 8:
            outs = outs + " >OverTemp"
        if bc & 0x10:
            outs = outs + " >Internal Voltage"
        if bc & 0x20:
            outs = outs + " >Over Voltage"
        if bc & 0x40:
            outs = outs + " >Under Voltage"
        if bc & 0x80:
            outs = outs + " >Over Current"
        if bc & 0x100:
            outs = outs + " >Open Motor Winding"
        if bc & 0x200:
            outs = outs + " >Bad Encoder"
        if bc & 0x400:
            outs = outs + " >COM Error"
        if bc & 0x800:
            outs = outs + " >Bad Flash"
        if bc & 0x1000:
            outs = outs + " >No Move"
        if bc & 0x2000:
            outs = outs + " >na"
        if bc & 0x4000:
            outs = outs + " >Blank Q Segment"
        if bc & 0x8000:
            outs = outs + " >na"
        if outs == "":
            outs = "No Alarm."

        self.Status['Alarm Code'] = outs
        return outs

    def get_move_data(self, verbose=False):
        for command in ["Acceleration", "Deceleration", "Velocity", "Current_Command", "Current_Position"]:
            self.motor_read(command, verbose=verbose)
        return

    def get_motor_hw_settings(self, verbose=False):
        for command in ["Encoder_Resolution", "Immediate_Position", "Immediate_Velocity", "Immediate_Current_Actual",
                        "Homing_Current"]:
            self.motor_read(command, verbose=verbose)
        return

    def motor_go(self, verbose=False):
        self.motor_write("Feed_To_Position", verbose=verbose)
        return

    def abs_move(self, abs_pos, read_back=False, verbose=False):
        resp = self.motor_write("Distance_Position", params=abs_pos, read_back=read_back, verbose=verbose)
        self.motor_go(verbose=verbose)
        if not read_back:
            resp = ""
        return resp

    def reset_position(self, abs_pos=0, read_back=False, verbose=False):
        self.motor_write("Encoder_Position", params=str(abs_pos), read_back=read_back, verbose=verbose)
        resp = self.motor_write("Set_Position", params=str(abs_pos), read_back=read_back, verbose=verbose)
        if not read_back:
            resp = ""
        return resp

    def wait_motor_complete(self):
        self.update_motor_status()
        while self.Status['Motion_In_Progress']:
            time.sleep(0.5)
            self.update_motor_status()
        return

    def do_abs_move_wait_complete(self, pos_abs):
        # move to a new location, using absolute coordinates, and wait for the move to complete
        # accelerations and velocity must already be set
        self.abs_move(pos_abs)
        self.wait_motor_complete()
        return

    @staticmethod
    def convert_string_hex16_to_num(ins, signed=True):
        resp = int(ins, 16)
        if signed:
            if resp > 0x7FFFFFFF:
                resp = resp - 0x100000000
        return resp

    #
    #  Idle Timer Functions
    #

    def idle_update_stats(self):
        self.update_motor_status()
        return

    def _idle_timer_run(self):
        self.idle_timer_is_running = False
        self.idle_timer_start()
        self.idle_update_stats()

    def idle_timer_start(self):
        if not self.idle_timer_is_running:
            self._idle_timer = Timer(self.idle_timer_interval, self._idle_timer_run)
            self._idle_timer.start()
            self.idle_timer_is_running = True

    def idle_timer_stop(self):
        self._idle_timer.cancel()
        self.idle_timer_is_running = False
