from Tkinter import *
from gps import *
import time
import Adafruit_ADS1x15
import math
from xlutils.copy import copy
from xlrd import *
import xlwt
import RPi.GPIO as GPIO


#Se definen los valores de lectura ADC
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
adc1 = Adafruit_ADS1x15.ADS1115(address=0x48)
adc2 = Adafruit_ADS1x15.ADS1115(address=0x49)
GAIN = 1
GAIN2 = 2/3

#Se inicializa gps
##global gpsd
##gpsd=gps(mode = WATCH_ENABLE)
##running=True
##current_value=None
##gpsd.next()
##gpsd.next()
##gpsd.next()
##gpsd.next()



#Se definela variable pi = 3,141...#
global pi
pi = math.pi

global color
color = 'green'
global paso#Senal de control mv Rshunt



#Funcion para iniciar la aplicacion

def App():
        global ventana_inicio
        ventana_inicio= Tk()
        ventana_inicio.geometry('430x220')
        #ventana_principal.title("Medidor de CEa y Humedad de suelo")
        ventana_inicio.resizable(0,0)
        #cargando=Canvas(ventana_inicio,width=400,height=500)
        #cargando.create_image(250,250,image=imagen_inicio)
        cargando = Label(ventana_inicio, text="Cargando Programa ...")
        cargando.pack()
        ventana_inicio.after(5000,inicio_programa)
        

#Funcion para mostrar informacion y menu

def inicio_programa():
        global iniciar1,cancelar1
        global ventana_principal
        ventana_inicio.destroy()
        ventana_principal = Tk()
        ventana_principal.geometry('430x220')
        ventana_principal.title("Medidor de CEa y Humedad de suelo")
        ventana_principal.resizable(0,0)

        Menubar=Menu(ventana_principal)
        
        menu_Opciones=Menu(Menubar,tearoff=0)
        menu_Opciones.add_command(label="Acerca de",font="Helvetica 10")
        menu_Opciones.add_command(label="Salir",font="Helvetica 10",command=quit)
        Menubar.add_cascade(label="Opciones",font="Helvetica 10",menu=menu_Opciones)

        menu_Ayuda=Menu(Menubar,tearoff=0)
        menu_Ayuda.add_command(label="Sensores",font="Helvetica 10")
        menu_Ayuda.add_command(label="Como utilizar",font="Helvetica 10")
        Menubar.add_cascade(label="Ayuda",font="Helvetica 10",menu=menu_Ayuda)      

        ventana_principal.config(menu=Menubar)

        texto_bienvenida = Label(ventana_principal,text="Trabajo final de M. Sc en Automatizacion industrial. \n Autor : Jhonatan Paolo Tovar Soto \n Director : Jesus Hernan Camacho Tamayo. M. Sc, Ph. D. \n Codirector : Leonardo Enrique Bermeo Clavijo. M. Sc, Ph. D.",font="Helvetica")
        
        iniciar1=Button(ventana_principal,text="Iniciar",font="Helvetica 12",command=iniciar)
        #cancelar1=Button(ventana_principal,text="Cancelar",command=quit)
        texto_bienvenida.pack(side=TOP,fill=BOTH, expand=True)
        iniciar1.pack()
        #cancelar1.pack()


#Funcion para escojer que tarea realizar
def iniciar():
        global ventana_sec_1
        ventana_sec_1 = Toplevel(ventana_principal)
        ocultar(ventana_principal)
        ventana_sec_1.geometry('400x170')
        ventana_sec_1.title("Menu principal")
        Texto1= Label(ventana_sec_1,text="Cual medicion desea obtener?",font="Helvetica 12")
        Texto1.pack()
        global item
        item = IntVar()
        Boton1= Radiobutton(ventana_sec_1, text = "Conductividad electrica, CEa.",font="Helvetica 12", variable = item, value =1)
        Boton1.pack(anchor=W)
        Boton2=Radiobutton(ventana_sec_1, text = "Nivel de humedad.",font="Helvetica 12", variable = item, value =2)
        Boton2.pack(anchor=W)
        Boton3=Radiobutton(ventana_sec_1, text = "Conductividad electrica, CEa y nivel de humedad",font="Helvetica 12", variable = item, value =3)
        Boton3.pack(anchor=W)

        Continuar1=Button(ventana_sec_1, text="Continuar",font="Helvetica 12",command=lambda:elegir(item.get()))
        Continuar1.pack()
        Continuar1.place(x=60,y=100,width=100)
        Atras1=Button(ventana_sec_1, text="Atras",font="Helvetica 12",command=lambda:destruir(ventana_principal,ventana_sec_1))
        Atras1.pack()
        Atras1.place(x=240,y=100,width=100)
        

#Funcion que elije que operacion realizar
def elegir(elec):
        if elec==1:
                CEa()
                print("1")
        elif elec==2:
                Humedad()
                print("2")
        else:
                CEa_Humedad()
                print("3")
        

#Funciones para crear ventana de visualizacion de datos

def CEa():
        global ventana_CEa,n
        
        n=0
        paso=0
        ventana_CEa = Toplevel(ventana_principal)
        ocultar(ventana_sec_1)
        ventana_CEa.geometry('500x300')
        ventana_CEa.title('Obtencion de CEa')
        global long_electrodo,R_ap,P_ap,CE_ap,longitud,latitud,milvolt,mensaje
        long_electrodo = DoubleVar()
        R_ap = DoubleVar()
        P_ap = DoubleVar()
        CE_ap = DoubleVar()
        longitud = DoubleVar()
        latitud = DoubleVar()
        milvolt = DoubleVar()
        mensaje = StringVar()
        
        Pregunta=Label(ventana_CEa, text = "Elija la longitud de electrodo:",font="Helvetica 12")
        Pregunta.place(x=20,y=20)

        Boton1=Radiobutton(ventana_CEa, text = "10 cm",font="Helvetica 12", variable = long_electrodo, value =0.1)
        Boton1.place(x=50,y=50,width=100)
        #Radiobutton(ventana_CEa, text = "15 cm", variable = long_electrodo, value =0.15).pack()
        Boton2=Radiobutton(ventana_CEa, text = "20 cm",font="Helvetica 12", variable = long_electrodo, value =0.2)
        Boton2.place(x=50,y=80,width=100)
        Boton3=Radiobutton(ventana_CEa, text = "25 cm",font="Helvetica 12", variable = long_electrodo, value =0.25)
        Boton3.place(x=50,y=110,width=100)

        
        #Label(ventana_CEa,text="Resistencia aparente:").pack()
        #Label(ventana_CEa,textvariable=R_ap).pack()
        #Label(ventana_CEa,text = "Resistividad aparente:").pack()
        #Label(ventana_CEa,textvariable=P_ap).pack()
        Texto1=Label(ventana_CEa,text = "Conductividad aparente:",font="Helvetica 12")
        Texto1.place(x=300,y=20)
        CEa=Label(ventana_CEa,textvariable=CE_ap,font="Helvetica 12")
        CEa.place(x=370,y=50)
        Mensaje = Label(ventana_CEa,textvariable=mensaje,font="Helvetica 12")
        Mensaje.place(x=370,y=70)
        Texto2=Label(ventana_CEa,text = "Longitud:",font="Helvetica 12")
        Texto2.place(x=300,y=110)
        Longitud1=Label(ventana_CEa,textvariable=longitud,font="Helvetica 12")
        Longitud1.place(x=370,y=110)
        Texto3=Label(ventana_CEa,text = "Latitud:",font="Helvetica 12")
        Texto3.place(x=300,y=140)
        Latitud1=Label(ventana_CEa,textvariable=latitud,font="Helvetica 12")
        Latitud1.place(x=370,y=140)
        #Label(ventana_CEa,text = "Mv:").pack()
        #Label(ventana_CEa,textvariable=milvolt).pack()
        Boton1=Button(ventana_CEa,text="Tomar datos",font="Helvetica 12",command=lambda:calculo_CEa(long_electrodo.get()))
        Boton1.place(x=330,y=180)
        Boton2=Button(ventana_CEa,text = "Volver al menu principal",font="Helvetica 12", command=lambda:destruir2(ventana_sec_1,ventana_CEa))
        Boton2.place(x=40,y=205)
        Boton3=Button(ventana_CEa,text = "Obtener grafica",font="Helvetica 12", command=graficar())
        Boton3.place(x=320,y=230)

def Humedad():
        global ventana_Humedad
        ventana_Humedad = Toplevel(ventana_principal)
        ocultar(ventana_sec_1)
        ventana_Humedad.geometry('500x300')
        ventana_Humedad.title('Obtencion de Humedad')
        global longitud,latitud,Hum,Ke,longitud_electrodoH
        long_electrodoH = DoubleVar()
        Ke = DoubleVar()
        Hum = DoubleVar()
        longitud = DoubleVar()
        latitud = DoubleVar()
        
        Pregunta=Label(ventana_Humedad, text = "Elija la longitud de electrodo:",font="Helvetica 12")
        Pregunta.place(x=20,y=20)

        Boton1=Radiobutton(ventana_Humedad, text = "13 cm",font="Helvetica 12", variable = long_electrodoH, value =0.1)
        Boton1.place(x=50,y=50,width=100)
        #Radiobutton(ventana_Humedad, text = "15 cm", variable = long_electrodoH, value =0.15).pack()
        Boton2=Radiobutton(ventana_Humedad, text = "20 cm",font="Helvetica 12", variable = long_electrodoH, value =0.2)
        Boton2.place(x=50,y=80,width=100)
        #Radiobutton(ventana_Humedad, text = "25 cm", variable = long_electrodoH, value =0.25).pack()

        Texto1=Label(ventana_Humedad,text = "Contenido de Humedad:",font="Helvetica 12")
        Texto1.place(x=300,y=20)
        Humedad=Label(ventana_Humedad,textvariable=Hum,font="Helvetica 12")
        Humedad.place(x=370,y=50)
        Texto2=Label(ventana_Humedad,text = "Longitud:",font="Helvetica 12",)
        Texto2.place(x=300,y=110)
        Longitud2=Label(ventana_Humedad,textvariable=longitud,font="Helvetica 12")
        Longitud2.place(x=370,y=110)
        Texto3=Label(ventana_Humedad,text = "Latitud:",font="Helvetica 12",)
        Texto3.place(x=300,y=140)
        Latitud2=Label(ventana_Humedad,textvariable=latitud,font="Helvetica 12")
        Latitud2.place(x=370,y=140)

        Boton1=Button(ventana_Humedad,text="Tomar datos",font="Helvetica 12",command=lambda:calculo_Hum(long_electrodoH.get()))
        Boton1.place(x=330,y=180)
        Boton2=Button(ventana_Humedad,text = "Volver al menu principal",font="Helvetica 12", command=lambda:destruir(ventana_sec_1,ventana_Humedad))
        Boton2.place(x=40,y=205)
        Boton3=Button(ventana_Humedad,text = "Obtener grafica",font="Helvetica 12", command=graficar())
        Boton3.place(x=320,y=230)
def CEa_Humedad():
        global ventana_CEa_humedad,n
        
        n=0
        paso=0
        ventana_CEa_humedad = Toplevel(ventana_principal)
        ocultar(ventana_sec_1)
        ventana_CEa_humedad.geometry('500x300')
        ventana_CEa_humedad.title('Obtencion de CEa y Humedad')
        global long_electrodo,R_ap,P_ap,CE_ap,longitud,latitud,milvolt,mensaje
        long_electrodo = DoubleVar()
        R_ap = DoubleVar()
        P_ap = DoubleVar()
        CE_ap = DoubleVar()
        CE_ap.set(0.0195)
        longitud = DoubleVar()
        longitud.set(-74.08434)
        latitud = DoubleVar()
        latitud.set(4.638959)
        milvolt = DoubleVar()
        mensaje = StringVar()
        mensaje.set("Medicion correcta")
        global Hum,Ke,longitud_electrodoH
        long_electrodoH = DoubleVar()
        Ke = DoubleVar()
        Hum = DoubleVar()
        Hum.set(49.2)
        
        Pregunta=Label(ventana_CEa_humedad, text = "Elija la longitud de electrodo de CEa:",font="Helvetica 12")
        Pregunta.place(x=20,y=20)

        Boton1=Radiobutton(ventana_CEa_humedad, text = "10 cm",font="Helvetica 12", variable = long_electrodo, value =0.1)
        Boton1.place(x=50,y=50,width=100)
        #Radiobutton(ventana_CEa, text = "15 cm", variable = long_electrodo, value =0.15).pack()
        Boton2=Radiobutton(ventana_CEa_humedad, text = "20 cm",font="Helvetica 12", variable = long_electrodo, value =0.2)
        Boton2.place(x=50,y=80,width=100)
        Boton3=Radiobutton(ventana_CEa_humedad, text = "25 cm",font="Helvetica 12", variable = long_electrodo, value =0.25)
        Boton3.place(x=50,y=110,width=100)

        Pregunta=Label(ventana_CEa_humedad, text = "Elija la longitud de electrodo:",font="Helvetica 12")
        Pregunta.place(x=20,y=140)

        Boton4=Radiobutton(ventana_CEa_humedad, text = "13 cm",font="Helvetica 12", variable = long_electrodoH, value =0.1)
        Boton4.place(x=50,y=170,width=100)
        Boton5=Radiobutton(ventana_CEa_humedad,text = "20 cm",font="Helvetica 12", variable = long_electrodoH, value =0.2)
        Boton5.place(x=50,y=200,width=100)


        Texto1=Label(ventana_CEa_humedad,text = "Conductividad aparente:",font="Helvetica 12")
        Texto1.place(x=300,y=20)
        CEa=Label(ventana_CEa_humedad,textvariable=CE_ap,font="Helvetica 12")
        CEa.place(x=370,y=50)
        Texto2=Label(ventana_CEa_humedad,text = "Humedad:",font="Helvetica 12")
        Texto2.place(x=300,y=70)
        HUM=Label(ventana_CEa_humedad,textvariable=Hum,font="Helvetica 12")
        HUM.place(x=370,y=100)
        Mensaje = Label(ventana_CEa_humedad,textvariable=mensaje,font="Helvetica 12")
        Mensaje.place(x=370,y=120)
        Texto2=Label(ventana_CEa_humedad,text = "Longitud:",font="Helvetica 12")
        Texto2.place(x=300,y=140)
        Longitud1=Label(ventana_CEa_humedad,textvariable=longitud,font="Helvetica 12")
        Longitud1.place(x=370,y=140)
        Texto3=Label(ventana_CEa_humedad,text = "Latitud:",font="Helvetica 12")
        Texto3.place(x=300,y=170)
        Latitud1=Label(ventana_CEa_humedad,textvariable=latitud,font="Helvetica 12")
        Latitud1.place(x=370,y=170)
        Boton1=Button(ventana_CEa_humedad,text="Tomar datos",font="Helvetica 12",command=lambda:calculo_CEa(long_electrodo.get()))
        Boton1.place(x=330,y=200)
        Boton2=Button(ventana_CEa_humedad,text = "Volver al menu principal",font="Helvetica 12", command=lambda:destruir2(ventana_sec_1,ventana_CEa))
        Boton2.place(x=40,y=230)
        Boton3=Button(ventana_CEa_humedad,text = "Obtener grafica",font="Helvetica 12", command=graficar())
        Boton3.place(x=320,y=240)
#Funciones para tomar datos,promediar,realizar los calculos y guardar archivos de excel

def calculo_CEa(long_valor):
        global n,paso,escribir,p,m
        while n==0:
            archivo = xlwt.Workbook()
            libro1 = archivo.add_sheet("Datos CEa",cell_overwrite_ok=True)
            fuente = xlwt.easyxf('font: name Calibri,colour blue, bold on')
            libro1.write(n,1,"Resistencia",fuente)
            libro1.write(n,2,"Resistividad",fuente)
            libro1.write(n,3,"Conductividad",fuente)
            libro1.write(n,4,"Latitud",fuente)
            libro1.write(n,5,"Longitud",fuente)
            archivo.save("Datos.xls")
            n=1
            m=1
            p=1
            paso=0

        #Se selecciona automaticamente la separacion entre electrodos
        if long_valor==0.1:
                sep_electrodo=0.02
        elif long_valor==0.15:
                sep_electrodo=0.02
        elif long_valor==0.2:
                sep_electrodo=0.03
        else:
                sep_electrodo=0.04
                
        

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23,GPIO.OUT)#Senal Rshunt, GPIO2
        GPIO.setup(18,GPIO.OUT)#Senal frecuencias, GPIO1
        
        global val_ant1,val_ant2,val_ant3,val_ant4
        global val_ant11,val_ant22,val_ant33,val_ant44
        global valor_lec1,valor_lec2,valor_lec3
        global valor1,valor2,valor3
        
        val_ant11=0
        val_ant22=0
        val_ant33=0
        val_ant44=0
        
        #Se define las listas de iteracion para frecuencias y promedios
        lista1=range(10)#Frecuencias de medicion
        lista2=range(5) #Iteraciones de toma de muestras

        #Se realiza iteracion para mandar pulsos de frecuencia con amplitud 10 voltios
        for j in lista1:
                tiempo=float(0.1*j)#Tiempo de espera de las frecuencias de medicion
                val_ant1=0
                val_ant2=0
                val_ant3=0
                val_ant4=0
                #Se realiza iteracion para promediar mediciones del suelo
                for i in lista2:
                        GPIO.output(18,True)
                        time.sleep(tiempo)#Espera de pulso en alto

                        #An0 = Voltaje salida monitor corriente
                        #An1 = Voltaje diferencial suelo +
                        #An2 = Voltaje diferencial suelo -
                        
                        valor_lec1 = adc1.read_adc(0,GAIN2,data_rate=32)*float(6.144)/32767
                        valor_lec2 = adc1.read_adc(1,GAIN2,data_rate=32)*float(6.144)/32767
                        valor_lec3 = adc1.read_adc(2,GAIN2,data_rate=32)*float(6.144)/32767
                        
                        valor1 = 2*valor_lec1#Valor real voltaje salida monitor de corriente
                        valor1 = valor1 + val_ant1#Sumatoria de mediciones 
                        val_ant1 = valor1#Asigna recursivamente valores leidos
                        
                        valor2 = valor_lec2 + val_ant2#Sumatoria de mediciones 
                        val_ant2=valor2#Asigna recursivamente valores leidos

                        valor3 = valor_lec3 + val_ant3#Sumatoria de mediciones 
                        val_ant3=valor3#Asigna recursivamente valores leidos

                        GPIO.output(18,False)
                        time.sleep(tiempo)#Espera de pulso en bajo
                        #Finaliza el primer for.

                valor1 = valor1/len(lista2)#Valor 1 promediado para una medida de frecuencia
                valor1 = valor1 + val_ant11#Sumatoria de mediciones
                val_ant11 = valor1#Asigna recursivamente valores leidos

                valor2 = valor2/len(lista2)#Valor 2 promediado para una medida de frecuencia
                valor2 = valor2 + val_ant22#Sumatoria de mediciones
                val_ant22 = valor2#Asigna recursivamente valores leidos

                valor3 = valor3/len(lista2)#Valor 3 promediado para una medida de frecuencia
                valor3 = valor3 + val_ant33#Sumatoria de mediciones
                val_ant33 = valor3#Asigna recursivamente valores leidos

                #FiNaliza el segundo for
                
        valor1 = valor1/len(lista1)#Valor final voltaje monitor de corriente
        valor2 = valor2/len(lista1)#Valor final voltaje + suelo
        valor3 = valor3/len(lista1)#Valor final voltaje - suelo
        valor2 = 3*(valor2 - valor3)#Valor final voltaje diferencial suelo
        valor3 = valor1/50#Valor voltaje Rshunt para monitoreo

        #Condicional para determinar Rshunt
        if paso==0:
                if valor3>=0.095:
                        mensaje.set("Medicion incorrecta")
                        paso=1
                        GPIO.output(23,True)
                        rshunt=5.6
                        escribir = 0
                else:
                        mensaje.set("Medicion correcta")
                        rshunt=118
                        escribir = 1
        else:
                if valor3 <=0.005:
                        mensaje.set("Medicion incorrecta")
                        paso=0
                        GPIO.output(23,False)
                        rshunt=118
                        escribir = 0
                else:
                        mensaje.set("Medicion correcta")
                        rshunt=5.6
                        escribir = 1

        
        corriente = valor3/rshunt #Calculo de la corriente del suelo
        resistencia = valor2/corriente #Calculo de la resistencia en el suelo

        #Calculo de resistividad
        A = 4*pi*sep_electrodo*resistencia #Numerador de la resistividad
        B = (2*sep_electrodo)/((sep_electrodo**2) + (4*long_valor**2))**0.5
        C = (sep_electrodo)/((sep_electrodo**2) + (long_valor**2))**0.5
        D = 1 + B -C #Denominador de la resistividad
        
        resistividad = A/D #Resistividad aparente del suelo
        conductividad = 1/resistividad #Conductividad aparente del suelo
        R_ap.set(resistencia)
        P_ap.set(resistividad)
        CE_ap.set(conductividad)

        global gpsd
        gpsd=gps(mode = WATCH_ENABLE)
        running=True
        current_value=None
        gpsd.next()
        gpsd.next()
        gpsd.next()
        gpsd.next()
        gpsd.next()
        gpsd.next()
        gpsd.next()
        gpsd.next()
        valor_latitud=gpsd.fix.latitude
        valor_longitud=gpsd.fix.longitude
        latitud.set(valor_latitud)
        longitud.set(valor_longitud)
        milvolt.set(valor3)
        running=False


        if escribir==0:
                p = p
        else:
                
                for m in range(5):
                    documento = "Datos.xls"
                    nuevo = open_workbook(documento,formatting_info=True)
                    copia = copy(nuevo)
                    hoja_nueva=copia.get_sheet(0)
                    if m==1:
                        hoja_nueva.write(p,1,resistencia)
                    elif m==2:
                        hoja_nueva.write(p,2,resistividad)
                    elif m==3:
                        hoja_nueva.write(p,3,conductividad)
                    elif m==4:
                        hoja_nueva.write(p,4,valor_latitud)
                    else:
                        hoja_nueva.write(p,5,valor_longitud)
                    copia.save(documento)
                p=p+1

        valor1 = 0
        valor2 = 0
        valor3 = 0
        

def calculo_Hum(long_valor):        
        Ke.set(long_valor)
        Hum.set(3)
        valor_latitud=gpsd.fix.latitude
        valor_longitud=gpsd.fix.longitude
        latitud.set(valor_latitud)
        longitud.set(valor_longitud)
        gpsd.next()
        return



#Funcion pra graficarlos datos
def graficar():
        return 
#Funcion para mostrar ventana
def mostrar(v1):
        v1.deiconify()

#Funcion para ocultar ventana
def ocultar(v2):
        v2.iconify()

#Funcion para destruir ventanay mostrar la anterior
def destruir(v3,v4):
        v3.deiconify()
        v4.destroy()

def destruir2(v3,v4):
        v3.deiconify()
        v4.destroy()
        GPIO.output(23,False)
        GPIO.output(18,False)
        GPIO.cleanup()
        n=0
        paso=0

#Funcion para limpiar los puertos GPIO
def limpiar_GPIO():
        GPIO.cleanup()
#Se genera las ventanas

#Ventana de inicio//ventana_inicio
##ventana_inicio = Tk()
##imagen_inicio = PhotoImage(file=imagen)
##cargando=Canvas(ventana_inicio,width=400,height=500)
##cargando.create_image(250,250,image=imagen_inicio)
##cargando = Label(ventana_inicio,image=imagen_inicio)
##cargando.pack()
##ventana_inicio.after(5000,ventana_inicio.destroy)

#Ventana principal//ventana_principal

App()

#Ventana secundaria // ventana_sec1

#Ventana secundaria// ventana_sec2

#Ventana secundaria// ventana_sec3
mainloop()

    
