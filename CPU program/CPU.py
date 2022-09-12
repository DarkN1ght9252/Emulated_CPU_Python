class ControlUnit:
    """A ControlUnit"""

    def __init__(self):
        self.is_stopped = False
        self.instruction_register = 0
        self.programCounter = 0
        self.memoryAddressRegister = 0
        self.memoryBufferRegister = 0
        self.accumulator = 0
        self.operandRegister = 0
        self.isDirect = False
        self.memory = RAM()
        self.alu = ALU(False, False, False, False)

    def fetch_instruction(self):
        self.memoryAddressRegister = self.programCounter
        self.memory.is_write = False
        self.memoryBufferRegister = self.memory.read_byte(self.memoryAddressRegister)
        self.programCounter += 1
        self.instruction_register = self.memoryBufferRegister

    def decode_instruction(self):
        if not self.instruction_register == 0:
            self.memoryAddressRegister = self.programCounter
            self.memory.is_write = False
            self.memoryBufferRegister = self.memory.read_byte(self.memoryAddressRegister)
            self.programCounter += 1
            self.operandRegister = self.memoryBufferRegister
        if self.instruction_register == 3 or self.instruction_register == 5 or self.instruction_register == 7:
            self.isDirect = True
        else:
            self.isDirect = False

    def fetch_operand(self):
        if self.isDirect:
            self.memoryAddressRegister = self.operandRegister
            self.memory.is_write = False
            self.memoryBufferRegister = self.memory.read_byte(self.memoryAddressRegister)
            self.operandRegister = self.memoryBufferRegister

    def execute(self):
        if self.instruction_register == 0:
            self.stop()

        if self.instruction_register == 2:
            self.load()

        if self.instruction_register == 3:
            self.load()

        if self.instruction_register == 4:
            self.store()

        if self.instruction_register == 5:
            self.store()

        if self.instruction_register == 6:
            self.compare()

        if self.instruction_register == 7:
            self.compare()

        if self.instruction_register == 8:
            self.jump()

        if self.instruction_register == 9:
            self.jump_if_equal()

        if self.instruction_register == 10:
            self.jump_if_less_than()

        if self.instruction_register == 11:
            self.jump_if_greater_than()

    def load(self):
        self.alu.set_control_signal(0)
        self.alu.set_left_operand(self.operandRegister)
        self.alu.execute()
        self.accumulator = self.alu.output

    def store(self):
        self.memory.is_write = True
        self.memory.write_byte(self.operandRegister, self.accumulator)

    def compare(self):
        self.alu.set_left_operand(self.accumulator)
        self.alu.set_right_operand(self.operandRegister)

    def jump(self):
        self.programCounter = self.operandRegister

    def jump_if_equal(self):
        if self.alu.isZero:
            self.programCounter = self.operandRegister

    def jump_if_greater_than(self):
        if self.alu.isNegative and not self.alu.isOverflow or not self.alu.isNegative and self.alu.isOverflow:
            self.programCounter = self.operandRegister

    def jump_if_less_than(self):
        if self.alu.isNegative and self.alu.isOverflow or not self.alu.isNegative and not self.alu.isOverflow and not self.alu.isZero:
            self.programCounter = self.operandRegister

    def stop(self):
        self.is_stopped = True

    def to_string(self):
        print("Control Unit Statistics")
        print("\tACCUMULATOR: ", self.accumulator)
        print("\tPROGRAM COUNTER: ", self.programCounter)
        print("\tINSTRUCTION REGISTER: ", self.instruction_register)
        print("\tMEMORY ADDRESS REGISTER: ", self.memoryAddressRegister)
        print("\tMEMORY BUFFER REGISTER: ", self.memoryBufferRegister)
        print("\tOPERAND REGISTER: ", self.operandRegister, "\n")


class ALU:
    """A ALU"""

    def __init__(self, is_negative, is_overflow, is_zero, is_carry):
        self.isNegative = is_negative
        self.isOverflow = is_overflow
        self.isZero = is_zero
        self.isCarry = is_carry
        self.leftOperand = 0
        self.rightOperand = 0
        self.output = 0
        self.controlSignal = 0

    def set_negative(self, negative):
        self.isNegative = negative

    def set_overflow(self, overflow):
        self.isOverflow = overflow

    def set_zero(self, zero):
        self.isZero = zero

    def set_carry(self, carry):
        self.isCarry = carry

    def get_negative(self):
        return self.isNegative

    def get_overflow(self):
        return self.isOverflow

    def get_zero(self):
        return self.isZero

    def get_carry(self):
        return self.isCarry

    def set_left_operand(self, left_operand):
        self.leftOperand = left_operand

    def set_right_operand(self, right_operand):
        self.rightOperand = right_operand
        self.execute()

    def set_output(self, output):
        self.output = output
        self.execute()

    def set_control_signal(self, control_signal):
        self.controlSignal = control_signal
        self.execute()

    def get_left_operand(self):
        return self.leftOperand

    def get_right_operand(self):
        return self.rightOperand

    def get_output(self):
        return self.output

    def get_control_signal(self):
        return self.controlSignal

    def execute(self):
        if self.controlSignal == 0:
            self.pass_through()

        if self.controlSignal == 1:
            self.add()

        if self.controlSignal == 2:
            self.compare()

    def add(self):
        self.output = self.leftOperand + self.rightOperand
        if self.output == 0:
            self.isZero = True
        else:
            if self.output < 0:
                self.isNegative = True
        if self.isNegative:
            if self.output > 127:
                self.isOverflow = True
            if self.output < -128:
                self.isOverflow = True
        else:
            if self.output < 0:
                self.isOverflow = True
            if self.output < 255:
                self.isOverflow = True

    def compare(self):
        self.output = self.leftOperand - self.rightOperand

        if self.output == 0:
            self.isZero = True
        else:
            if self.output < 0:
                self.isNegative = True

        if self.isNegative:
            if self.output > 127:
                self.isOverflow = True
            if self.output < -128:
                self.isOverflow = True
        else:
            if self.output < 0:
                self.isOverflow = True
            if self.output < 255:
                self.isOverflow = True

    def pass_through(self):
        self.output = self.leftOperand
        if self.output == 0:
            self.isZero = True
        else:
            if self.output < 0:
                self.isNegative = True


class RAM:
    """A RAM"""

    def __init__(self):
        self.is_write = False
        self.memory = [2, 7, 7, 64, 9, 20, 10, 25, 2, 3, 4, 70, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 4, 70, 0, 2, 2, 4, 70, 0,
                       0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       3, 0,
                       0, 0, 0, 0, 85, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]

    def setmode(self, mode):
        self.is_write = mode

    def read_byte(self, byte_address):
        if self.is_write:
            print("Set to write and cannot read")
        else:
            return self.memory[byte_address]

    def write_byte(self, byte_address, byte_value):
        if self.is_write:
            self.memory[byte_address] = byte_value
        else:
            print("Set to read and cannot write")


if __name__ == '__main__':

    cpu = ControlUnit()
    while not cpu.is_stopped:
        cpu.fetch_instruction()
        cpu.decode_instruction()
        cpu.fetch_operand()
        cpu.execute()
        cpu.to_string()
