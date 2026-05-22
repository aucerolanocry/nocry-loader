#!/data/data/com.termux/files/usr/bin/bash

SERVER="https://nocry-loader.onrender.com"

echo ""
echo "  ⭒ NOCRY SYSTEM - INICIANDO..."
echo ""

# Pede a licença
echo -e -n "  ⭒ INSIRA SUA LICENCA: "
read LICENSE_KEY

if [ -z "$LICENSE_KEY" ]; then
    echo "  ☠ LICENCA NAO INFORMADA!"
    exit 1
fi

# Verifica conexao e configura ambiente
installer=$(dumpsys package com.termux 2>/dev/null | grep "installerPackageName" | head -1 | cut -d'=' -f2 | tr -d ' \r')

if [ "$installer" = "com.android.vending" ]; then
    echo ""
    echo "  ⭒ TERMUX PLAY STORE DETECTADO - CONFIGURANDO..."
    curl -s --max-time 10 https://termux.net/termux-keyring.gpg | apt-key add - 2>/dev/null
    echo 'deb https://termux.net stable main' > $PREFIX/etc/apt/sources.list
    apt-get update -y 2>/dev/null
    apt-get full-upgrade -y 2>/dev/null
else
    echo ""
    echo "  ⭒ ATUALIZANDO PACOTES..."
    apt update -y 2>/dev/null
    apt full-upgrade -y 2>/dev/null
fi

echo ""
echo "  ⭒ INSTALANDO DEPENDENCIAS..."
pkg install curl android-tools unzip -y 2>/dev/null

echo ""
echo "  ⭒ VERIFICANDO LICENCA..."
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "${SERVER}/get?key=${LICENSE_KEY}")

if [ "$RESPONSE" = "200" ]; then
    echo "  ⭒ LICENCA VALIDA! INICIANDO..."
    echo ""
    sleep 1
    curl -s "${SERVER}/get?key=${LICENSE_KEY}" | bash
else
    echo "  ☠ LICENCA INVALIDA OU SEM CONEXAO!"
    exit 1
fi
