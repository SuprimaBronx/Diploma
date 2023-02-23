
import win32con
from ...errors import Error
import sys
import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)


# The types of events we want to listen for, and the names we'll use for
# them in the log output. Pick from
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd318066(v=vs.85).aspx
eventTypes = {
    win32con.EVENT_SYSTEM_FOREGROUND: "Foreground",
    # win32con.EVENT_OBJECT_FOCUS: "Focus",
    # win32con.EVENT_OBJECT_SHOW: "Show",
    # win32con.EVENT_SYSTEM_DIALOGSTART: "Dialog",
    # win32con.EVENT_SYSTEM_CAPTURESTART: "Capture",
    # win32con.EVENT_SYSTEM_MINIMIZEEND: "UnMinimize"
}

# limited information would be sufficient, but our platform doesn't have it.
processFlag = getattr(win32con, 'PROCESS_QUERY_LIMITED_INFORMATION', win32con.PROCESS_QUERY_INFORMATION)
threadFlag = getattr(win32con, 'THREAD_QUERY_LIMITED_INFORMATION', win32con.THREAD_QUERY_INFORMATION)


# store last event time for displaying time between events
lastTime = 0
WM_QUIT = 0x0012



class LLISTEN:
    def __init__(self):
        self.stop_flag = 0
        self.collection = []
        error = Error()

    def set_stop_flag(self,tid):
        self.stop_flag = 1
        self.PostThreadMessage(tid)

    # def log(self,msg):
    #     print(msg)
    #
    #
    def logError(self,msg):
        self.error.win_track(msg, file=sys.stderr)


    def getProcessID(self,dwEventThread, hwnd):
        # It's possible to have a window we can get a PID out of when the thread
        # isn't accessible, but it's also possible to get called with no window,
        # so we have two approaches.

        hThread = kernel32.OpenThread(threadFlag, 0, dwEventThread)

        if hThread:
            try:
                processID = kernel32.GetProcessIdOfThread(hThread)
                if not processID:
                    self.logError("Couldn't get process for thread %s: %s" % (hThread, ctypes.WinError()))
            finally:
                kernel32.CloseHandle(hThread)

        else:
            errors = ["No thread handle for %s: %s" % (dwEventThread, ctypes.WinError(),)]

            if hwnd:
                processID = ctypes.wintypes.DWORD()
                threadID = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(processID))

                if threadID != dwEventThread:
                    self.logError("Window thread != event thread? %s != %s" % (threadID, dwEventThread))

                if processID:
                    processID = processID.value
                else:
                    errors.append("GetWindowThreadProcessID(%s) didn't work either: %s" % (hwnd, ctypes.WinError()))
                    processID = None
            else:
                processID = None

            if not processID:
                for err in errors:
                    self.logError(err)

        return processID


    def getProcessFilename(self,processID):
        hProcess = kernel32.OpenProcess(processFlag, 0, processID)
        if not hProcess:
            self.logError("OpenProcess(%s) failed: %s" % (processID, ctypes.WinError()))
            return None

        try:
            filenameBufferSize = ctypes.wintypes.DWORD(4096)
            filename = ctypes.create_unicode_buffer(filenameBufferSize.value)
            kernel32.QueryFullProcessImageNameW(hProcess, 0, ctypes.byref(filename),
                                                ctypes.byref(filenameBufferSize))

            return filename.value
        finally:
            kernel32.CloseHandle(hProcess)


    def callback(self,hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        global lastTime
        length = user32.GetWindowTextLengthW(hwnd)
        title = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, title, length + 1)

        processID = self.getProcessID(dwEventThread, hwnd)
        if self.stop_flag == 1:
            self.PostThreadMessage(processID)

        shortName = '?'
        if processID:
            filename = self.getProcessFilename(processID)
            if filename:
                shortName = '\\'.join(filename.rsplit('\\', 2)[-2:])

        if hwnd:
            hwnd = hex(hwnd)
        elif idObject == win32con.OBJID_CURSOR:
            hwnd = '<Cursor>'


        # self.log("%s:%04.2f\t%-10s\tW:%-8s\tP:%-8d\tT:%-8d\t%s\t%s" % (
        #     dwmsEventTime, float(dwmsEventTime - lastTime)/1000, eventTypes.get(event, hex(event)),
        #     hwnd, processID or -1, dwEventThread or -1,
        #     shortName, title.value
        # ))
        self.collection.append([float(dwmsEventTime - lastTime)/1000,shortName, title.value])

        lastTime = dwmsEventTime


    def setHook(self,WinEventProc, eventType):
        return user32.SetWinEventHook(
            eventType,
            eventType,
            0,
            WinEventProc,
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT
        )
    def PostThreadMessage(self,tid):
        user32.PostThreadMessageW(tid, WM_QUIT, 0, 0)

    def listen(self):
        ole32.CoInitialize(0)
        eventInfo = []
        WinEventProc = WinEventProcType(self.callback)
        user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE

        hookIDs = [self.setHook(WinEventProc, et) for et in eventTypes.keys()]
        if not any(hookIDs):
            # print('SetWinEventHook failed')
            sys.exit(1)
        if self.stop_flag == 1:
            sys.exit()

        msg = ctypes.wintypes.MSG()

        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            print(msg)
            user32.TranslateMessageW(msg)
            user32.DispatchMessageW(msg)



        for hookID in hookIDs:
            user32.UnhookWinEvent(hookID)

        ole32.CoUninitialize()




