#!/bin/sh
set -e

if [ -n "$XRAY_SUBSCRIPTION_URL" ]; then
  echo "📥 Fetching subscription from $XRAY_SUBSCRIPTION_URL ..."
  RAW=$(wget -qO- "$XRAY_SUBSCRIPTION_URL" 2>/dev/null || curl -fsSL "$XRAY_SUBSCRIPTION_URL")
  if [ -z "$RAW" ]; then
    echo "❌ Failed to fetch subscription URL"
    exit 1
  fi
  DECODED=$(printf '%s' "$RAW" | base64 -d 2>/dev/null)
  XRAY_VLESS_URL=$(printf '%s' "$DECODED" | grep '^vless://' | head -n1)
  if [ -z "$XRAY_VLESS_URL" ]; then
    echo "❌ No vless:// entry found in subscription"
    exit 1
  fi
  echo "✅ Got VLESS URL from subscription"
fi

if [ -z "$XRAY_VLESS_URL" ]; then
  echo "❌ Neither XRAY_SUBSCRIPTION_URL nor XRAY_VLESS_URL is set!"
  exit 1
fi

echo "🧩 Parsing XRAY_VLESS_URL..."

UUID=$(echo "$XRAY_VLESS_URL"     | sed -n 's#vless://\([^@]*\)@.*#\1#p')
SERVER=$(echo "$XRAY_VLESS_URL"   | sed -n 's#vless://[^@]*@\([^:]*\):.*#\1#p')
PORT=$(echo "$XRAY_VLESS_URL"     | sed -n 's#vless://[^@]*@[^:]*:\([0-9]*\).*#\1#p')
SECURITY=$(echo "$XRAY_VLESS_URL" | grep -o 'security=[^&# ]*' | cut -d= -f2)
TYPE=$(echo "$XRAY_VLESS_URL"     | grep -o 'type=[^&# ]*'     | cut -d= -f2)
FP=$(echo "$XRAY_VLESS_URL"       | grep -o 'fp=[^&# ]*'       | cut -d= -f2)
SNI=$(echo "$XRAY_VLESS_URL"      | grep -o 'sni=[^&# ]*'      | cut -d= -f2)
PBK=$(echo "$XRAY_VLESS_URL"      | grep -o 'pbk=[^&# ]*'      | cut -d= -f2)
SID=$(echo "$XRAY_VLESS_URL"      | grep -o 'sid=[^&# ]*'      | cut -d= -f2)
SPX=$(echo "$XRAY_VLESS_URL"      | grep -o 'spx=[^&# ]*'      | cut -d= -f2)
PATH_ENC=$(echo "$XRAY_VLESS_URL" | grep -o 'path=[^&# ]*'     | cut -d= -f2)
MODE=$(echo "$XRAY_VLESS_URL"     | grep -o 'mode=[^&# ]*'     | cut -d= -f2)

urldecode() { printf '%b' "${1//%/\\x}"; }

SPX_DEC=$(urldecode "$SPX")
PATH_DEC=$(urldecode "$PATH_ENC")
[ -z "$PATH_DEC" ] && PATH_DEC="/"
[ -z "$MODE" ]     && MODE="auto"

echo "✅ Generating config.json for type=$TYPE security=$SECURITY..."

build_stream_settings() {
  _NET="$1"
  _SEC="$2"

  if [ "$_NET" = "xhttp" ]; then
    NET_BLOCK="\"xhttpSettings\": {\"path\": \"$PATH_DEC\", \"mode\": \"$MODE\"}"
  elif [ "$_NET" = "ws" ]; then
    NET_BLOCK="\"wsSettings\": {\"path\": \"$PATH_DEC\"}"
  elif [ "$_NET" = "grpc" ]; then
    NET_BLOCK="\"grpcSettings\": {\"serviceName\": \"$PATH_DEC\"}"
  else
    NET_BLOCK=""
  fi

  if [ "$_SEC" = "reality" ]; then
    SEC_BLOCK="\"realitySettings\": {
        \"show\": false,
        \"fingerprint\": \"$FP\",
        \"serverName\": \"$SNI\",
        \"publicKey\": \"$PBK\",
        \"shortId\": \"$SID\",
        \"spiderX\": \"$SPX_DEC\"
      }"
  elif [ "$_SEC" = "tls" ]; then
    SEC_BLOCK="\"tlsSettings\": {\"serverName\": \"$SNI\"}"
  else
    SEC_BLOCK=""
  fi

  PARTS="\"network\": \"$_NET\", \"security\": \"$_SEC\""
  [ -n "$NET_BLOCK" ] && PARTS="$PARTS, $NET_BLOCK"
  [ -n "$SEC_BLOCK" ] && PARTS="$PARTS, $SEC_BLOCK"

  echo "$PARTS"
}

STREAM=$(build_stream_settings "$TYPE" "$SECURITY")

if [ "$SECURITY" = "reality" ] && [ "$TYPE" != "xhttp" ]; then
  USER_JSON="{\"id\": \"$UUID\", \"encryption\": \"none\", \"flow\": \"xtls-rprx-vision\"}"
else
  USER_JSON="{\"id\": \"$UUID\", \"encryption\": \"none\"}"
fi

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
      "users": [$USER_JSON]
    }]},
    "streamSettings": {$STREAM}
  }]
}
EOF

echo "✅ Starting Xray (server=$SERVER:$PORT type=$TYPE security=$SECURITY)..."
exec /usr/bin/xray -config /etc/xray/config.json
