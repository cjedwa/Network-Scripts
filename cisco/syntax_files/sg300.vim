" Vim syntax file
" Language: Cisco SG300
" Maintainer: Cody Edwards
" Latest Revision 09 April 2017
if exists("b:current_syntax")
    finish
endif
let b:current_syntax = "sg300"

"Keywords
syn keyword passwords passwords
hi default passwords ctermfg=Blue guifg=Blue

syn region lredConfigs start="\v^interface" end='!'
syn match lredCommand "\v^ip\ ssh\ "
syn match lredCommand "\v^ip\ ssh-client\ "
hi default lredConfigs ctermfg=lightred  guifg=lightred

syn region magentaCommand start="crypto key pubkey-chain ssh" end="\v^exit\nexit"
syn match magentaCommand "\v^aaa\ "
syn match magentaCommand "\v^snmp-server\ "
syn match magentaCommand "\v^logging\ "
hi default magentaCommand ctermfg=Magenta  guifg=Magenta

syn region lblueCommand start="management access-list" end="management access-class"
syn match lblueCommand "\v^voice\ vlan\ "
hi default lblueCommand ctermfg=lightblue  guifg=lightblue

syn match yellowCommand "ip\ dhcp\ "
syn match yellowCommand "\v^ip\ igmp\ "
syn match yellowCommand "\v^ip\ arp\ "
syn match yellowCommand "\v^ip\ source-guard"
syn match yellowCommand "\v^ip\ arp-inspection"
syn match yellowCommand "radius-server\ "
syn region yellowConfigs start="line" end='exit'
hi default yellowCommand ctermfg=yellow  guifg=yellow

syn match brownCommand "cdp\ "
syn match brownCommand "lldp\ "
syn region brownCommand start="banner login #" end="#"
syn match brownCommand "\v^sntp\ "
hi default brownCommand ctermfg=brown  guifg=brown



syn match lcyanCommand "\v^clock\ "
syn match lcyanCommand "\v^username\ "
syn match lcyanCommand "\v^hostname\ "
hi default lcyanCommand ctermfg=lightcyan  guifg=lightcyan

syn match cyanCommand "\v^security-suite\ "
syn match cyanCommand "\v^ip\ default-gateway"
hi default cyanCommand ctermfg=cyan  guifg=cyan


syn match redCommand "\v^no\ "
syn match redCommand "\v^encrypted\ "
syn match redCommand "\v^exit\ "
hi default redCommand ctermfg=Red  guifg=Red
