const express = require('express');
const http = require('http');
const websocket = require('ws');
const { parse } = require('url');
const os = require('os');

const app = express();
const server = http.createServer(app);
const socket = new websocket.Server({ server });

app.use(express.static('web'));

server.listen(80, () => {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        console.log(`접속 주소: http://${net.address}`);
      }
    }
  }
});

let clients = []; // { id, idNum, ws }
let clientUrls = {}; // { web1: 'url' }
const fallbackUrls = [
  "https://example.com",
  "https://www.youtube.com/embed/dQw4w9WgXcQ",
  "https://threejs.org",
  "https://orwiss.xyz",
  "https://web.dev",
  "https://developer.chrome.com"
];

socket.on('connection', (client, request) => {
  const idNum = parseInt(parse(request.url, true).query.id);
  if (!idNum || idNum < 1 || idNum > 6) return client.close();

  const id = 'web' + idNum;
  if (clients.find(c => c.id === id)) return client.close();

  client.id = id;
  client.idNum = idNum;
  clients.push(client);
  console.log(`${id} 접속`);

  // 초기 URL 지정
  const sorted = [...clients].sort((a, b) => a.idNum - b.idNum);
  const i = sorted.findIndex(c => c.id === id);
  const initUrl = fallbackUrls[i % fallbackUrls.length];
  clientUrls[id] = initUrl;

  // ✅ 최초 접속자에겐 슬라이드 없는 init 전송
  client.send(`init:${initUrl}`);

  client.on('message', (msg) => {
    msg = msg.toString();
    if (msg.startsWith('url:')) {
      clientUrls[client.id] = msg.slice(4);
    }
  });

  client.on('close', () => {
    clients = clients.filter(c => c.id !== id);
    delete clientUrls[id];
    console.log(`${id} 종료`);
  });
});

setInterval(() => {
  const sorted = [...clients].sort((a, b) => a.idNum - b.idNum);
  const len = sorted.length;
  if (len < 2) return;

  for (let i = 0; i < len; i++) {
    const cur = sorted[i];
    const next = sorted[(i + 1) % len];
    const fromUrl = clientUrls[cur.id] || fallbackUrls[i % fallbackUrls.length];
    const toUrl = clientUrls[next.id] || fallbackUrls[(i + 1) % fallbackUrls.length];

    if (cur.readyState === websocket.OPEN) {
      cur.send(`switch:${fromUrl}:${toUrl}`);
    }
  }
}, 10000);
