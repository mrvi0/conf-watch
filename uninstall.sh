#!/usr/bin/env bash

# ConfWatch Uninstaller
# Удаляет все файлы, каталоги и алиасы, связанные с ConfWatch

CONFWATCH_HOME="$HOME/.confwatch"

print_header() {
    echo -e "\n\033[1;36m$1\033[0m"
    echo "=================================================="
}

print_header "ConfWatch Uninstaller"

# Подтверждение
read -p "Вы уверены, что хотите полностью удалить ConfWatch? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Удаление отменено."
    exit 0
fi

# Удаление каталога
if [[ -d "$CONFWATCH_HOME" ]]; then
    rm -rf "$CONFWATCH_HOME"
    echo "Удалён каталог $CONFWATCH_HOME"
else
    echo "Каталог $CONFWATCH_HOME не найден."
fi

# Удаление алиасов и PATH из .bashrc
if [[ -f "$HOME/.bashrc" ]]; then
    sed -i '/confwatch/d' "$HOME/.bashrc"
    sed -i '/.confwatch/d' "$HOME/.bashrc"
    echo "Алиасы и PATH удалены из .bashrc"
fi

print_header "Удаление завершено!"
echo "Если вы хотите полностью очистить систему, перезапустите терминал или выполните: source ~/.bashrc" 