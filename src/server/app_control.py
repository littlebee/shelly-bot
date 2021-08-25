def app_ctrl():
    app_HOST = ''
    app_PORT = 10123
    app_BUFSIZ = 1024
    app_ADDR = (app_HOST, app_PORT)

    AppSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    AppSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    AppSerSock.bind(app_ADDR)

    def setup():
        move.setup()

    def appCommand(data_input):
        print(f"received data in app_ctrl(). data={data_input}")

    def appconnect():
        global AppCliSock, AppAddr
        AppSerSock.listen(5)
        print('waiting for App connection...')
        AppCliSock, AppAddr = AppSerSock.accept()
        print('...App connected from :', AppAddr)

    appconnect()
    setup()
    # Define a thread for FPV and OpenCV
    app_threading = threading.Thread(target=appconnect)
    # 'True' means it is a front thread,it would close when the mainloop() closes
    app_threading.setDaemon(True)
    app_threading.start()  # Thread starts

    while 1:
        data = ''
        data = str(AppCliSock.recv(app_BUFSIZ).decode())
        if not data:
            continue
        appCommand(data)
        pass


def start_app_control_thread():
    AppConnect_threading = threading.Thread(
        target=app_ctrl)  # Define a thread for FPV and OpenCV
    # 'True' means it is a front thread,it would close when the mainloop() closes
    AppConnect_threading.setDaemon(True)
    AppConnect_threading.start()  # Thread starts
