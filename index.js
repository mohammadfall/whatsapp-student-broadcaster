const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const { GoogleSpreadsheet } = require('google-spreadsheet');
require('dotenv').config();
const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// عرض صورة QR عبر /qr
app.get('/qr', (req, res) => {
  const qrPath = path.join(__dirname, 'qr.png');
  res.sendFile(qrPath);
});

app.listen(PORT, () => {
  console.log(`🚀 Express server running on port ${PORT}`);
});

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  },
});

client.on('qr', async (qr) => {
  try {
    await qrcode.toFile('qr.png', qr);
    console.log('📸 QR code saved to qr.png - افتح /qr في المتصفح');
  } catch (err) {
    console.error('❌ Failed to generate QR code image', err);
  }
});

client.on('ready', async () => {
  console.log('✅ WhatsApp Bot is ready!');

  async function checkAndSendMessages() {
    const doc = new GoogleSpreadsheet(process.env.GOOGLE_SHEET_ID);

    await doc.useServiceAccountAuth({
      client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
      private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\n/g, '
'),
    });

    await doc.loadInfo();
    const sheet = doc.sheetsByIndex[0];
    const rows = await sheet.getRows();

    for (let row of rows) {
      if (row.Status !== '✅') {
        const number = row.Phone.replace(/[^0-9+]/g, '');
        const message = row.Message;
        try {
          await client.sendMessage(`${number}@c.us`, message);
          console.log(`✅ Sent to ${number}`);
          row.Status = '✅';
          await row.save();
        } catch (err) {
          console.error(`❌ Failed for ${number}`, err);
        }
      }
    }
  }

  await checkAndSendMessages();
  setInterval(checkAndSendMessages, 7 * 60 * 1000);
});

client.initialize();
