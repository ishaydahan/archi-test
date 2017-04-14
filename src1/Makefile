CC		:=	gcc -m32
CC_FLAGS	:=	-w -Wall -g
ASM		:=	nasm
ASM_FLAGS	:=	-f elf -g
LINK		:=	ld

SRC_DIR		:=	.
OBJ_DIR		:=	.
LIST_DIR	:=	.
BIN_DIR		:=	.

all: task1 task2

task1:	$(OBJ_DIR)/main1.o $(OBJ_DIR)/task1.o
	$(CC) -o $(BIN_DIR)/task1.bin $(OBJ_DIR)/main1.o $(OBJ_DIR)/task1.o

task2:	$(OBJ_DIR)/main2.o $(OBJ_DIR)/task2.o
	$(CC) -o $(BIN_DIR)/task2.bin $(OBJ_DIR)/main2.o $(OBJ_DIR)/task2.o

# .c/.s compile rules
$(OBJ_DIR)/%.o : $(SRC_DIR)/%.c
	$(CC) -c $(CC_FLAGS) $< -o $@

$(OBJ_DIR)/%.o : $(SRC_DIR)/%.s
	$(ASM) $(ASM_FLAGS) $< -o $@ -l $(subst .o,.lst,$(subst $(OBJ_DIR),$(LIST_DIR),$@))

clean:
	rm $(BIN_DIR)/*.bin $(OBJ_DIR)/*.o $(LIST_DIR)/*.lst