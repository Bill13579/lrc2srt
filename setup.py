from cx_Freeze import setup, Executable
includes = ["atexit"] 
exe = Executable(
    script = "lrc2srt.py",
    base = "Win32GUI"
    )
 
setup(
    options = {"build_exe": {"includes": includes}},
    executables = [exe]
    )
