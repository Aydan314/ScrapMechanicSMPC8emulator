import random

### Define Globals ###
RAM_SIZE = 16
ROM_SIZE = 64
ALU_AMOUNT = 4
OPERAND_SIZE = 8
VALID_INSTRUCTIONS = [".","BRA","BRM","BRE","BRL","RAV","RAA","STV","STA","LVA","LVB","LRA","LRB","LAA","LAB","URS","ADD","SUB","AND","OR.","XOR","CMP","RNR",".","PRC","PRN","CAL","RET","SIR","INP","CLS","HLT"]
CALL_STACK_DEPTH = 4

PRINTABLE_CHARS = [" ","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","?","!","(",")",".","0","1","2","3","4","5","6","7","8","9"]
SCREEN_LINES = 5
SCREEN_LENGTH = 8

### Define Objects ###
class CallStack:
    def __init__(self):
        self.Reset()

    def PopContents(self):
        for line in range(0,CALL_STACK_DEPTH-1):
            if line != CALL_STACK_DEPTH:
                self.Contents[line] = self.Contents[line + 1]
            else:
                self.contents[line] = 0

    def ShiftContents(self):
        for line in range(CALL_STACK_DEPTH - 1,-1,-1):
            if line > 1:
                self.Contents[line] = self.Contents[line - 1]
            else:
                self.Contents[line] = 0

    def WriteValue(self,Value):
        self.ShiftContents()
        self.Contents[0] = Value

    def ReadValue(self):
        value = self.Contents[0]
        self.PopContents()
        return value

    def Reset(self):
        self.Contents = []

        for i in range(0, CALL_STACK_DEPTH):
            self.Contents.append(0)

class Screen:
    def __init__(self):
        self.Reset()
        
    def ShiftContents(self):
        for line in range(SCREEN_LINES - 1,-1,-1):
            if line > 0:
                self.Contents[line] = self.Contents[line - 1]
            else:
                self.Contents[line] = ""

    def PrintNumber(self,RAMinput):
        self.ShiftContents()
        self.Contents[0] = RAMinput.Contents[8]

    def PrintCharacters(self,RAMinput):
        self.ShiftContents()

        output = ""
        for i in range(0,OPERAND_SIZE):
            output += ConvertToCharacter(RAMinput.Contents[i])

        self.Contents[0] = output

    def PrintUserInput(self, value):
        self.ShiftContents()
        self.Contents[0] = value

    def Output(self):
        for line in range(SCREEN_LINES - 1,-1,-1):
            print(">" ,self.Contents[line])

    def Reset(self):
        self.Contents = []
        
        for i in range(0, SCREEN_LINES):
            self.Contents.append(" ")


class RAM:
    def __init__(self):
        self.Reset()

    def WriteValue(self,Value):
        self.Contents[self.CurrentAddress] = Value

    def ReadValue(self):
        return self.Contents[self.CurrentAddress]

    def SetCurrentAddress(self,Value):
        self.CurrentAddress = Value

    def Reset(self):
        self.Contents = []
        self.CurrentAddress = 0
        
        for i in range(1,RAM_SIZE):
            self.Contents.append(0)

    def ResetScreen(self):
        for i in range(0, 16):
            self.Contents[i] = 0

class ROM:
    def __init__(self,Program):
        self.Reset(Program)

    def ReadOpcode(self,LineNum):
        return self.Contents[LineNum][0]

    def ReadOperand(self,LineNum):
        return self.Contents[LineNum][1]

    def ReadALUselection(self,LineNum):
        return self.Contents[LineNum][2]

    def Reset(self,Program):
        self.Contents = Program

class ProgramCounter:
    def __init__(self):
        self.Reset()

    def Update(self):
        if self.Branch:
            self.CurrentAddress = self.JumpAddress
            self.Branch = False
        else:
            self.CurrentAddress += 1
            if self.CurrentAddress >= ROM_SIZE:
                self.CurrentAddress = 0

    def Jump(self,jumpAddress):
        self.JumpAddress = jumpAddress
        self.Branch = True

    def ReadValue(self):
        return self.CurrentAddress

    def Reset(self):
        self.CurrentAddress = 0
        self.JumpAddress = 0
        self.Branch = False

class ALU:
    def __init__(self):
        self.Reset()

    def SetRegisterA(self,Value):
        self.RegisterA[self.RegisterSet] = Value

    def SetRegisterB(self,Value):
        self.RegisterB[self.RegisterSet] = Value

    def Add(self):
        Value = self.RegisterA[self.RegisterSet] + self.RegisterB[self.RegisterSet]
        Value = CastToBitAmount(Value,OPERAND_SIZE)
        print(self.RegisterA[self.RegisterSet],self.RegisterB[self.RegisterSet])
        self.Accumulator = Value

    def Subtract(self):
        Value = self.RegisterA[self.RegisterSet] - self.RegisterB[self.RegisterSet]
        Value = CastToBitAmount(Value,OPERAND_SIZE)
        self.Accumulator = Value

    def And(self):
        A = ConvertToBinary(self.RegisterA[self.RegisterSet], OPERAND_SIZE)
        B = ConvertToBinary(self.RegisterB[self.RegisterSet], OPERAND_SIZE)
        self.Accumulator = ConvertToDenary(AndValues(A,B))

    def Or(self):
        A = ConvertToBinary(self.RegisterA[self.RegisterSet], OPERAND_SIZE)
        B = ConvertToBinary(self.RegisterB[self.RegisterSet], OPERAND_SIZE)
        self.Accumulator = ConvertToDenary(OrValues(A,B))

    def Xor(self):
        A = ConvertToBinary(self.RegisterA[self.RegisterSet], OPERAND_SIZE)
        B = ConvertToBinary(self.RegisterB[self.RegisterSet], OPERAND_SIZE)
        self.Accumulator = ConvertToDenary(XorValues(A,B))

    def Reset(self):
        self.RegisterA = [0,0,0,0]
        self.RegisterB = [0,0,0,0]
        self.Comparisons = [False,False,False]
        self.Accumulator = 0
        self.RegisterSet = 0

    def UseRegisterSet(self, RegisterSet):
        self.RegisterSet = RegisterSet

    def Compare(self):
        self.Comparisons[0] = self.RegisterA[self.RegisterSet] == self.RegisterB[self.RegisterSet]
        self.Comparisons[1] = self.RegisterA[self.RegisterSet] > self.RegisterB[self.RegisterSet]
        self.Comparisons[2] = self.RegisterA[self.RegisterSet] < self.RegisterB[self.RegisterSet]
        print(self.Comparisons)

    def IsEqual(self):
        return int(self.Comparisons[0])

    def IsMore(self):
        return int(self.Comparisons[1])

    def IsLess(self):
        return int(self.Comparisons[2])

    def ReadValue(self):
        return self.Accumulator

class InputModule:
    def __init__(self):
        self.Reset()

    def WriteValue(self,Value):
        self.Contents = Value
        self.NeedInput = False

    def ReadValue(self):
        return self.Contents

    def PromptInput(self):
        self.NeedInput = True

    def Reset(self):
        self.Contents = 0
        self.NeedInput = False
        
### Define Functions ###

def DisplayProgramOutput(SCREEN,PC):
        print("\n\n\n")
        SCREEN.Output()
        print("[ PC:",PC.ReadValue(),"]")

def ConvertToBinary(Number,BitAmount):
    Value = ""
    Number = int(Number)
    Number = Number % 2**BitAmount

    for i in range(BitAmount - 1, -1, -1):
        if Number - (2**i) >= 0:
            Value = Value + "#"
            Number -= (2**i)
        else:
            Value = Value + "."
    
    return Value

def ConvertToDenary(Number):
    Value = 0
    PlaceValue = len(Number)
    
    for i in range(PlaceValue - 1, -1, -1):
        if Number[PlaceValue - i - 1] == "#":
            Value += (2**i)
        
    return Value

def AndValues(NumberA,NumberB):
    Output=""
    for i in range(0,len(NumberA)):
        if NumberA[i] == "#" and NumberB[i] == "#":
            Output += "#"
        else:
            Output += "."
    return Output

def OrValues(NumberA,NumberB):
    Output=""
    for i in range(0,len(NumberA)):
        if NumberA[i] == "#" or NumberB[i] == "#":
            Output += "#"
        else:
            Output += "."
    return Output

def XorValues(NumberA,NumberB):
    Output = ""
    for i in range(0,len(NumberA)):
        if NumberA[i] != NumberB[i]:
            Output += "#"
        else:
            Output += "."
    return Output

def CastToBitAmount(Number,BitAmount):
    NewNum = ConvertToBinary(Number, OPERAND_SIZE)
    NewNum = NewNum[len(NewNum) - BitAmount : len(NewNum)]
    return ConvertToDenary(NewNum)
        

def GetInstructionID(Instruction):
    ID = 0
    for item in VALID_INSTRUCTIONS:
        if item == Instruction:
            return ID
        ID += 1
    return -1

def GenerateRandom():
    Output = ""
    for i in range(0,OPERAND_SIZE):
        Output += random.choice([".","#"])

    return Output

def ConvertToCharacter(Number):
    if Number >= len(PRINTABLE_CHARS):
        return " "
    return PRINTABLE_CHARS[Number]

def OutputProgram(ProgramOutput):
    for i in range(0,len(ProgramOutput[0])):
        programLine = ""
        for j in range(len(ProgramOutput) - 1,-1,-1):
            programLine += " " + ProgramOutput[j][i]
        
        print(programLine)
        

def AssembleProgram(Program):
    print("Here is your program, paint the # as white onto the appropriate positions on the cartridge\n")
    print("Front Side:\n")
    output = []
    finalOutput = []
    
    LineNum = 0
    for line in Program:
        if LineNum == 32:
            OutputProgram(output)
            output = []
            print("Back Side:\n")

        # Convert Instruction to Binary #
        Opcode = line[0]
        Opcode = ConvertToBinary(GetInstructionID(Opcode),5)

        # Convert Value to Binary #
        Operand = line[1]
        if Operand[0] not in [".","#"]:
            Operand = ConvertToBinary(Operand, OPERAND_SIZE)
        elif Operand == ".":
            Operand = "." * OPERAND_SIZE 

        lineNumString = str(LineNum)
        if LineNum < 10:
            lineNumString = "0" + lineNumString
        
        output.append(lineNumString + " " + Operand + "  " + Opcode)
        finalOutput.append(lineNumString + " " + Operand + "  " + Opcode)
        LineNum += 1
        
    OutputProgram(output)
    return finalOutput

def RunProgram(Program):
    programCounter = ProgramCounter()
    ram = RAM()
    rom = ROM(Program)
    inputModule = InputModule()
    screen = Screen()
    callStack = CallStack()
    
    alu = ALU()

    CurrentOpcode = "."
    CurrentOperand = "."
    CurrentALU = "."
    
    UserInput = ""
    run = True
    while run:
        print("\n" * 20)

        if programCounter.ReadValue() >= len(Program):
            print("!! Program Terminated Program Counter Out Of Range !!")
            run = False
            break

        CurrentOpcode = rom.ReadOpcode(programCounter.ReadValue())
        CurrentOperand = rom.ReadOperand(programCounter.ReadValue())
        
        print(CurrentOpcode,CurrentOperand)
        if CurrentOperand[0] in ["#","."]:
            CurrentOperand = ConvertToDenary(CurrentOperand)

        programCounter, ram, ALUs, inputModule, screen, callStack = ExecuteInstruction(CurrentOpcode,CurrentOperand,programCounter,ram,alu,inputModule,screen,callStack)
        
        DisplayProgramOutput(screen,programCounter)

        if CurrentOpcode == "HLT":
            print("Program Finished!")
            run = False
            break

        programCounter.Update()

        print("Hit ENTER Or type \"Quit\" to leave")

        invalidInput = True
        while invalidInput:
            invalidInput = False
            
            inputPrompt = ">"
            if inputModule.NeedInput:
                inputPrompt = "[ENTER INPUT] >>"
                
            UserInput = input("\n" + inputPrompt)
            
            if UserInput in ["Quit","quit"]:
                print("Exiting Program...")
                run = False
                break

            elif inputModule.NeedInput:
                try:
                    inputModule.WriteValue(CastToBitAmount(int(UserInput),OPERAND_SIZE))
                    screen.PrintUserInput(CastToBitAmount(int(UserInput),OPERAND_SIZE))
                    invalidInput = False
                except:
                    invalidInput = True
                
            
def ExecuteInstruction(Opcode,Operand,programCounter,ram,alu,inputModule,screen,callStack):
    if Opcode == "BRA":
        programCounter.Jump(int(Operand))
    elif Opcode == "BRM":
        if alu.IsMore():
            programCounter.Jump(int(Operand))
    elif Opcode == "BRE":
        if alu.IsEqual():
            programCounter.Jump(int(Operand))
    elif Opcode == "BRL":
        if alu.IsLess():
            programCounter.Jump(int(Operand))
    elif Opcode == "RAV":
        ram.SetCurrentAddress(CastToBitAmount(Operand,5))
    elif Opcode == "RAA":
        NewAddress = alu.ReadValue()
        ram.SetCurrentAddress(CastToBitAmount(NewAddress,5))
    elif Opcode == "STV":
        ram.WriteValue(int(Operand))
    elif Opcode == "STA":
        NewValue = alu.ReadValue()
        ram.WriteValue(CastToBitAmount(NewValue,OPERAND_SIZE))
    elif Opcode == "LVA":
        alu.SetRegisterA(int(Operand))
    elif Opcode == "LVB":
        alu.SetRegisterB(int(Operand))
    elif Opcode == "LRA":
        alu.SetRegisterA(ram.ReadValue())
    elif Opcode == "LRB":
        alu.SetRegisterB(ram.ReadValue())
    elif Opcode == "LAA":
        alu.SetRegisterA(alu.ReadValue())
    elif Opcode == "LAB":
        alu.SetRegisterB(alu.ReadValue())
    elif Opcode == "ADD":
        alu.Add()
    elif Opcode == "SUB":
        alu.Subtract()
    elif Opcode == "AND":
        alu.And()
    elif Opcode == "OR.":
        alu.Or()
    elif Opcode == "XOR":
        alu.Xor()
    elif Opcode == "URS":
        alu.UseRegisterSet(int(Operand))
    elif Opcode == "CMP":
        alu.Compare()
    elif Opcode == "RNR":
        RandNum = GenerateRandom()
        RandNum = AndValues(RandNum,ConvertToBinary(Operand,OPERAND_SIZE))
        ram.WriteValue(ConvertToDenary(RandNum))
    elif Opcode == "PRC":
        screen.PrintCharacters(ram)
    elif Opcode == "PRN":
        screen.PrintNumber(ram)
    elif Opcode == "CAL":
        programCounter.Jump(int(Operand))
        callStack.WriteValue(programCounter.ReadValue() + 1)
       
    elif Opcode == "RET":
        programCounter.Jump(callStack.ReadValue())
        
    elif Opcode == "SIR":
        ram.WriteValue(inputModule.ReadValue())
    elif Opcode == "INP":
        inputModule.PromptInput()
    elif Opcode == "CLS":
        screen.Reset()
    
    return programCounter, ram, alu, inputModule, screen, callStack

### Main Program ###
print("Reading File...")
File = open("INPUT CODE HERE.txt","r")
FileLines = File.readlines()
File.close()

if len(FileLines) > ROM_SIZE:
    print("!! ERROR: Program must be at max 64 lines !!")
else:
    ### Syntax Check ###
    print("Checking Program...")

    Program = []
    EncounteredError = False
    
    for line in FileLines:
        line=line.strip("\n")
        ProgramLine = line.split(" ")

        if len(ProgramLine) == 2:
            if ProgramLine[0] not in VALID_INSTRUCTIONS:
                print("!! ERROR: Invalid Instruction !!")
                print(">> ",line)
                EncounteredError = True
                break
            
            else:
                Program.append(ProgramLine)
        else:
            print("!! ERROR: Each line must contain an opcode and operand !!")
            print(">> ", line)
            print("NOTE: If a line doesn't require a value put a 0 or .")
            EncounteredError = True
            break

    if not EncounteredError:
        ### Main Loop ###
        print("No Errors Encountered")
        UserInput=""
        
        while UserInput not in ["quit","Quit"]:
            print("\n=======================")
            print("Type \"Quit\" to exit\nType \"Output\" to assemble program to machine code\nType \"Run\" to test program")
            print("=======================\n")
            UserInput = input(">")

            if UserInput in ["output","Output"]:
                outputProgram = AssembleProgram(Program)
                inp = input("\nHit ENTER to continue...\nOr \"Step\" to display the lines one by one\n")
                if inp in ["step","Step"]:
                    for line in outputProgram:
                        print("\n\n\n\n\n")
                        OutputProgram([line])
                        input("\nHit ENTER for next line\n")
                print("Your Program is now ready to go!")

            elif UserInput in ["run","Run"]:
                RunProgram(Program)
                input("\nHit ENTER to continue...")

    print("Exiting Program...")


