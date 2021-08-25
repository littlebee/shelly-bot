
def get_cpu_tempfunc():
    """ Return CPU temperature """
    result = 0
    mypath = "/sys/class/thermal/thermal_zone0/temp"
    with open(mypath, 'r') as mytmpfile:
        for line in mytmpfile:
            result = line

    result = float(result)/1000
    result = round(result, 1)
    return str(result)


def get_gpu_tempfunc():
    """ Return GPU temperature as a character string"""
    res = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    return res.replace("temp=", "")


def get_cpu_use():
    """ Return CPU usage using psutil"""
    cpu_cent = psutil.cpu_percent()
    return str(cpu_cent)


def get_ram_info():
    """ Return RAM usage using psutil """
    ram_cent = psutil.virtual_memory()[2]
    return str(ram_cent)


def get_swap_info():
    """ Return swap memory  usage using psutil """
    swap_cent = psutil.swap_memory()[3]
    return str(swap_cent)


def info_get():
    global cpu_t, cpu_u, gpu_t, ram_info
    while 1:
        cpu_t = get_cpu_tempfunc()
        cpu_u = get_cpu_use()
        ram_info = get_ram_info()
        time.sleep(3)


def info_send_client():
    SERVER_IP = addr[0]
    SERVER_PORT = 2256  # Define port serial
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)
    # Set connection value for socket
    Info_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Info_Socket.connect(SERVER_ADDR)
    print(SERVER_ADDR)
    while 1:
        try:
            Info_Socket.send(
                (get_cpu_tempfunc()+' '+get_cpu_use()+' '+get_ram_info()).encode())
            time.sleep(1)
        except:
            pass


def start_system_info_thread():
    info_threading = threading.Thread(target=info_send_client)
    # 'True' means it is a front thread,it would close when the mainloop() closes
    info_threading.setDaemon(True)
    info_threading.start()  # Thread starts
