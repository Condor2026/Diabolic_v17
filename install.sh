#!/bin/bash
echo "🔥 Instalando Diabolic_v17..."
pkg update && pkg install python git -y
pip install flask requests beautifulsoup4
git clone https://github.com/Conder2026/Diabolic_v17.py
cd Diabolic_v17.py
echo "✅ Listo. Ejecuta: python Diabolic_v17.py"