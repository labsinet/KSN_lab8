#!/usr/bin/env python3
"""Автоматична перевірка ЛР8 (Vagrant). Лише стандартна бібліотека."""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PASS_SCORE = int(os.environ.get("PASS_SCORE", "70"))

VARIANTS = {
    1: "ubuntu/jammy64", 2: "ubuntu/focal64", 3: "bento/ubuntu-24.04",
    4: "bento/ubuntu-22.04", 5: "bento/ubuntu-20.04", 6: "bento/debian-12",
    7: "bento/debian-11", 8: "bento/almalinux-9", 9: "bento/almalinux-8",
    10: "bento/rockylinux-9", 11: "bento/rockylinux-8",
    12: "bento/centos-stream-9", 13: "bento/fedora-latest",
    14: "generic/ubuntu2204", 15: "generic/ubuntu2004",
    16: "generic/debian12", 17: "generic/debian11", 18: "generic/alma9",
    19: "generic/rocky9", 20: "generic/alpine319",
    21: "geerlingguy/ubuntu2204", 22: "geerlingguy/ubuntu2004",
    23: "geerlingguy/debian12", 24: "geerlingguy/rockylinux9",
    25: "geerlingguy/rockylinux8", 26: "hashicorp/bionic64",
    27: "bento/ubuntu-22.04",  # + LAMP
    28: "bento/oraclelinux-9", 29: "generic/oracle9",
}
LAMP_VARIANT = 27

COMMANDS = [
    "vagrant up", "vagrant ssh", "vagrant status", "vagrant halt",
    "vagrant reload", "vagrant provision", "vagrant snapshot",
    "vagrant box list", "vagrant global-status", "vagrant destroy",
]

results = []


def check(name, points, earned, detail=""):
    earned = max(0.0, min(float(points), float(earned)))
    results.append({"name": name, "points": points,
                    "earned": round(earned, 1), "detail": detail})


def read(path):
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else None


# ---------- variant ----------
variant = None
raw = read("variant.txt")
if raw and raw.strip().isdigit() and int(raw.strip()) in VARIANTS:
    variant = int(raw.strip())
    check("Коректний variant.txt", 5, 5, f"варіант {variant}")
else:
    check("Коректний variant.txt", 5, 0, "потрібне число від 1 до 29")

# ---------- Vagrantfile ----------
vf_raw = read("Vagrantfile")
check("Наявність Vagrantfile", 5, 5 if vf_raw else 0,
      "" if vf_raw else "файл не знайдено")
vf = ""
if vf_raw:
    vf = "\n".join(l for l in vf_raw.splitlines()
                   if not l.strip().startswith("#"))

validate_ok = os.environ.get("VALIDATE_OUTCOME") == "success"
check("vagrant validate", 10, 10 if validate_ok else 0,
      "" if validate_ok else "команда завершилась з помилкою (див. лог кроку)")

# box
m = re.search(r'config\.vm\.box\s*=\s*["\']([^"\']+)["\']', vf)
box = m.group(1) if m else None
if variant and box == VARIANTS[variant]:
    check("Box збігається з варіантом", 10, 10, box)
else:
    exp = VARIANTS.get(variant, "?")
    check("Box збігається з варіантом", 10, 0,
          f"знайдено: {box!r}, очікується: {exp!r}")

# hostname
m = re.search(r'config\.vm\.hostname\s*=\s*["\']([^"\']+)["\']', vf)
check("Заданий hostname", 5, 5 if m else 0,
      "" if m else "додайте config.vm.hostname")

# resources
mem = re.search(r'\.memory\s*=\s*(\d+)', vf)
cpu = re.search(r'\.cpus\s*=\s*(\d+)', vf)
res_ok = bool(mem and int(mem.group(1)) >= 1024 and cpu and int(cpu.group(1)) >= 1)
check("ОЗУ ≥ 1024 МБ та cpus", 5, 5 if res_ok else 0,
      "" if res_ok else "задайте vb.memory >= 1024 та vb.cpus >= 1")

# port
port_ok = bool(re.search(
    r'forwarded_port[^\n]*guest:\s*80[^\n]*host:\s*8080|'
    r'forwarded_port[^\n]*host:\s*8080[^\n]*guest:\s*80', vf))
check("Проброс порту 80 → 8080", 5, 5 if port_ok else 0,
      "" if port_ok else 'config.vm.network "forwarded_port", guest: 80, host: 8080')

# provision
prov = "config.vm.provision" in vf
web = bool(re.search(r'nginx|apache2|httpd', vf))
if variant == LAMP_VARIANT:
    need = bool(re.search(r'apache2|httpd', vf)) and "php" in vf \
        and bool(re.search(r'mysql|mariadb', vf, re.I))
    detail = "варіант 27: потрібні Apache, PHP та MySQL/MariaDB"
else:
    need = web
    detail = "provisioner має встановлювати nginx / apache2 / httpd"
check("Provisioner встановлює вебсервер", 10, 10 if (prov and need) else 0,
      "" if (prov and need) else detail)

# ---------- report ----------
rep = read("report.md") or ""
if not rep:
    check("ПІБ, група, варіант у звіті", 5, 0, "report.md не знайдено")
else:
    def field(label):
        mm = re.search(rf'{label}:[ \t]*(.*)', rep)
        return mm.group(1).strip() if mm else ""
    fio, grp, var_rep = field("ПІБ"), field("Група"), field(r"Варіант[^:\n]*")
    ok = len(fio) >= 5 and len(grp) >= 2 and var_rep.strip().isdigit() \
        and variant is not None and int(var_rep.strip()) == variant
    check("ПІБ, група, варіант у звіті", 5, 5 if ok else 0,
          "" if ok else "заповніть ПІБ, групу; варіант має збігатися з variant.txt")

vag_ver = bool(re.search(r'Vagrant\s+\d+\.\d+\.\d+', rep))
vbox_ver = bool(re.search(r'\d+\.\d+\.\d+r\d+', rep))
check("Версії vagrant та VirtualBox у звіті", 5,
      2.5 * vag_ver + 2.5 * vbox_ver,
      "" if (vag_ver and vbox_ver) else
      "вставте вивід `vagrant --version` та `VBoxManage --version`")

found = [c for c in COMMANDS if c in rep]
missing = [c for c in COMMANDS if c not in rep]
check("Команди керування у звіті", 5, 5 * len(found) / len(COMMANDS),
      "" if not missing else "не згадано: " + ", ".join(missing))

# screenshots
shots = [p for p in (ROOT / "screenshots").glob("*")
         if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
check("Скріншоти (≥5)", 10, 10 * min(len(shots), 5) / 5,
      f"знайдено {len(shots)}")

# questions
good = 0
bad = []
for n in range(1, 11):
    mm = re.search(rf'###\s*Питання\s*{n}\b(.*?)(?=\n###\s|\n##\s|\Z)', rep, re.S)
    ans = ""
    if mm:
        a = re.search(r'\*\*Відповідь:\*\*(.*)', mm.group(1), re.S)
        ans = a.group(1).strip() if a else ""
    if len(ans) >= 40 and "TODO" not in ans:
        good += 1
    else:
        bad.append(n)
check("Відповіді на 10 питань", 20, 2 * good,
      "" if not bad else "потребують відповіді (≥40 символів): " +
      ", ".join(map(str, bad)))

# ---------- підсумок ----------
total = round(sum(r["earned"] for r in results), 1)
passed = total >= PASS_SCORE

lines = ["## Результат автоперевірки ЛР8", "",
         "| Перевірка | Бали | Коментар |", "|---|---|---|"]
for r in results:
    mark = "✅" if r["earned"] >= r["points"] else ("⚠️" if r["earned"] > 0 else "❌")
    lines.append(f'| {mark} {r["name"]} | {r["earned"]}/{r["points"]} | {r["detail"]} |')
lines += ["", f"**Разом: {total}/100** (прохідний бал — {PASS_SCORE}) — "
          + ("**зараховано автоматикою**" if passed else "**не зараховано**"),
          "", "_Автоматика не запускає ВМ; виводи та скріншоти перевіряє викладач._"]
summary = "\n".join(lines)
print(summary)

if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
        f.write(summary + "\n")

(ROOT / "results.json").write_text(
    json.dumps({"variant": variant, "score": total, "passed": passed,
                "checks": results}, ensure_ascii=False, indent=2),
    encoding="utf-8")
sys.exit(0 if passed else 1)
