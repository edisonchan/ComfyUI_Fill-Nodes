# custom_nodes/FL_SystemCheck.py

import sys
import os
import platform
import psutil
import importlib
import pkg_resources
import cpuinfo
import json
from server import PromptServer
from aiohttp import web
from typing import Dict, Any

class FL_SystemCheck:
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {"required": {}}

    RETURN_TYPES = ()
    FUNCTION = "run_check"
    OUTPUT_NODE = True
    CATEGORY = "🏵️Fill Nodes/utility"

    def run_check(self) -> tuple:
        return (True,)

def gather_system_info() -> Dict[str, Any]:
    # --------------------------
    # Helper Functions
    # --------------------------
    def safe_get_cpu_info() -> str:
        try:
            return cpuinfo.get_cpu_info().get('brand_raw', 'Unable to determine')
        except Exception:
            return "CPU info error"

    def get_gpu_info() -> str:
        try:
            import torch
            if torch.cuda.is_available():
                # NVIDIA GPU 信息
                gpu_name = torch.cuda.get_device_name(0)
                vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
                sm_version = torch.cuda.get_device_properties(0).major, torch.cuda.get_device_properties(0).minor
                return f"{gpu_name} {vram:.0f} GB (SM {sm_version[0]}{sm_version[1]})"
            else:
                try:
                    import pyopencl as cl
                    platforms = cl.get_platforms()
                    for platform in platforms:
                        devices = platform.get_devices()
                        for device in devices:
                            if device.type == cl.device_type.GPU:
                                gpu_name = device.name
                                vram = device.global_mem_size / (1024 ** 3)
                                # 获取 AMD 显卡的架构版本
                                amd_arch = device.get_info(cl.device_info.NAME)  # 通常包含类似 gfx1201 的信息
                                return f"{gpu_name} {vram:.0f} GB (Arch {amd_arch})"
                    return "No GPU found (AMD or NVIDIA)"
                except ImportError:
                    return "PyTorch not installed, and pyopencl not installed for AMD GPU detection"
        except Exception as e:
            return f"GPU detection error: {str(e)}"


    def get_library_version(library: str, pkg_name: str = None) -> str:
        pkg = pkg_name or library
        try:
            return pkg_resources.get_distribution(pkg).version
        except pkg_resources.DistributionNotFound:
            pass
        except Exception as e:
            return f"Pkg error: {str(e)}"
        
        try:
            module = importlib.import_module(library)
            return getattr(module, "__version__", "No version attribute")
        except ImportError:
            return "Not installed"
        except Exception as e:
            return f"Module error: {str(e)}"

    def get_env_var(var: str) -> str:  # 确保此函数存在
        return os.environ.get(var, 'Not set')

    # --------------------------
    # 信息收集
    # --------------------------
    info = {
        "Python version": sys.version.split()[0],
        "Operating System": f"{platform.system()} {platform.release()}",
        "CPU": safe_get_cpu_info(),
        "RAM": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        "GPU": get_gpu_info(),
        "PyTorch": get_library_version('torch'),
        "torchvision": get_library_version('torchvision'),
        "torchaudio": get_library_version('torchaudio'),
        "xformers": get_library_version('xformers'),
        "sageattention": get_library_version('sageattention', pkg_name='sageattention'),
        "Triton": get_library_version('triton'),
        "OpenCV": get_library_version('cv2', 'opencv-python'),
        "Pillow": get_library_version('PIL', 'pillow'),
        "numpy": get_library_version('numpy'),
        "transformers": get_library_version('transformers'),
        "diffusers": get_library_version('diffusers'),
        **{f"Env: {var}": get_env_var(var) for var in ['PYTHONPATH', 'CUDA_HOME', 'LD_LIBRARY_PATH']}
    }
    return info

# --------------------------
# Web 路由注册
# --------------------------
@PromptServer.instance.routes.get("/fl_system_info")
async def system_info(request: web.Request) -> web.Response:
    try:
        return web.json_response(gather_system_info())
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

if __name__ == "__main__":
    print(json.dumps(gather_system_info(), indent=2))
