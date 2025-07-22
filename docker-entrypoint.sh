#!/bin/env sh
set -e

CONFIG="/etc/phpmyadmin/config.user.inc.php"
cat > "$CONFIG" <<'EOF'
<?php
$i = 0;
EOF

# 找到所有 PMA_HOST_N 環境變數
for name in $(env | awk -F= '/^PMA_HOST_[0-9]+/ {print $1}' | sort); do
  n=$(echo "$name" | sed 's/^PMA_HOST_//')
  # 使用 eval 讀取對應變數
  eval host=\$$name
  eval user=\$PMA_USER_$n
  [ -z "$user" ] && continue

  eval pass=\$PMA_PASS_$n
  eval label=\$PMA_LABEL_$n
  eval port=\$PMA_PORT_$n
  eval ssl_flag=\$PMA_SSL_$n
  eval ssl_ca=\$PMA_SSL_CA_$n
  eval ssl_verify=\$PMA_SSL_VERIFY_$n

  cat >> "$CONFIG" <<EOF

\$i++;
\$cfg['Servers'][\$i]['verbose']   = '${label:-Server $n}';
\$cfg['Servers'][\$i]['host']      = '$host';
\$cfg['Servers'][\$i]['port']      = '$port';
\$cfg['Servers'][\$i]['auth_type'] = '$AUTH_TYPE';
\$cfg['Servers'][\$i]['user']      = '$user';
\$cfg['Servers'][\$i]['password']  = '$pass';
\$cfg['Servers'][\$i]['extension'] = 'mysqli';
EOF

  if [ "$ssl_flag" = "true" ]; then
    cat >> "$CONFIG" <<EOF
\$cfg['Servers'][\$i]['ssl']        = true;
\$cfg['Servers'][\$i]['ssl_ca']     = '$ssl_ca';
\$cfg['Servers'][\$i]['ssl_verify'] = ${ssl_verify:-true};
EOF
  fi
  echo "$host:$port"
done

if [ ! -f /etc/phpmyadmin/config.secret.inc.php ]; then
  cat > /etc/phpmyadmin/config.secret.inc.php <<EOF
<?php
\$cfg['blowfish_secret'] = '$(openssl rand -base64 32)';
EOF
fi

apache2-foreground