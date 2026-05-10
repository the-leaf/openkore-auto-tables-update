import re
import requests
import subprocess



class Patches:
    def __init__(self, server_name, patch_info, patch_file):
        self.server_name = server_name
        self.patch_info = patch_info
        self.patch_file = patch_file

    def get_patchinfo(self):
        resp = requests.get(self.patch_info)
        if resp.status_code == 200:
            patches = []
            for i in resp.text.splitlines():
                if not '//' in i and len(i) > 0:
                    data = i.split()
                    patches.append(data[1])
            return patches


    def get_patchfile(self, name):
        resp = requests.get(f"{self.patch_file}/{name}")
        if resp.status_code == 200:
            with open(f"./patches/{self.server_name}/downloaded/{name}", 'wb') as File:
                File.write(resp.content)
            return True
        return False

    def unpack_rgz(self, filename):
        # ใส่ sudo กลับเข้ามาเพื่อให้รันเครื่องมือภายนอกได้สมบูรณ์
        cmd = f"sudo perl ./tools/rgz.pl -l -v {filename}"
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        lines, error = process.communicate()
        process.wait()

        lines = lines.splitlines()
        # ป้องกันข้อผิดพลาดเช็คว่ามีข้อมูลให้ pop หรือไม่
        if len(lines) > 0: lines.pop(0)

        output = {}
        for i in lines:
            if len(i) > 0:
                data = list(i.strip().decode('UTF-8', errors='ignore').split())
                if len(data) >= 3:
                    output[data[2]] = data[1]
        return output

    def unpack_rgz_file(self, rgz, rgz_file, rgz_file_format_name):
        rgz_file = rgz_file.replace('\\\\', '\\')
        # ใส่ sudo กลับเข้ามา
        cmd = f"sudo perl ./tools/rgz.pl -x {rgz} {rgz_file} ./patches/{self.server_name}/extracted/{rgz_file_format_name}"
        process = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        lines, error = process.communicate()
        process.wait()
        return True

    def unpack_gpf(self, filename):
        # ใส่ sudo กลับเข้ามา
        cmd = f'sudo ./tools/grf_extract {filename}'
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        lines, error = process.communicate()
        process.wait()

        lines = lines.splitlines()
        
        # แก้ไขจุดนี้: เช็คความปลอดภัยก่อนลบบรรทัดหัวข้อ (Header) ถ้าไม่มีข้อมูลให้ข้ามไปเลย
        if len(lines) > 0: lines.pop(0)
        if len(lines) > 0: lines.pop(0)

        output = {}
        for i in lines:
            if len(i) > 0:
                matches = re.findall(r'(.*)\s\((\d+)\)', i.strip().decode('UTF-8', errors='ignore'))
                if matches:
                    data = list(matches[0])
                    output[data[0]] = data[1]
        return output

    def unpack_gpf_file(self, gpf, gpf_file, gpf_file_format_name):
        # ใส่ sudo กลับเข้ามา
        cmd = f'sudo ./tools/grf_extract {gpf} {gpf_file} ./patches/{self.server_name}/extracted/{gpf_file_format_name}'
        process = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        lines, error = process.communicate()
        process.wait()
        return True
