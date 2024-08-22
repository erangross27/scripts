import wmi

def get_intel_gpu_info():
    try:
        c = wmi.WMI()
        gpu_info = c.Win32_VideoController(AdapterCompatibility="Intel Corporation")[0]
        
        print(f"GPU: {gpu_info.Name}")
        
        # Convert memory to GB
        memory_gb = int(gpu_info.AdapterRAM) / (1024**3) if gpu_info.AdapterRAM else "Unknown"
        
        print(f"Total VRAM: {memory_gb:.2f} GB" if isinstance(memory_gb, float) else f"Total VRAM: {memory_gb}")
        
        print(f"Driver Version: {gpu_info.DriverVersion}")
        print(f"Video Processor: {gpu_info.VideoProcessor}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_intel_gpu_info()
