from cx_Freeze import setup, Executable

setup(
    name="compress_pdf",
    version="0.1",
    description="A PDF compression tool",
    executables=[Executable("compress_zip_file_nice.py")],
)