#!/bin/sh
set -e

if [ -z "$XRAY_VLESS_URL" ]; then
  echo "❌ XRAY_VLESS_URL not set!"
  exit 1
fi

echo "🧩 Parsing XRAY_VLESS_URL..."

UUID=$(echo "$XRAY_VLESS_URL" | sed -n 's#vless://\([^@]*\)@.*#\1#p')
SERVER=$(echo "$XRAY_VLESS_URL" | sed -n 's#vless://[^@]*@\([^:]*\):.*#\1#p')
PORT=$(echo "$XRAY_VLESS_URL" | sed -n 's#.*:\([0-9]*\).*#\1#p')
SECURITY=$(echo "$XRAY_VLESS_URL" | grep -o 'security=[^&]*' | cut -d= -f2)
TYPE=$(echo "$XRAY_VLESS_URL" | grep -o 'type=[^&]*' | cut -d= -f2)
FP=$(echo "$XRAY_VLESS_URL" | grep -o 'fp=[^&]*' | cut -d= -f2)
SNI=$(echo "$XRAY_VLESS_URL" | grep -o 'sni=[^&]*' | cut -d= -f2)
PBK=$(echo "$XRAY_VLESS_URL" | grep -o 'pbk=[^&]*' | cut -d= -f2)
SID=$(echo "$XRAY_VLESS_URL" | grep -o 'sid=[^&]*' | cut -d= -f2)
SPX=$(echo "$XRAY_VLESS_URL" | grep -o 'spx=[^&]*' | cut -d= -f2)

SPX_DEC=$(printf '%b' "${SPX//%/\\x}")

echo "✅ Generating config.json for $TYPE + $SECURITY..."

if [ "$SECURITY" = "reality" ]; then
  cat <<EOF > /etc/xray/config.json
{
  "inbounds": [{
    "port": 10808,
    "listen": "0.0.0.0",
    "protocol": "socks",
    "settings": {"udp": true}
  }],
  "outbounds": [{
    "protocol": "vless",
    "settings": {"vnext": [{
      "address": "$SERVER",
      "port": $PORT,
      "users": [{
        "id": "$UUID",
        "encryption": "none",
        "flow": "xtls-rprx-vision"
      }]
    }]},
    "streamSettings": {
      "network": "$TYPE",
      "security": "reality",
      "realitySettings": {
        "show": false,
        "fingerprint": "$FP",
        "serverName": "$SNI",
        "publicKey": "$PBK",
        "shortId": "$SID",
        "spiderX": "$SPX_DEC"
      }
    }
  }]
}
EOF

elif [ "$SECURITY" = "tls" ]; then
  cat <<EOF > /etc/xray/config.json
{
  "inbounds": [{
    "port": 10808,
    "listen": "0.0.0.0",
    "protocol": "socks",
    "settings": {"udp": true}
  }],
  "outbounds": [{
    "protocol": "vless",
    "settings": {"vnext": [{
      "address": "$SERVER",
      "port": $PORT,
      "users": [{"id": "$UUID","encryption":"none"}]
    }]},
    "streamSettings": {
      "network": "$TYPE",
      "security": "tls",
      "tlsSettings": {"serverName": "$SNI"}
    }
  }]
}
EOF

else
  cat <<EOF > /etc/xray/config.json
{
  "inbounds": [{
    "port": 10808,
    "listen": "0.0.0.0",
    "protocol": "socks",
    "settings": {"udp": true}
  }],
  "outbounds": [{
    "protocol": "vless",
    "settings": {"vnext": [{
      "address": "$SERVER",
      "port": $PORT,
      "users": [{"id": "$UUID","encryption":"none"}]
    }]},
    "streamSettings": {"network": "$TYPE","security":"none"}
  }]
}
EOF
fi

echo "✅ Starting Xray..."
exec /usr/bin/xray -config /etc/xray/config.json
