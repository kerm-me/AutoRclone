#!/bin/bash

# 解析命令行选项
while getopts ":ien:r:" opt; do
  case ${opt} in
    i )
      INSTALL_CADDY=true
      ;;
    n )
      EDIT_CADDYFILE=true
      ;;
    r )
      REMOTE_DOMAIN=$(echo "${OPTARG}" | cut -d":" -f1)
      LOCAL_PORT=$(echo "${OPTARG}" | cut -d":" -f2)
      ;;
    e )
      TLS_EMAIL="${OPTARG}"
      ;;
    \? )
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    : )
      echo "Invalid option: -$OPTARG requires an argument" >&2
      exit 1
      ;;
  esac
done

if [ "$INSTALL_CADDY" = true ]; then
  # 安装 Caddy
  sudo apt update && sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/caddy-stable-archive-keyring.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main" | sudo tee /etc/apt/sources.list.d/caddy-stable.list
  sudo apt update && sudo apt install -y caddy
  
  # 输出安装成功消息
  echo -e "\033[32mCaddy has been installed successfully.\033[0m"
fi

if [ "$EDIT_CADDYFILE" = true ]; then
  # 使用 Nano 编辑 Caddyfile 文件
  sudo nano /etc/caddy/Caddyfile
fi

# 添加反向代理规则
if [ ! -z "$REMOTE_DOMAIN" ] && [ ! -z "$LOCAL_PORT" ]; then
  # 检查 Caddyfile 中是否已存在同名的域名，如果存在则删除该行
  sudo sed -i "/$REMOTE_DOMAIN/d" /etc/caddy/Caddyfile
  
  # 将反向代理规则添加到 Caddyfile 文件末尾
  if [ ! -z "$TLS_EMAIL" ]; then
    echo "$REMOTE_DOMAIN {
      reverse_proxy localhost:$LOCAL_PORT
      tls $TLS_EMAIL
    }" | sudo tee -a /etc/caddy/Caddyfile > /dev/null
    
    # 输出反向代理添加成功消息
    echo -e "\033[32mReverse proxy for $REMOTE_DOMAIN has been added successfully.\033[0m"
  else
    echo "Error: TLS email is required for HTTPS/TLS. Please provide a valid email address using the -e option."
    exit 1
  fi
fi

# 重启 Caddy 服务使其生效
sudo systemctl restart caddy
