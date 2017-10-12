import sys
import random
import time
import os.path
from ethinst import am_tcp_motors as am

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Applied_Motion_SCL_TCP.py - Proof of concept utility to control the Applied Motion SSM23Q motors via TCP.
Motor_IP_X = "192.168.1.10"
Motor_IP_Y = "192.168.1.20"


def do_incremental_move_test(all_axes):
    #  Test each axis from start point to end point, stopping every delta-p.
    #   Looking for cumulative creep-age due to many stop/starts.
    print("Choose which axis to test.")
    for my_axis in all_axes:
        print
        print("Move the machine to a safe starting location:")
        do_move_xy(all_axes)
        print
        print
        ch = raw_input("Test %s axis? (Y=Yes, Enter to skip, Q=Quit): " % my_axis.properties['Name'])
        if ch.upper() == 'Y':
            print
            start_mm = float(raw_input("Enter starting location in mm: "))
            end_mm = float(raw_input("Enter ending location in mm: "))
            dp_mm = float(raw_input("Enter incremental distance in mm: "))
            print
            raw_input("Press enter when ready to move to the finish location (%d mm). " % end_mm)
            my_axis.do_abs_move_wait_complete(mm_to_steps(my_axis, end_mm))
            raw_input("Press enter when ready to move to the start location (%d mm). " % start_mm)
            my_axis.do_abs_move_wait_complete(mm_to_steps(my_axis, start_mm))
            raw_input("Press enter when ready to start the test. ")
            
            my_mm = start_mm
            while my_mm != end_mm:
                my_mm = my_mm + dp_mm
                if my_mm >= end_mm:
                    my_mm = end_mm
                steps = mm_to_steps(my_axis, my_mm)
                print("Start: %d mm, End: %d mm, Moving to: %d mm (%d steps)." % (start_mm, end_mm, my_mm, steps))
                print
                my_axis.do_abs_move_wait_complete(steps)
            print
            print("Done with this axis.")
            print
        elif ch.upper() == 'Q':
            return
    return
        
        
def do_random_move_test(all_axes, num_points=200, park_mm=100):
    # Move each axis to random locations from min_mm to max_mm num_points number of times.
    #  When finished, pack the axes at park_mm location.
    # Tests for final positioning errors after many random moves.
    ch = raw_input("Press enter to move to park position of (%d, %d) mm. (Q to quit)" % (park_mm, park_mm))
    if ch.upper() == 'Q':
        return
    for my_axis in all_axes:
        my_axis.do_abs_move_wait_complete(mm_to_steps(my_axis, park_mm))
    ch = raw_input("Press enter to start random move test. Q to quit.")
    if ch.upper() == 'Q':
        return
    for my_point in range(num_points):
        print
        outs = ""
        for my_axis in all_axes:
            move = random.randint(my_axis.properties['min_mm'], my_axis.properties['max_mm'])
            steps_to_move = mm_to_steps(my_axis, move)
            my_axis.abs_move(steps_to_move)
            outs = outs + my_axis.properties['Name'] + ":"+str(move) + "   "
        print("Moving %d/%d to %s" % (my_point, num_points, outs))
        for my_axis in all_axes:
            my_axis.wait_motor_complete()
            print("%s-Axis position complete at: %s" % (
                my_axis.properties['Name'],
                steps_to_mm(my_axis, my_axis.motor_read("Immediate_Position")))
                )

    print
    print("Now moving to (%d,%d)." % (park_mm, park_mm))
    print

    for my_axis in all_axes:
        my_axis.abs_move(mm_to_steps(my_axis, park_mm))

    for my_axis in all_axes:
        my_axis.wait_motor_complete()
        print("%s-Axis park position: %s" % (my_axis.properties['Name'],
                                             steps_to_mm(my_axis, my_axis.motor_read("Immediate_Position"))))
    return


def log_position(all_axes, sample_interval=0.01):
    done = False

    # prepare holding arrays for data
    my_data = {}
    for my_axis in all_axes:
        my_data[my_axis.properties['Name']] = []

    # assuming both axis have same resolution...
    print
    mm_to_go = float(raw_input("Enter mm to go, both axes (Ctrl-Break to quit): "))
    print
    distance = str(all_axes[0].properties['steps_per_mm'] * mm_to_go)

    print("Moving %d mm (%s counts)..." % (mm_to_go, distance))
    print
    for my_axis in all_axes:
        my_axis.abs_move(distance)

    while not done:
        # sample vel and position
        for my_axis in all_axes:
            my_data[my_axis.properties['Name']].append(my_axis.motor_read("Immediate_Position"))

        # check for motion complete.
        done = True
        for my_axis in all_axes:
            my_axis.update_motor_status()
            if my_axis.Status['Motion_In_Progress']:
                done = False

        time.sleep(sample_interval)
    return my_data


def log_current(all_axes, sample_interval=0.01):
    done = False

    # prepare holding arrays for data
    my_data = {}
    for my_axis in all_axes:
        my_data[my_axis.properties['Name']] = []

    # assuming both axis have same resolution...
    print
    mm_to_go = float(raw_input("Enter mm to go, both axes (Ctrl-Break to quit): "))
    print
    distance = str(all_axes[0].properties['steps_per_mm'] * mm_to_go)

    print("Moving %d mm (%s counts)..." % (mm_to_go, distance))
    print
    for my_axis in all_axes:
        my_axis.abs_move(distance)

    while not done:
        # sample vel and position
        for my_axis in all_axes:
            my_data[my_axis.properties['Name']].append(my_axis.motor_read("Immediate_Current_Actual"))

        # check for motion complete.
        done = True
        for my_axis in all_axes:
            my_axis.update_motor_status()
            if my_axis.Status['Motion_In_Progress']:
                done = False

        time.sleep(sample_interval)
    return my_data


def write_to_file(f_name, my_data):
    f = open(f_name, 'w')
    num_data = 0
    for key in my_data:
        f.write("%s, " % str(key))
        num_data = len(my_data[key])
    f.write('\n')
    idx = 0
    while idx < num_data:
        for col in my_data:
            f.write("%s, " % str(my_data[col][idx]))
        f.write('\n')
        idx = idx + 1
    f.close()
    return


def print_status(stat):
    for item in sorted(stat):
        print("%s : %s" % (str(item), str(stat[item])))
    return


def show_motor_parameters(all_axes):
    #  First, list the properties
    key_len = 0
    # get length of longest key
    for key in sorted(all_axes[0].properties):
        if len(key) > key_len:
            key_len = len(key)
    key_len = key_len + 1
    for key in sorted(all_axes[0].properties):
        s = key
        # align 2nd column based on longest key length
        spaces = key_len - len(key)
        for sp in range(spaces):
            s = s + " "

        for my_axis in all_axes:
            s = s + str(my_axis.make_nice_ascii(my_axis.properties[key])) + '\t'
        print(s)

    # Next the parameters (long)
    key_len = 0
    # get length of longest key
    for key in sorted(all_axes[0].parameters):
        if len(key) > key_len:
            key_len = len(key)
    key_len = key_len + 1
    for key in sorted(all_axes[0].parameters):
        s = key
        # align 2nd column based on longest key length
        spaces = key_len - len(key)
        for sp in range(spaces):
            s = s + " "

        for my_axis in all_axes:
            s = s + str(my_axis.make_nice_ascii(my_axis.parameters[key]))+'\t'
        print(s)

    # Next the status (long)
    key_len = 0
    # get length of longest key
    for key in sorted(all_axes[0].Status):
        if len(key) > key_len:
            key_len = len(key)
    key_len = key_len + 1
    for key in sorted(all_axes[0].Status):
        s = key
        # align 2nd column based on longest key length
        spaces = key_len - len(key)
        for sp in range(spaces):
            s = s + " "

        for my_axis in all_axes:
            s = s + str(my_axis.make_nice_ascii(my_axis.Status[key])) + '\t'
        print(s)
    return


def do_motor_data(all_axes):
    for my_axis in all_axes:
        my_axis.update_motor_status()
        my_axis.get_move_data()
        my_axis.get_motor_hw_settings()
    show_motor_parameters(all_axes)
    return


def do_reset_motor_position(my_axis, abs_pos=0, verbose=False):
    my_axis.reset_position(abs_pos=abs_pos, read_back=True, verbose=verbose)
    new_pos = my_axis.motor_read("Immediate_Position", verbose=verbose)
    print("%s-Axis position: %s [mm]" % (my_axis.properties['Name'], steps_to_mm(my_axis, new_pos)))
    return


def steps_to_mm(my_axis, in_steps):
    return float(in_steps) / my_axis.properties['steps_per_mm']
    

def mm_to_steps(my_axis, in_mm):
    return int(float(in_mm) * my_axis.properties['steps_per_mm'])


def do_move_xy(all_axes):
    # get current position.
    for my_axis in all_axes:
        print("%s-Axis position: %s [mm]" % (my_axis.properties['Name'],
                                             steps_to_mm(my_axis, my_axis.motor_read("Immediate_Position"))))
        my_axis.motor_write(
            "Distance_Position", params=my_axis.parameters['Immediate_Position']['value'], read_back=True
        )
        ch = raw_input("Enter new position in mm, or nothing to keep current: ")
        print
        if ch:
            ch = mm_to_steps(my_axis, int(ch))
            my_axis.motor_write("Distance_Position", params=ch, read_back=True)
    for my_axis in all_axes:
        my_axis.motor_go()
    for my_axis in all_axes:
        my_axis.wait_motor_complete()
    return


def do_home(all_axes):
    home_x = False
    home_y = False
    print
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("1) Home X        2) Home Y")
    print("3) Home everything")
    ch = get_choice(3)
    if ch != 'Q':
        for my_axis in all_axes:
            if my_axis.properties['Name'] == "X" and (ch == 1 or ch == 3):
                my_axis.motor_write("Hard_Stop_Homing", params=0)
                home_x = True
            elif my_axis.properties['Name'] == "Y" and (ch == 2 or ch == 3):
                my_axis.motor_write("Hard_Stop_Homing", params=0)
                home_y = True
        for my_axis in all_axes:
            my_axis.wait_motor_complete()
        for my_axis in all_axes:
            # Set Position to park_mm
            if my_axis.properties['Name'] == "X" and home_x:
                my_axis.reset_position(mm_to_steps(my_axis, my_axis.properties['home_mm']), read_back=True)
                my_axis.properties['homed'] = True
            elif my_axis.properties['Name'] == "Y" and home_y:
                my_axis.reset_position(mm_to_steps(my_axis, my_axis.properties['home_mm']), read_back=True)
                my_axis.properties['homed'] = True
    return


def do_motor_init(my_axis, vel=10, accel=25, decel=30):
    #  Setup initial vel, acceleration
    my_axis.motor_write("Acceleration", params=accel, read_back=True)
    my_axis.motor_write("Deceleration", params=decel, read_back=True)
    my_axis.motor_write("Velocity", params=vel, read_back=True)
    return


def do_setup_homing(my_axis, hc=0.75,
                    hv1=10, hv2=10, hv3=10,
                    ha1=20, ha2=20, ha3=10,
                    hl1=20, hl2=20, hl3=10,
                    home_offset=-20000
                    ):
    my_axis.motor_write("Homing_Current", params=hc, read_back=True)
    my_axis.motor_write("Homing_Velocity1", params=hv1, read_back=True)
    my_axis.motor_write("Homing_Velocity2", params=hv2, read_back=True)
    my_axis.motor_write("Homing_Velocity3", params=hv3, read_back=True)
    my_axis.motor_write("Homing_Acceleration1", params=ha1, read_back=True)
    my_axis.motor_write("Homing_Acceleration2", params=ha2, read_back=True)
    my_axis.motor_write("Homing_Acceleration3", params=ha3, read_back=True)
    my_axis.motor_write("Homing_Deceleration1", params=hl1, read_back=True)
    my_axis.motor_write("Homing_Deceleration2", params=hl2, read_back=True)
    my_axis.motor_write("Homing_Deceleration3", params=hl3, read_back=True)
    my_axis.motor_write("Homing_Offset", params=home_offset, read_back=True)
    return


def do_reset_drives(all_axes):
    for my_axis in all_axes:
        my_axis.motor_write("Restart_Or_Reset")
        my_axis.motor_write("Motor_Enable")
    return


def get_choice(max_num):  # Return number or 'Q'
    ok = 0
    ins = ""
    while not ok:
        ins = raw_input("Enter choice (1..%d), or 'Q' to skip: " % max_num)
        if ins:
            ins = ins.upper()
            if ins != 'Q':
                try:
                    ins = int(ins)
                    if (ins > 0) and (ins <= max_num):
                        ok = 1
                except TypeError:
                    pass
            else:
                ok = 1
    return ins


if __name__ == "__main__":
    all_axis = []
    print
    print
    print("*******************************************************************************")
    x_axis = am.EthernetAppliedMotionTCPMotor(Motor_IP_X, my_name="X", steps_per_mm=4000, min_mm=0.0,
                                              max_mm=975.0, home_mm=5.0, homed=False)
    print("Successfully connected to Ethernet device at IP: " + Motor_IP_X + ", Port: 7776.")
    all_axis.append(x_axis)
    y_axis = am.EthernetAppliedMotionTCPMotor(Motor_IP_Y, my_name="Y", steps_per_mm=4000, min_mm=0.0,
                                              max_mm=500.0, home_mm=5.0, homed=False)
    print("Successfully connected to Ethernet device at IP: " + Motor_IP_Y + ", Port: 7776.")
    all_axis.append(y_axis)
    print("*******************************************************************************")
    print
    for axis in all_axis:
        do_motor_init(axis)
        do_setup_homing(axis)

    do_motor_data(all_axis)
    print
    print
    menu_choice = 0
    while menu_choice != 'Q':
        print("------------------------------------------------------")
        print(" Main Menu")
        print("                        1) Move (x,y)")
        print(" 2) Do Incremental Test 3) Do Random Move Test")
        print(" 4) Log I-Data          5) Log Positional Data")
        print(" 6) Home                7) Display Motor Data")
        print(" 8) Reset X Position    9) Reset Y Position")
        print("10) Reset drives")
        menu_choice = get_choice(10)
        if menu_choice != 'Q':
            if menu_choice == 1:
                do_move_xy(all_axis)
            elif menu_choice == 2:
                do_incremental_move_test(all_axis)
            elif menu_choice == 3:
                do_random_move_test(all_axis)
            elif menu_choice == 4:
                data = log_current(all_axis)
                write_to_file('I-data.csv', data)
            elif menu_choice == 5:
                data = log_position(all_axis)
                write_to_file('Pos-data.csv', data)
            elif menu_choice == 6:
                do_home(all_axis)
            elif menu_choice == 7:
                do_motor_data(all_axis)
            elif menu_choice == 8:
                do_reset_motor_position(x_axis)
            elif menu_choice == 9:
                do_reset_motor_position(y_axis)
            elif menu_choice == 10:
                do_reset_drives(all_axis)

    for axis in all_axis:
        axis.close()
