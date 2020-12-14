'''
*flow chart*
최대 용량을 입력하여 Progressbar를 생성(createProcess 함수) ->
Port Name을 입력하여 블루투스 통신 연결(portConnect 함수) ->
블루투스로부터 데이터를 받아옴(thread_run 함수, getData 함수) ->
데이터 값이 10을 넘어서면 수액 투여 실행(mapping 함수, clock 함수, update 함수) ->
수액이 투여되면 남은 시간과 투여 진행 상황 퍼센트로 표시(clock 함수, update 함수)

*process detail*
가변저항값은 0~1024. 이를 직관적으로 해석하기 위해 
1024를 14 등분으로 나누고 mapping을 하여 한 방울이 떨어지는 시간을 계산
이 시간만큼 process(방울 수)라는 변수를 1씩 증가
최대 용량이 1000이라면 1000번 떨어져야 끝남
한 방울이 떨어지는 시간과 최대 용량을 가지고 남은 시간과 진행된 용량을 퍼센트로 표시하도록 함


*in additional*
윈도우를 표시하는 main Thread가 실행되면 다른 행동을 취할 수가 없음
시간을 계산하거나 블루투스를 통해 데이터를 받아오기 위해서는 multi Threading이 필요함
clock, thread_run 함수가 multi Thread를 하는 함수임
'''
#GUI 해더
from tkinter import ttk
from tkinter import *
#블루투스 통신을 위한 serial 해더
import serial
#멀티쓰레딩을 위한 해더
import threading
#Timer Thread를 사용하기 위한 해더
import time

window = Tk() # 윈도우 생성
window.title("Ringer Monitoring System") # 윈도우 타이틀 설정
window.geometry("640x640+100+100") # 윈도우 크기 설정
window.resizable(False, False) # 윈도우 크기를 조절하지 못하도록 설정

P = 0 # Progressbar 변수
max = 10 # Progressbar 사이즈 변수
Percent = 0 # 남은 Percent를 표시하는(라벨) 변수
input_data = 0 # 블루투스 값 변수
bluetooth = 0 # 블루투스 변수

def close_window():
	if bluetooth != 0:
		bluetooth.close()
	window.destroy()
	print("Window closed")
closebutton = Button(window, text='X', command=close_window)
closebutton.grid(row =8, column = 0)

def createProcess(event): # Progressbar와 Percent라벨 생성하는 함수
	# global로 외부에서 생성한 변수를 가져옴(global로 설정 안하면 사용 못함)
	global P
	global max
	global Percent
	max = int(maxnum.get()) #Entry에서 입력한 값을 숫자로 가져옴. Progressbar의 최대값을 의미함
	#Progressbar를 max값에 맞게 생성
	P = ttk.Progressbar(window, orient="horizontal", length=300, maximum=max, mode="determinate")
	P.grid(row = 4, column = 3)#Progressbar의 위치 설정
	Percent = Label(window, text="0%")#Percent를 표시하는 라벨을 생성
	Percent.grid(row = 4, column = 0)#Percent를 표시하는 라벨의 위치 설정
	
def getData():#블루투스에서 데이터를 가져오는 함수
	# global로 외부에서 생성한 변수를 가져옴(global로 설정 안하면 사용 못함)
	global input_data
	global bluetooth
	bluetooth.flushInput()#블루투스 데이터를 flushing함
	input_data=bluetooth.readline()#블루투스에서 데이터를 Line으로 가져옴
	print(input_data.decode())#데이터를 디코딩함(안하면 이상한 데이터로 보임)
	global flag
	if float(input_data.decode()) > 10: #블루투스를 통해 들어온 데이터 값이 10 이상이면 실행(가변저항값이 0~10이면 꺼져있다 판단)
		if flag == 0:
			update()# Progress 실행
			clock()# Timer 실행
			flag = 1 # 위 함수들이 실행되지 못하도록 Flag On
			
target_time = 60*60*12 #임의로 최종 시간을 설정함(가변저항값에 따라 변경될 예정)

def mapping():# 블루투스를 통해 가져온 가변저항값(클램프 위치)을 시간으로 Mapping하는 함수 
	# global로 외부에서 생성한 변수를 가져옴(global로 설정 안하면 사용 못함)
	global input_data
	global target_time
	#가변저항값은 1024가 최대. 이를 14 등분으로 나누기 위해 73.2를 나눠줌
	rating = str(round(float(input_data.decode())/73.2))
	#Mapping Table
	timing = {'0': 12000, 
			'1': 9000,
			'2': 7200,
			'3': 6000,
			'4': 4600,
			'5': 3700,
			'6': 3000,
			'7': 2300,
			'8': 1800,
			'9': 1400,
			'10':1200,
			'11':900,
			'12':700,
			'13':600}.get(rating, 600)
	#Mapping 값을 확인하기 위해 Print함
	print(timing)		
	#Mapping된 시간과 최대 용량을 가지고 용량이 0이 되는 최대 시간을 계산
	target_time =  float(max * 20) * (float(timing) / 1000.0)
	#print(float(max * 20))
	#print((float(timing) / 1000.0))
	return timing
	
#현재 시간
current_time = 0

def clock():#수액의 용량이 0이 되는 남은 시간을 계산
	# global로 외부에서 생성한 변수를 가져옴(global로 설정 안하면 사용 못함)
	global current_time
	global target_time
	#이 함수가 다시 실행되면 현재 시간에 1을 추가
	current_time += 1
	#초를 분과 초로 나눠줌(나머지와 몫을 이용) 
	minute , second = divmod(int(target_time) - current_time, 60)
	#분을 시와 분으로 나눠줌(나머지와 몫을 이용) 
	hour, minute = divmod(minute, 60)
	#남은 시간을 나타내는 라벨에 표시
	L['text'] = "{0} : {1} : {2}".format(int(hour), int(minute), int(second))
	#이것은 멀티쓰레드를 위함으로 1초에 한번씩 이 함수가 실행되도록 함
	#멀티쓰레딩이기 때문에 다른 쓰레드에 영향을 주지 않음(병렬처리로 간주해도 됨)
	threading.Timer(1, clock).start()
	
	
	
	
def portConnect(event):#Port Name에 해당하는 Port로 연결을 시도
	# global로 외부에서 생성한 변수를 가져옴(global로 설정 안하면 사용 못함)
	global bluetooth
	#Entry에서 입력한 Port name으로 연결 시도. bitrate는 9600
	bluetooth=serial.Serial(portnname.get(), 9600)
	print("Connected")
	#thread_run이라는 함수를 실행
	thread_run()

def thread_run():#주기적으로 블루투스에서 보낸 데이터를 받기 위한 쓰레드 함수
	getData()#데이터를 받아오는 함수
	#0.5초마다 이 함수가 멀티쓰레드로 실행됨
	threading.Timer(0.5, thread_run).start()

#용량을 입력하는 부분을 알려주기 위한 라벨
label1 = Label(window, text="용량")
label1.grid(row = 0, column = 0)
#최대 용량을 설정하는 Entry
maxnum=Entry(window)
maxnum.bind("<Return>", createProcess)
maxnum.grid(row = 0, column = 1)

#Port name을 입력하는 부분을 알려주기 위한 라벨
label2 = Label(window, text="포트")
label2.grid(row = 1, column = 0)
#Port name을 설정하는 Entry
portnname=Entry(window)
portnname.bind("<Return>", portConnect)
portnname.grid(row = 1, column = 1)


flag = 0
process = 0

		
def update():#주기적으로 Progress를 업데이트 하기 위한 함수
	# global로 외부에서 생성한 변수를 가져옴(global로 설정 안하면 사용 못함)
	global process
	global flag
	global Percent
	global current_time
	#이 함수가 실행되면 Process가 1씩 증가
	process += 1
	#Progressbar에 Process 값을 입력(최대 용량이 100이라면 Process가 100이 될때 Progressbar가 꽉 채워짐)
	P['value'] = process
	#현재 용량이 얼만큼 줄어들었는지 퍼센트로 표시하는 부분
	Percent['text'] = "{0}%".format(int((process/float(max)) * 100))
	#만약 최대 용량만큼 수액 투여가 진행됐다면 밑을 실행
	if P['value'] >= P['maximum']:
		flag = 0#다시 flag를 off 시킴
		process = 0 #process 초기화
		current_time = 0#현재 시간 초기화
		return  # This will end the after() loop
	#이 함수를 mapping된 시간만큼 다시 실행
	window.after( mapping(), update )

#남은 용량 표시하는 라벨
L = Label(window, text="Remain")
L.grid(row = 5, column = 0)



#window를 반복함(윈도우를 끄지 않을 때까지 실행)
window.mainloop()



