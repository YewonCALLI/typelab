const WebSocket = require('ws');
const http = require('http');

// HTTP 서버 생성 (Railway에서 HTTPS로 자동 업그레이드됨)
const server = http.createServer();

const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  console.log('✅ Client connected');

  ws.on('message', (data, isBinary) => {
    // 받은 데이터를 저장 없이 그대로 모든 클라이언트에게 중계
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data, { binary: isBinary });
      }
    });
  });

  ws.on('close', () => {
    console.log('❌ Client disconnected');
  });
});

// 포트 설정 (Railway에서는 환경변수 PORT 자동 주입)
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`🚀 WebSocket server running on port ${PORT}`);
});
