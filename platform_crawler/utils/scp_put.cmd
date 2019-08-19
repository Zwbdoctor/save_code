
        spawn scp G:\python_work\banks\save_data root@47.100.245.190:/data/wenbo    /
        expect "(yes/no)?" {
"       send "yes
        expect "password:"
"       send "pwd@aso@123
"}      } "password:" {send "pwd@aso@123
        expect eof
        exit
