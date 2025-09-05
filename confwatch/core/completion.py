"""
Autocompletion generator for ConfWatch.
Generates bash and zsh completion scripts.
"""

import os
from typing import List, Dict


class CompletionGenerator:
    """Generates shell completion scripts for ConfWatch."""
    
    def __init__(self):
        self.commands = {
            'list': {'help': 'List monitored files', 'args': []},
            'snapshot': {
                'help': 'Create snapshots',
                'args': ['--comment', '-c', '--force', '-f'],
                'files': True
            },
            'diff': {
                'help': 'Show diff between versions',
                'args': [],
                'files': True
            },
            'history': {
                'help': 'Show file history',
                'args': [],
                'files': True
            },
            'tag': {
                'help': 'Tag current version',
                'args': [],
                'files': True
            },
            'rollback': {
                'help': 'Rollback to specific version',
                'args': [],
                'files': True
            },
            'web': {
                'help': 'Start web interface',
                'args': ['--host', '--port', '--debug']
            },
            'web-daemon': {
                'help': 'Manage persistent web server daemon',
                'subcommands': {
                    'start': {'args': ['--host', '--port', '--debug', '--foreground', '-f']},
                    'stop': {'args': []},
                    'restart': {'args': ['--host', '--port', '--debug']},
                    'status': {'args': []},
                    'config': {'args': ['--host', '--port', '--debug']}
                }
            },
            'daemon': {
                'help': 'Manage file monitoring daemon',
                'subcommands': {
                    'start': {'args': ['--foreground', '-f', '--polling', '-p']},
                    'stop': {'args': []},
                    'restart': {'args': ['--polling', '-p']},
                    'status': {'args': []}
                }
            },
            'update': {
                'help': 'Update ConfWatch to latest version',
                'args': ['--force', '-f', '--branch']
            },
            'reset-password': {
                'help': 'Reset web interface password',
                'args': ['--force', '-f']
            },
            'uninstall': {
                'help': 'Uninstall ConfWatch',
                'args': ['--force', '-f']
            }
        }
    
    def generate_bash_completion(self) -> str:
        """Generate bash completion script."""
        script = '''#!/usr/bin/env bash
# ConfWatch bash completion script

_confwatch_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    local commands="list snapshot diff history tag rollback web web-daemon daemon update reset-password uninstall"
    
    # Global options
    local global_opts="--help -h --version"
    
    # If we're completing the first argument (command)
    if [[ ${COMP_CWORD} == 1 ]]; then
        COMPREPLY=( $(compgen -W "${commands} ${global_opts}" -- ${cur}) )
        return 0
    fi
    
    local command="${COMP_WORDS[1]}"
    
    case $command in
        snapshot)
            local opts="--comment -c --force -f"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                # Complete file paths
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            ;;
        diff|history|tag|rollback)
            if [[ ${cur} == -* ]]; then
                COMPREPLY=()
            else
                # Complete file paths
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            ;;
        web)
            local opts="--host --port --debug"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        web-daemon)
            local subcommands="start stop restart status config"
            if [[ ${COMP_CWORD} == 2 ]]; then
                COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
            else
                local subcmd="${COMP_WORDS[2]}"
                case $subcmd in
                    start|config)
                        local opts="--host --port --debug --foreground -f"
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                        ;;
                    restart)
                        local opts="--host --port --debug"
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                        ;;
                    stop|status)
                        COMPREPLY=()
                        ;;
                esac
            fi
            ;;
        daemon)
            local subcommands="start stop restart status"
            if [[ ${COMP_CWORD} == 2 ]]; then
                COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
            else
                local subcmd="${COMP_WORDS[2]}"
                case $subcmd in
                    start|restart)
                        local opts="--foreground -f --polling -p"
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                        ;;
                    stop|status)
                        COMPREPLY=()
                        ;;
                esac
            fi
            ;;
        update)
            local opts="--force -f --branch"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        reset-password|uninstall)
            local opts="--force -f"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

# Register completion function
complete -F _confwatch_completion confwatch
'''
        return script
    
    def generate_zsh_completion(self) -> str:
        """Generate zsh completion script."""
        script = '''#compdef confwatch
# ConfWatch zsh completion script

_confwatch() {
    local context state state_descr line
    typeset -A opt_args
    
    _arguments -C \\
        '1: :_confwatch_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in
                snapshot)
                    _arguments \\
                        '(-c --comment)'{-c,--comment}'[Comment for snapshot]:comment:' \\
                        '(-f --force)'{-f,--force}'[Force snapshot creation]' \\
                        '*:file:_files'
                    ;;
                diff|history|tag|rollback)
                    _arguments '*:file:_files'
                    ;;
                web)
                    _arguments \\
                        '--host[Host to bind to]:host:' \\
                        '--port[Port to bind to]:port:' \\
                        '--debug[Enable debug mode]'
                    ;;
                web-daemon)
                    _confwatch_web_daemon
                    ;;
                daemon)
                    _confwatch_daemon
                    ;;
                update)
                    _arguments \\
                        '(-f --force)'{-f,--force}'[Force update without confirmation]' \\
                        '--branch[Branch to update from]:branch:'
                    ;;
                reset-password|uninstall)
                    _arguments \\
                        '(-f --force)'{-f,--force}'[Force without confirmation]'
                    ;;
            esac
            ;;
    esac
}

_confwatch_commands() {
    local commands; commands=(
        'list:List monitored files'
        'snapshot:Create snapshots'
        'diff:Show diff between versions'
        'history:Show file history'
        'tag:Tag current version'
        'rollback:Rollback to specific version'
        'web:Start web interface'
        'web-daemon:Manage persistent web server daemon'
        'daemon:Manage file monitoring daemon'
        'update:Update ConfWatch to latest version'
        'reset-password:Reset web interface password'
        'uninstall:Uninstall ConfWatch'
    )
    _describe 'command' commands
}

_confwatch_web_daemon() {
    local context state state_descr line
    typeset -A opt_args
    
    _arguments -C \\
        '1: :_confwatch_web_daemon_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[2] in
                start|config)
                    _arguments \\
                        '--host[Host to bind to]:host:' \\
                        '--port[Port to bind to]:port:' \\
                        '--debug[Enable debug mode]' \\
                        '(-f --foreground)'{-f,--foreground}'[Run in foreground]'
                    ;;
                restart)
                    _arguments \\
                        '--host[Host to bind to]:host:' \\
                        '--port[Port to bind to]:port:' \\
                        '--debug[Enable debug mode]'
                    ;;
            esac
            ;;
    esac
}

_confwatch_web_daemon_commands() {
    local commands; commands=(
        'start:Start persistent web server daemon'
        'stop:Stop persistent web server daemon'
        'restart:Restart persistent web server daemon'
        'status:Show web daemon status'
        'config:Configure web daemon settings'
    )
    _describe 'web-daemon command' commands
}

_confwatch_daemon() {
    local context state state_descr line
    typeset -A opt_args
    
    _arguments -C \\
        '1: :_confwatch_daemon_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[2] in
                start|restart)
                    _arguments \\
                        '(-f --foreground)'{-f,--foreground}'[Run in foreground]' \\
                        '(-p --polling)'{-p,--polling}'[Use polling instead of watchdog]'
                    ;;
            esac
            ;;
    esac
}

_confwatch_daemon_commands() {
    local commands; commands=(
        'start:Start file monitoring daemon'
        'stop:Stop file monitoring daemon'
        'restart:Restart file monitoring daemon'
        'status:Show daemon status'
    )
    _describe 'daemon command' commands
}

_confwatch "$@"
'''
        return script
    
    def save_completion_scripts(self, output_dir: str):
        """Save completion scripts to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save bash completion
        bash_script = self.generate_bash_completion()
        bash_file = os.path.join(output_dir, "confwatch-completion.bash")
        with open(bash_file, 'w') as f:
            f.write(bash_script)
        
        # Save zsh completion
        zsh_script = self.generate_zsh_completion()
        zsh_file = os.path.join(output_dir, "_confwatch")
        with open(zsh_file, 'w') as f:
            f.write(zsh_script)
        
        return bash_file, zsh_file 