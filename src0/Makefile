CC		:=	gcc 
CC_FLAGS	:=	-m32
ASM		:=	nasm
ASM_FLAGS	:=	-f elf 


all: myexe.out
	
myexe.out:	myasm.s main.c
	$(ASM) $(ASM_FLAGS)  myasm.s -o myasm.o

	$(CC) $(CC_FLAGS) main.c myasm.o -o myexe.out


