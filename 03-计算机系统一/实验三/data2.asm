.ORIG x3000
; 初始化地址
LD R0,fen1   ; R0 = x3200
LD R3,fen2   ; R3 = x4000
AND R5,R5,#0
ADD R5,R5,#16 ; 16个数据

; 批量转移 x3200 → x4000
zhuan
BRz pai
LDR R2,R0,#0
STR R2,R3,#0
ADD R0,R0,#1
ADD R3,R3,#1
ADD R5,R5,#-1
BRnzp zhuan

; 选择排序（从大到小）
pai
LD R3,fen2   ; 回到x4000
AND R1,R1,#0
ADD R1,R1,#15 ; 16个数只需15轮外循环

waixun
BRz paiwan
ADD R2,R1,#0 ; 内循环次数 = 当前外循环剩余次数
LDR R4,R3,#0 ; R4 = 当前最大值
ADD R6,R3,#0 ; R6 = 扫描指针
ADD R7,R3,#0 ; R7 = 最大值地址

neixun
ADD R6,R6,#1 ; 下一个数
LDR R5,R6,#0 ; R5 = 待比较数

NOT R0,R4
ADD R0,R0,#1
ADD R0,R5,R0 ; R5 - R4
BRnz next    ; 不大，跳过

; 更新最大值
LDR R4,R6,#0
ADD R7,R6,#0

next
ADD R2,R2,#-1
BRp neixun

; 交换：当前位置R3 ? 最大值位置R7
LDR R0,R3,#0
STR R0,R7,#0
STR R4,R3,#0

ADD R3,R3,#1
ADD R1,R1,#-1
BRnzp waixun

; 统计等级：A≥85，B75-84
paiwan
LD R0,fen2   ; 从x4000开始
AND R4,R4,#0 ; A人数
AND R6,R6,#0 ; B人数
AND R1,R1,#0
ADD R1,R1,#16

tongji
LDR R2,R0,#0

; 判断A
LD R7,fena
ADD R3,R2,R7
BRz isa
BRp isa

; 判断B
LD R7,fenb
ADD R3,R2,R7
BRz isb
BRp isb
BR nexttong

isa
ADD R4,R4,#1
BR nexttong
isb
ADD R6,R6,#1

nexttong
ADD R0,R0,#1
ADD R1,R1,#-1
BRp tongji

; 保存结果
STI R4,cuna
STI R6,cunb

HALT

fen1  .FILL x3200
fen2  .FILL x4000
fena  .FILL #-85
fenb  .FILL #-75
cuna  .FILL x4100
cunb  .FILL x4101
.END