#!/bin/bash
echo "🔥 Instalando DIABOLIC BALEARES..."
if [ -d "/data/data/com.termux" ]; then
    pkg update && pkg install python git -y
else
    sudo apt update && sudo apt install python3 python3-pip git -y
fi
pip install flask requests beautifulsoup4
git clone https://github.com/Condor2026/Diabolic_v17
cd Diabolic_v17
echo "✅ Listo. Ejecuta: python Diabolic_v17.py"
